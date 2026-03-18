"use client";

import Link from "next/link";
import { useState } from "react";

const NAV_ITEMS = [
  { href: "/", label: "Dashboard", labelJp: "ダッシュボード" },
  { href: "/jobs", label: "Leads", labelJp: "求人" },
  { href: "/tracker", label: "Pipeline", labelJp: "進捗" },
  { href: "/orgs", label: "Organizations", labelJp: "企業" },
  { href: "/stories", label: "Stories", labelJp: "ストーリー" },
  { href: "/hype", label: "North Star", labelJp: "応援" },
];

export default function Shell({ children }: { children: React.ReactNode }) {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <div className="min-h-screen flex flex-col md:flex-row">
      {/* Mobile header */}
      <div className="md:hidden flex items-center justify-between px-4 py-3 border-b border-border bg-paper-warm/50">
        <div>
          <h1 className="font-serif text-xl font-light tracking-tight text-ink">Scout</h1>
          <p className="text-[10px] text-muted font-light">Asago to the Moon</p>
        </div>
        <button
          onClick={() => setMenuOpen(!menuOpen)}
          className="p-2 text-ink/70 hover:text-ink transition-colors"
          aria-label="Toggle menu"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            {menuOpen ? (
              <path d="M6 6l12 12M6 18L18 6" />
            ) : (
              <path d="M4 8h16M4 16h16" />
            )}
          </svg>
        </button>
      </div>

      {/* Mobile nav dropdown */}
      {menuOpen && (
        <nav className="md:hidden bg-paper-warm/50 border-b border-border px-4 py-2">
          {NAV_ITEMS.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => setMenuOpen(false)}
              className="flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-light text-ink/80 hover:bg-paper-warm hover:text-ink transition-colors"
            >
              <span>{item.label}</span>
              <span className="text-[10px] text-muted">{item.labelJp}</span>
            </Link>
          ))}
        </nav>
      )}

      {/* Desktop sidebar */}
      <nav className="hidden md:flex w-52 shrink-0 border-r border-border bg-paper-warm/50 p-6 flex-col gap-1">
        <div className="mb-8">
          <h1 className="font-serif text-2xl font-light tracking-tight text-ink">Scout</h1>
          <p className="text-xs text-muted mt-1 font-light">Asago to the Moon</p>
        </div>
        {NAV_ITEMS.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className="flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-light text-ink/80 hover:bg-paper-warm hover:text-ink transition-colors"
          >
            <span>{item.label}</span>
            <span className="text-[10px] text-muted">{item.labelJp}</span>
          </Link>
        ))}
      </nav>

      {/* Main content */}
      <main className="flex-1 p-5 md:p-12 overflow-auto max-w-4xl">
        {children}
      </main>
    </div>
  );
}
