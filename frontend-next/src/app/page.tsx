import Link from "next/link";

export default function Home() {
  return (
    <main className="p-6 space-y-4">
      <h1 className="text-2xl font-semibold">Altassian</h1>
      <div className="space-x-3">
        <Link className="underline" href="/login">Login</Link>
        <Link className="underline" href="/register">Register</Link>
        <Link className="underline" href="/spaces">Spaces</Link>
      </div>
    </main>
  );
}
