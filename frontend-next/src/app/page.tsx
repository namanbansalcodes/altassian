import {redirect} from "next/navigation";
import {maybeUser} from "@/lib/auth";

export default async function RootPage() {
  const user = await maybeUser();
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  redirect((user ? "/home" : "/login") as any);
}
