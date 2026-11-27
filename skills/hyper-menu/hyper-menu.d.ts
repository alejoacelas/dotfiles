export interface HyperMenuItem {
  /** The single key that runs it inside the menu; lowercase. */
  key: string;
  label: string;
  /** Label of the shortcut that runs it with the menu closed, such as "M-Z" or "⌘K". */
  outside?: string;
  run: () => void;
  /** Dimmed and not runnable when this returns false. */
  enabled?: () => boolean;
}
export interface HyperMenuGroup {
  title: string;
  items: HyperMenuItem[];
}
export interface HyperMenu {
  open(): void;
  close(): void;
  toggle(): void;
  isOpen(): boolean;
  destroy(): void;
}
export function createHyperMenu(options: {
  /** A function is read again each time the menu draws. */
  groups: HyperMenuGroup[] | (() => HyperMenuGroup[]);
  /** Open on a lone tap of Hyper (default true). */
  hyperTap?: boolean;
  onRun?: (item: HyperMenuItem) => void;
  /** Attributes for the menu's element, for the host app's styling or tests. */
  attributes?: Record<string, string>;
}): HyperMenu;
export function onHyperTap(onTap: () => void, target?: Window): () => void;
