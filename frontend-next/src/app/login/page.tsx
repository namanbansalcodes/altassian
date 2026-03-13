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
        <input className="w-full border p-3 rounded text-base" placeholder="Username" value={username} onChange={e=>setUsername(e.target.value)} />
        <input className="w-full border p-3 rounded text-base" type="password" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)} />
        <button className="bg-black text-white px-4 py-3 rounded w-full sm:w-auto font-medium" type="submit">Sign in</button>
      </form>
    </main>
  );
}
