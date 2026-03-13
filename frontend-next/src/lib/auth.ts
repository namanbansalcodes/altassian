export type Tokens = {
  access: string;
  refresh: string;
};

export type JwtPayload = {
  exp?: number;
  iat?: number;
  [key: string]: any;
};

export function parseJwt(token: string): JwtPayload | null {
  try {
    const [, payload] = token.split(".");
    const json = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
    return JSON.parse(json);
  } catch {
    return null;
  }
}

export function msUntilExpiry(token?: string): number | null {
  if (!token) return null;
  const p = parseJwt(token);
  if (!p?.exp) return null;
  const now = Date.now() / 1000;
  return Math.max(0, (p.exp - now) * 1000);
}
