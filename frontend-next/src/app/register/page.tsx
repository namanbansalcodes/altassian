"use client";
import { useState } from "react";
import ky from "ky";
import { useRouter } from "next/navigation";

export default function RegisterPage() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await ky.post("/api/users/", { json: { username, email, password } });
      router.push("/login");
    } catch (e) {
      setError("Registration failed");
    }
  }

  return (
    <main className="p-4 sm:p-6 max-w-sm mx-auto space-y-4">
      <h1 className="text-lg sm:text-xl font-semibold">Register</h1>
      {error && <p className="text-red-600 text-sm">{error}</p>}
      <form className="space-y-4" onSubmit={onSubmit}>
        <input className="w-full border p-3 rounded text-base" placeholder="Username" value={username} onChange={e=>setUsername(e.target.value)} />
        <input className="w-full border p-3 rounded text-base" placeholder="Email" type="email" value={email} onChange={e=>setEmail(e.target.value)} />
        <input className="w-full border p-3 rounded text-base" type="password" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)} />
        <button className="bg-black text-white px-4 py-3 rounded w-full sm:w-auto font-medium" type="submit">Create account</button>
      </form>
    </main>
  );
}
