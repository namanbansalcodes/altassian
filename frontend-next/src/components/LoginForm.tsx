"use client";

import {useState} from "react";
import {useRouter} from "next/navigation";
import {Mail, KeyRound, ArrowLeft} from "lucide-react";
import {api, HTTPError} from "@/lib/api";

type Step = "email" | "code";

export function LoginForm() {
  const router = useRouter();
  const [step, setStep] = useState<Step>("email");
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function requestCode(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      await api.requestOtp(email);
      setStep("code");
    } catch (err) {
      setError(await readError(err, "Couldn't send code."));
    } finally {
      setBusy(false);
    }
  }

  async function verifyCode(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      await api.verifyOtp(email, code, displayName.trim() || undefined);
      router.push("/home");
      router.refresh();
    } catch (err) {
      setError(await readError(err, "Invalid or expired code."));
    } finally {
      setBusy(false);
    }
  }

  if (step === "email") {
    return (
      <form onSubmit={requestCode} className="flex w-full max-w-sm flex-col gap-3">
        <label className="flex flex-col gap-1">
          <span className="text-sm font-medium text-zinc-700">Email</span>
          <div className="relative">
            <Mail className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-zinc-400" size={16} />
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoFocus
              placeholder="you@example.com"
              className="w-full rounded-md border border-zinc-300 bg-white py-2 pl-9 pr-3 text-sm focus:border-zinc-900 focus:outline-none"
            />
          </div>
        </label>
        {error && (
          <p className="rounded-md bg-rose-50 px-3 py-2 text-sm text-rose-700" role="alert">
            {error}
          </p>
        )}
        <button
          type="submit"
          disabled={busy || !email}
          className="mt-2 rounded-md bg-zinc-900 px-3 py-2 text-sm font-medium text-white hover:bg-zinc-700 disabled:opacity-50"
        >
          {busy ? "Sending…" : "Send sign-in code"}
        </button>
        <p className="mt-1 text-xs text-zinc-500">
          We&apos;ll email a 6-digit code. New here? An account is created on first verify.
        </p>
      </form>
    );
  }

  return (
    <form onSubmit={verifyCode} className="flex w-full max-w-sm flex-col gap-3">
      <button
        type="button"
        onClick={() => { setStep("email"); setCode(""); setError(null); }}
        className="flex items-center gap-1 self-start text-xs text-zinc-500 hover:text-zinc-900"
      >
        <ArrowLeft size={12} /> change email
      </button>
      <p className="text-sm text-zinc-700">
        Enter the 6-digit code we just emailed to <span className="font-medium text-zinc-900">{email}</span>.
      </p>
      <label className="flex flex-col gap-1">
        <span className="text-sm font-medium text-zinc-700">Code</span>
        <div className="relative">
          <KeyRound className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-zinc-400" size={16} />
          <input
            inputMode="numeric"
            pattern="[0-9]{6}"
            maxLength={6}
            value={code}
            onChange={(e) => setCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
            required
            autoFocus
            placeholder="123456"
            className="w-full rounded-md border border-zinc-300 bg-white py-2 pl-9 pr-3 font-mono text-base tracking-[0.4em] focus:border-zinc-900 focus:outline-none"
          />
        </div>
      </label>
      <label className="flex flex-col gap-1">
        <span className="text-sm font-medium text-zinc-700">
          Display name <span className="text-zinc-400">(optional, first time only)</span>
        </span>
        <input
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
          maxLength={120}
          placeholder="What should we call you?"
          className="rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm focus:border-zinc-900 focus:outline-none"
        />
      </label>
      {error && (
        <p className="rounded-md bg-rose-50 px-3 py-2 text-sm text-rose-700" role="alert">
          {error}
        </p>
      )}
      <button
        type="submit"
        disabled={busy || code.length !== 6}
        className="mt-2 rounded-md bg-zinc-900 px-3 py-2 text-sm font-medium text-white hover:bg-zinc-700 disabled:opacity-50"
      >
        {busy ? "Verifying…" : "Verify and continue"}
      </button>
    </form>
  );
}

async function readError(err: unknown, fallback: string): Promise<string> {
  if (err instanceof HTTPError) {
    const body = await err.response.json().catch(() => null);
    return (body as {detail?: string})?.detail ?? fallback;
  }
  return fallback;
}
