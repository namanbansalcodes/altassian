import {requireUser} from "@/lib/auth";
import {ssrApi} from "@/lib/api";
import {cookies} from "next/headers";
import {Chrome} from "@/components/Chrome";

export default async function AuthedLayout({children}: {children: React.ReactNode}) {
  const user = await requireUser();
  const cookieHeader = (await cookies()).toString();
  const spaces = await ssrApi.listSpaces(cookieHeader).catch(() => ({results: []}));
  return <Chrome user={user} spaces={spaces.results}>{children}</Chrome>;
}
