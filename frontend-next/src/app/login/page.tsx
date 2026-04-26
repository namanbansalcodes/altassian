import Link from "next/link";
import {LoginForm} from "@/components/LoginForm";

export default function LoginPage() {
  return (
    <main className="flex min-h-screen items-center justify-center px-4">
      <div className="flex w-full max-w-sm flex-col items-center gap-6">
        <Link href="/" className="text-2xl font-semibold tracking-tight">
          Altassian
        </Link>
        <LoginForm />
        <p className="text-xs text-zinc-500">Invite-only. Ask an admin for access.</p>
      </div>
    </main>
  );
}
