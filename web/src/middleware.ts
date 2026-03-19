// Middleware lives at web/middleware.ts (project root).
// This stub satisfies Next.js's file detection. The root middleware runs instead.
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(_req: NextRequest) {
  return NextResponse.next();
}

export const config = { matcher: [] };
