export interface HyperMenuItem {
  /** The single key that runs it inside the menu; lowercase, and the letter `outside` ends in. */
  key: string;
  label: string;
  /** The shortcut that runs it with the menu closed, such as ";-Z" or "⌘K"; shown on the row. */
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
