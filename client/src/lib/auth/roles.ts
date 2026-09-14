/** Clerk role helpers — mirror server `auth/roles.py` claim path. */

export type AppRole = "viewer" | "analyst" | "admin" | "ops";

const ROLE_ORDER: Record<AppRole, number> = {
  viewer: 1,
  analyst: 2,
  admin: 3,
  ops: 4,
};

export function parseRole(value: unknown, fallback: AppRole = "viewer"): AppRole {
  if (typeof value === "string" && value in ROLE_ORDER) {
    return value as AppRole;
  }
  return fallback;
}

export function roleAtLeast(have: AppRole, need: AppRole): boolean {
  return ROLE_ORDER[have] >= ROLE_ORDER[need];
}

/** Matches server: public_metadata.role, else top-level role, else viewer. */
export function roleFromMetadata(
  publicMetadata: Record<string, unknown> | null | undefined,
  unsafeMetadata?: Record<string, unknown> | null,
): AppRole {
  const fromPublic = publicMetadata?.role;
  if (fromPublic != null) return parseRole(fromPublic);
  const fromUnsafe = unsafeMetadata?.role;
  if (fromUnsafe != null) return parseRole(fromUnsafe);
  return "viewer";
}
