import {cookies} from "next/headers";
import {redirect} from "next/navigation";
import type {User} from "./types";
import {ssrApi} from "./api";

/** Get current user during SSR. Redirects to /login on 401. */
export async function requireUser(): Promise<User> {
  const cookieHeader = (await cookies()).toString();
  try {
    return await ssrApi.me(cookieHeader);
  } catch {
    redirect("/login");
  }
}

/** Try to get user; returns null instead of redirecting. */
export async function maybeUser(): Promise<User | null> {
  const cookieHeader = (await cookies()).toString();
  try {
    return await ssrApi.me(cookieHeader);
  } catch {
    return null;
  }
}
