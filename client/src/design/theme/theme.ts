export type ThemeMode = "dark" | "light";
export type ThemePreference = ThemeMode | "system";

/** @deprecated Prefer ThemeMode / ThemePreference — kept for call sites. */
export type AppTheme = ThemeMode;

export const THEME_STORAGE_KEY = "ouroboros-theme";

export function isThemeMode(value: unknown): value is ThemeMode {
  return value === "dark" || value === "light";
}

export function isThemePreference(value: unknown): value is ThemePreference {
  return value === "dark" || value === "light" || value === "system";
}

export function isAppTheme(value: unknown): value is ThemeMode {
  return isThemeMode(value);
}

export function readSystemTheme(): ThemeMode {
  if (typeof window === "undefined") return "dark";
  return window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
}

/** Resolve preference → concrete data-theme mode. */
export function resolveThemeMode(preference: ThemePreference): ThemeMode {
  return preference === "system" ? readSystemTheme() : preference;
}

/** Apply resolved mode to <html> — keeps data-theme + .dark/.light in sync. */
export function applyTheme(mode: ThemeMode): void {
  const root = document.documentElement;
  root.setAttribute("data-theme", mode);
  root.classList.remove("dark", "light");
  root.classList.add(mode);
}

/** Apply preference: resolve system if needed, then write DOM. */
export function applyThemePreference(preference: ThemePreference): ThemeMode {
  const mode = resolveThemeMode(preference);
  applyTheme(mode);
  return mode;
}

export function readStoredTheme(): ThemePreference | null {
  try {
    const raw = localStorage.getItem(THEME_STORAGE_KEY);
    return isThemePreference(raw) ? raw : null;
  } catch {
    return null;
  }
}

export function persistTheme(preference: ThemePreference): void {
  try {
    localStorage.setItem(THEME_STORAGE_KEY, preference);
  } catch {
    /* ignore quota / private mode */
  }
}

export function resolveInitialTheme(): ThemePreference {
  return readStoredTheme() ?? "dark";
}
