/**
 * Client structured logger — modular, env-gated, no secrets in output.
 * Enable with NEXT_PUBLIC_LOG_LEVEL=debug|info|warn|error (default: warn in prod, info in dev).
 */

export type LogLevel = "debug" | "info" | "warn" | "error";

const LEVEL_ORDER: Record<LogLevel, number> = {
  debug: 10,
  info: 20,
  warn: 30,
  error: 40,
};

const SENSITIVE_KEY = /^(authorization|x-api-key|cookie|password|token|secret|api[_-]?key)$/i;

function resolveMinLevel(): LogLevel {
  const raw = (process.env.NEXT_PUBLIC_LOG_LEVEL || "").toLowerCase();
  if (raw === "debug" || raw === "info" || raw === "warn" || raw === "error") {
    return raw;
  }
  return process.env.NODE_ENV === "production" ? "warn" : "info";
}

function shouldLog(level: LogLevel): boolean {
  return LEVEL_ORDER[level] >= LEVEL_ORDER[resolveMinLevel()];
}

/** Shallow redact of common secret field names. */
export function redactFields(
  fields?: Record<string, unknown>,
): Record<string, unknown> | undefined {
  if (!fields) return undefined;
  const out: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(fields)) {
    out[k] = SENSITIVE_KEY.test(k) ? "[redacted]" : v;
  }
  return out;
}

type LogFields = Record<string, unknown>;

function emit(level: LogLevel, scope: string, msg: string, fields?: LogFields): void {
  if (!shouldLog(level)) return;
  const payload = {
    ts: new Date().toISOString(),
    level,
    scope,
    msg,
    ...redactFields(fields),
  };
  const line = JSON.stringify(payload);
  if (level === "error") console.error(line);
  else if (level === "warn") console.warn(line);
  else console.log(line);
}

export type ScopedLogger = {
  debug: (msg: string, fields?: LogFields) => void;
  info: (msg: string, fields?: LogFields) => void;
  warn: (msg: string, fields?: LogFields) => void;
  error: (msg: string, fields?: LogFields) => void;
  child: (subScope: string) => ScopedLogger;
};

/** Create a scoped logger, e.g. `createLogger("api")`. */
export function createLogger(scope: string): ScopedLogger {
  return {
    debug: (msg, fields) => emit("debug", scope, msg, fields),
    info: (msg, fields) => emit("info", scope, msg, fields),
    warn: (msg, fields) => emit("warn", scope, msg, fields),
    error: (msg, fields) => emit("error", scope, msg, fields),
    child: (sub) => createLogger(`${scope}.${sub}`),
  };
}

export const rootLogger = createLogger("ouroboros");
