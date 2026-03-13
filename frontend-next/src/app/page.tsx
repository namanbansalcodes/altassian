import Link from "next/link";

export default function Home() {
  return (
    <main className="p-4 sm:p-6 space-y-4">
      <h1 className="text-xl sm:text-2xl font-semibold">Altassian</h1>
      <div className="flex flex-wrap gap-3">
        <Link className="underline" href="/login">Login</Link>
        <Link className="underline" href="/register">Register</Link>
        <Link className="underline" href="/spaces">Spaces</Link>
      </div>
    </main>
  );
}
