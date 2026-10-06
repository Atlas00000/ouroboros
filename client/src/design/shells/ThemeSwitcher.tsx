"use client";

import { Monitor, Moon, Sun } from "lucide-react";
import {
  useCallback,
  useEffect,
  useId,
  useRef,
  useState,
  type KeyboardEvent,
} from "react";
import type { LucideIcon } from "lucide-react";

import { Button } from "@/design/primitives/Button";
import { Icon } from "@/design/primitives/Icon";
import {
  applyThemePreference,
  persistTheme,
  resolveInitialTheme,
  type ThemePreference,
} from "@/design/theme/theme";
import { cn } from "@/lib/utils";

import "./theme-switcher.css";

const OPTIONS: {
  value: ThemePreference;
  icon: LucideIcon;
  label: string;
}[] = [
  { value: "dark", icon: Moon, label: "Dark" },
  { value: "light", icon: Sun, label: "Light" },
  { value: "system", icon: Monitor, label: "System" },
];

function iconFor(preference: ThemePreference): LucideIcon {
  return OPTIONS.find((o) => o.value === preference)?.icon ?? Moon;
}

export function ThemeSwitcher() {
  const [preference, setPreference] = useState<ThemePreference>("dark");
  const [ready, setReady] = useState(false);
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);
  const menuId = useId();

  const select = useCallback((next: ThemePreference) => {
    applyThemePreference(next);
    persistTheme(next);
    setPreference(next);
    setOpen(false);
  }, []);

  useEffect(() => {
    const initial = resolveInitialTheme();
    // Match DOM to preference (boot script usually already did this before paint).
    applyThemePreference(initial);
    setPreference(initial);
    setReady(true);
  }, []);

  useEffect(() => {
    if (preference !== "system") return;
    const mq = window.matchMedia("(prefers-color-scheme: light)");
    const onChange = () => applyThemePreference("system");
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, [preference]);

  useEffect(() => {
    if (!open) return;
    const onPointer = (e: MouseEvent) => {
      if (!rootRef.current?.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: globalThis.KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("mousedown", onPointer);
    window.addEventListener("keydown", onKey);
    return () => {
      window.removeEventListener("mousedown", onPointer);
      window.removeEventListener("keydown", onKey);
    };
  }, [open]);

  function onMenuKeyDown(e: KeyboardEvent<HTMLDivElement>) {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      const buttons = rootRef.current?.querySelectorAll<HTMLButtonElement>(
        "[data-theme-option]",
      );
      if (!buttons?.length) return;
      const i = [...buttons].indexOf(document.activeElement as HTMLButtonElement);
      buttons[(i + 1) % buttons.length]?.focus();
    }
    if (e.key === "ArrowUp") {
      e.preventDefault();
      const buttons = rootRef.current?.querySelectorAll<HTMLButtonElement>(
        "[data-theme-option]",
      );
      if (!buttons?.length) return;
      const i = [...buttons].indexOf(document.activeElement as HTMLButtonElement);
      buttons[(i - 1 + buttons.length) % buttons.length]?.focus();
    }
  }

  const triggerLabel = `Theme: ${OPTIONS.find((o) => o.value === preference)?.label ?? "Dark"}`;

  return (
    <div className="ds-theme-switcher" ref={rootRef}>
      <Button
        type="button"
        variant="ghost"
        size="sm"
        className="h-9 w-9 px-0"
        onClick={() => setOpen((v) => !v)}
        aria-label={triggerLabel}
        title={triggerLabel}
        aria-haspopup="menu"
        aria-expanded={open}
        aria-controls={menuId}
        disabled={!ready}
      >
        <Icon icon={iconFor(preference)} size="md" />
      </Button>

      {open ? (
        <div
          id={menuId}
          className="ds-theme-switcher__menu"
          role="menu"
          aria-label="Theme"
          onKeyDown={onMenuKeyDown}
        >
          {OPTIONS.map((opt) => {
            const active = preference === opt.value;
            return (
              <button
                key={opt.value}
                type="button"
                role="menuitemradio"
                aria-checked={active}
                data-theme-option={opt.value}
                data-active={active ? "true" : undefined}
                className={cn("ds-theme-switcher__option", active && "is-active")}
                title={opt.label}
                aria-label={opt.label}
                onClick={() => select(opt.value)}
              >
                <Icon icon={opt.icon} size="md" />
              </button>
            );
          })}
        </div>
      ) : null}
    </div>
  );
}
