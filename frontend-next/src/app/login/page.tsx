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
    <main className="p-6 max-w-sm mx-auto space-y-4">
      <h1 className="text-xl font-semibold">Login</h1>
      {error && <p className="text-red-600 text-sm">{error}</p>}
      <form className="space-y-3" onSubmit={onSubmit}>
        <input className="w-full border p-2 rounded" placeholder="Username" value={username} onChange={e=>setUsername(e.target.value)} />
        <input className="w-full border p-2 rounded" type="password" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)} />
        <button className="bg-black text-white px-4 py-2 rounded" type="submit">Sign in</button>
      </form>
    </main>
  );
}
