"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    const res = await fetch("/api/auth", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password }),
    });

    if (res.ok) {
      router.push("/");
      router.refresh();
    } else {
      setError("Incorrect password / パスワードが違います");
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-paper">
      <div className="text-center animate-fade-up">
        <h1 className="font-serif text-4xl font-light tracking-tight text-ink mb-2">
          Scout
        </h1>
        <p className="text-xs text-muted font-light mb-10">
          Asago to the Moon
        </p>

        <form onSubmit={handleSubmit} className="w-72 mx-auto">
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password / パスワード"
            className="w-full px-4 py-3 text-sm font-light border border-border rounded-lg bg-white focus:outline-none focus:border-calm transition-colors text-center"
            autoFocus
          />
          {error && (
            <p className="text-xs text-accent mt-2 font-light">{error}</p>
          )}
          <button
            type="submit"
            disabled={loading}
            className="mt-4 w-full px-5 py-3 text-sm bg-ink text-paper rounded-lg hover:bg-ink/80 transition-colors font-light disabled:opacity-50"
          >
            {loading ? "..." : "Enter / 入る"}
          </button>
        </form>

        <p className="text-[10px] text-muted font-light mt-12">
          Project Asago-to-the-Moon
        </p>
      </div>
    </div>
  );
}
