#!/usr/bin/env python3
"""Fetch Granola meeting metadata and verbatim transcript chunks via its app API."""

from __future__ import annotations

import argparse
import json
import os
import plistlib
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, time
from pathlib import Path
from typing import Any

API = "https://api.granola.ai"
DEFAULT_PLATFORM = "darwin" if sys.platform == "darwin" else sys.platform


class ApiError(RuntimeError):
    pass


def installed_version() -> str | None:
    info = Path("/Applications/Granola.app/Contents/Info.plist")
    try:
        data = plistlib.loads(info.read_bytes())
        value = data.get("CFBundleShortVersionString")
        return value if isinstance(value, str) and value else None
    except (OSError, plistlib.InvalidFileException):
        return None


def request(endpoint: str, payload: dict[str, Any], args: argparse.Namespace) -> Any:
    token = os.environ.get("GRANOLA_ACCESS_TOKEN")
    if not token:
        raise ApiError(
            "GRANOLA_ACCESS_TOKEN is not set; inject a current bearer token with "
            "the repository's secret manager"
        )
    version = (
        args.client_version
        or os.environ.get("GRANOLA_CLIENT_VERSION")
        or installed_version()
    )
    if not version:
        raise ApiError(
            "Granola client version is unknown; set GRANOLA_CLIENT_VERSION or pass "
            "--client-version"
        )
    body = json.dumps(payload, separators=(",", ":")).encode()
    req = urllib.request.Request(
        f"{API}{endpoint}",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Client-Version": version,
            "X-Granola-Platform": args.platform,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as response:
            raw = response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        if exc.code in (401, 403):
            raise ApiError(
                f"Granola authentication failed ({exc.code}); refresh the injected token"
            ) from None
        raise ApiError(f"Granola API returned HTTP {exc.code}: {detail}") from None
    except urllib.error.URLError as exc:
        raise ApiError(f"Granola API request failed: {exc.reason}") from None
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ApiError(f"Granola API returned invalid JSON: {exc}") from None


def documents_from_response(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict):
        for key in ("documents", "results", "data"):
            candidate = value.get(key)
            if isinstance(candidate, list):
                return [item for item in candidate if isinstance(item, dict)]
    raise ApiError("unexpected get-documents response shape")


def chunks_from_response(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict):
        for key in ("transcript", "chunks", "data"):
            candidate = value.get(key)
            if isinstance(candidate, list):
                return [item for item in candidate if isinstance(item, dict)]
    raise ApiError("unexpected get-document-transcript response shape")


def parse_day(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"expected YYYY-MM-DD, got {value!r}"
        ) from None


def document_time(document: dict[str, Any]) -> datetime | None:
    calendar_event = document.get("google_calendar_event")
    candidates = [
        document.get("created_at"),
        document.get("start_time"),
        calendar_event.get("start_time") if isinstance(calendar_event, dict) else None,
    ]
    for value in candidates:
        if not isinstance(value, str):
            continue
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone()
        except ValueError:
            pass
    return None


def filter_documents(
    documents: list[dict[str, Any]], start: date | None, end: date | None
) -> list[dict[str, Any]]:
    if not start and not end:
        return documents
    lower = datetime.combine(start, time.min).astimezone() if start else None
    upper = datetime.combine(end, time.max).astimezone() if end else None
    result = []
    for document in documents:
        when = document_time(document)
        if when is None:
            continue
        if lower and when < lower:
            continue
        if upper and when > upper:
            continue
        result.append(document)
    return result


def speaker(chunk: dict[str, Any]) -> str:
    if chunk.get("source") == "microphone":
        return "Me"
    detected = chunk.get("detectedSpeaker") or chunk.get("detected_speaker")
    if isinstance(detected, dict):
        name = detected.get("participantName") or detected.get("participant_name")
        if isinstance(name, str) and name.strip():
            return name.strip()
    return "Them"


def chunk_text(chunk: dict[str, Any]) -> str:
    value = chunk.get("text")
    if isinstance(value, str):
        return value.strip()
    words = chunk.get("words")
    if isinstance(words, list):
        return " ".join(
            str(word.get("text", "")).strip()
            if isinstance(word, dict)
            else str(word).strip()
            for word in words
        ).strip()
    return ""


def render_turns(chunks: list[dict[str, Any]]) -> str:
    turns: list[tuple[str, list[str]]] = []
    for chunk in chunks:
        text = chunk_text(chunk)
        if not text:
            continue
        who = speaker(chunk)
        if turns and turns[-1][0] == who:
            turns[-1][1].append(text)
        else:
            turns.append((who, [text]))
    if not turns:
        raise ApiError("transcript contains no text chunks")
    return "\n\n".join(f"{who}: {' '.join(parts)}" for who, parts in turns) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--client-version", help="Granola app version (auto-detected on macOS)"
    )
    parser.add_argument("--platform", default=DEFAULT_PLATFORM, help="X-Granola-Platform value")
    parser.add_argument("--timeout", type=float, default=30, help="HTTP timeout in seconds")
    commands = parser.add_subparsers(dest="command", required=True)

    meetings = commands.add_parser("meetings", help="list meeting metadata")
    meetings.add_argument("--from", dest="from_day", type=parse_day)
    meetings.add_argument("--to", dest="to_day", type=parse_day)

    transcript = commands.add_parser("transcript", help="fetch one verbatim transcript")
    transcript.add_argument("document_id")
    transcript.add_argument("--format", choices=("json", "text"), default="text")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "meetings":
            response = request("/v2/get-documents", {}, args)
            documents = filter_documents(
                documents_from_response(response), args.from_day, args.to_day
            )
            print(json.dumps(documents, ensure_ascii=False, indent=2))
        else:
            response = request(
                "/v1/get-document-transcript", {"document_id": args.document_id}, args
            )
            chunks = chunks_from_response(response)
            if args.format == "json":
                print(json.dumps(chunks, ensure_ascii=False, indent=2))
            else:
                sys.stdout.write(render_turns(chunks))
        return 0
    except ApiError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
