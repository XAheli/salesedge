import { useEffect } from "react";
import { useAppStore } from "@/stores/useAppStore";

export const COMMAND_PALETTE_EVENT = "salesedge:open-command-palette";
export const GLOBAL_ESCAPE_EVENT = "salesedge:global-escape";

export interface UseKeyboardShortcutsOptions {
  enabled?: boolean;
  /** If provided, called in addition to dispatching COMMAND_PALETTE_EVENT */
  onCommandPalette?: () => void;
  onToggleSidebar?: () => void;
  onEscape?: () => void;
}

function isEditableTarget(target: EventTarget | null): boolean {
  if (!target || !(target instanceof HTMLElement)) {
    return false;
  }
  const tag = target.tagName;
  if (tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") {
    return true;
  }
  if (target.isContentEditable) {
    return true;
  }
  return false;
}

export function useKeyboardShortcuts(options: UseKeyboardShortcutsOptions = {}): void {
  const { enabled = true, onCommandPalette, onToggleSidebar, onEscape } = options;
  const toggleSidebarStore = useAppStore((s) => s.toggleSidebar);

  useEffect(() => {
    if (!enabled) {
      return;
    }

    const onKeyDown = (e: KeyboardEvent) => {
      const mod = e.metaKey || e.ctrlKey;

      if (mod && e.key.toLowerCase() === "k") {
        e.preventDefault();
        onCommandPalette?.();
        window.dispatchEvent(new CustomEvent(COMMAND_PALETTE_EVENT));
        return;
      }

      if (mod && e.key === "/") {
        e.preventDefault();
        if (onToggleSidebar) {
          onToggleSidebar();
        } else {
          toggleSidebarStore();
        }
        return;
      }

      if (e.key === "Escape") {
        if (isEditableTarget(e.target)) {
          return;
        }
        onEscape?.();
        window.dispatchEvent(new CustomEvent(GLOBAL_ESCAPE_EVENT));
      }
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [enabled, onCommandPalette, onToggleSidebar, onEscape, toggleSidebarStore]);
}
