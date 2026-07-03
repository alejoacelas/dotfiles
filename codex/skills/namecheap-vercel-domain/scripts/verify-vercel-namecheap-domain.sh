#!/usr/bin/env bash
set -u

domain="${1:-}"
if [[ -z "$domain" || "$domain" == "-h" || "$domain" == "--help" ]]; then
  cat <<'USAGE'
Usage: verify-vercel-namecheap-domain.sh <domain>

Checks authoritative DNS, Vercel domain verification, and HTTP/HTTPS reachability
for an apex domain plus its www host.
USAGE
  exit 2
fi

www_domain="www.${domain}"

run() {
  printf '\n== %s ==\n' "$*"
  "$@"
  status=$?
  if [[ $status -ne 0 ]]; then
    printf '(exit %s)\n' "$status"
  fi
  return 0
}

need() {
  if ! command -v "$1" >/dev/null 2>&1; then
    printf 'Missing required command: %s\n' "$1" >&2
    return 1
  fi
}

need dig || exit 1
need curl || exit 1

printf 'Domain: %s\n' "$domain"

printf '\n== Public nameservers ==\n'
nameservers=()
while IFS= read -r ns; do
  [[ -n "$ns" ]] && nameservers+=("$ns")
done < <(dig +short NS "$domain" | sed 's/\.$//' | sort)
if [[ ${#nameservers[@]} -eq 0 ]]; then
  printf 'No NS records found for %s\n' "$domain"
else
  printf '%s\n' "${nameservers[@]}"
fi

if [[ ${#nameservers[@]} -gt 0 ]]; then
  for ns in "${nameservers[@]}"; do
    run dig +short "@${ns}" "$domain" A
    run dig +short "@${ns}" "$www_domain" CNAME
    run dig +short "@${ns}" "$www_domain" A
  done
fi

printf '\n== Recursive DNS ==\n'
run dig +short "$domain" A
run dig +short "$www_domain" CNAME
run dig +short "$www_domain" A

printf '\n== Vercel verification ==\n'
if command -v npx >/dev/null 2>&1; then
  run npx --yes vercel@latest domains verify "$domain"
  run npx --yes vercel@latest domains verify "$www_domain"
else
  printf 'Skipping Vercel verification: npx is not installed.\n'
fi

printf '\n== HTTP checks ==\n'
run curl -I --max-time 15 "http://${domain}"
run curl -I --max-time 15 "http://${www_domain}"
run curl -I --max-time 15 "https://${domain}"
run curl -I --max-time 15 "https://${www_domain}"
