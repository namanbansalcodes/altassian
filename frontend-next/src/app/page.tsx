import {redirect} from "next/navigation";
import {maybeUser} from "@/lib/auth";

export default async function RootPage() {
  const user = await maybeUser();
  redirect(user ? "/home" : "/login");
}
