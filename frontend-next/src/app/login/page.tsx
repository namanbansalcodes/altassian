"use client";
import { useState, useEffect } from "react";
import ky from "ky";
import { useSetAtom } from "jotai";
import { startEagerRefreshAtom, tokensAtom } from "@/atoms/auth";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const setTokens = useSetAtom(tokensAtom);
  const startLoop = useSetAtom(startEagerRefreshAtom);
  const router = useRouter();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      const data = await ky
        .post("/api/auth/login/", { json: { username, password } })
        .json<{ access: string; refresh: string }>();
      setTokens(data);
      startLoop();
      router.push("/");
    } catch (e: any) {
      setError("Login failed");
    }
  }

  return (
    <main className="p-4 sm:p-6 max-w-sm mx-auto space-y-4">
      <h1 className="text-lg sm:text-xl font-semibold">Login</h1>
      {error && <p className="text-red-600 text-sm">{error}</p>}
      <form className="space-y-4" onSubmit={onSubmit}>
        <input className="w-full border border-neutral-300 dark:border-neutral-600 p-3 rounded-lg text-base bg-white dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100 placeholder-neutral-400 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none min-h-[44px]" placeholder="Username" value={username} onChange={e=>setUsername(e.target.value)} />
        <input className="w-full border border-neutral-300 dark:border-neutral-600 p-3 rounded-lg text-base bg-white dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100 placeholder-neutral-400 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none min-h-[44px]" type="password" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)} />
        <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-3 rounded-lg w-full font-medium disabled:opacity-50 min-h-[44px]" type="submit">Sign in</button>
      </form>
    </main>
  );
}
