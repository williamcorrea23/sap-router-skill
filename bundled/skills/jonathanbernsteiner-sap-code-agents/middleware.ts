/**
 * Session middleware: refreshes the Supabase cookie session and gates every
 * route. Only the auth pages (login, forgot/reset
 * password, invitation acceptance) and the auth callback are public.
 * API routes get a 401 here when no session cookie exists — unless the
 * request carries a Bearer token, which the route itself validates.
 */
import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";

const PUBLIC_PREFIXES = ["/login", "/forgot-password", "/reset-password", "/invite", "/auth"];

function isPublic(path: string): boolean {
  return PUBLIC_PREFIXES.some((p) => path === p || path.startsWith(p + "/"));
}

export async function middleware(request: NextRequest) {
  let response = NextResponse.next({ request });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll: () => request.cookies.getAll(),
        setAll: (toSet) => {
          toSet.forEach(({ name, value }) => request.cookies.set(name, value));
          response = NextResponse.next({ request });
          toSet.forEach(({ name, value, options }) => response.cookies.set(name, value, options));
        },
      },
    }
  );

  // getUser() (not getSession) — revalidates the JWT with Supabase.
  const {
    data: { user },
  } = await supabase.auth.getUser();

  const path = request.nextUrl.pathname;

  if (!user) {
    // Invitation lookup/acceptance authenticate via the invite token itself.
    if (path.startsWith("/api/invitations/")) return response;
    if (path.startsWith("/api")) {
      // Routes validate Bearer tokens themselves; without either credential
      // the request is rejected here already.
      if (request.headers.get("authorization")) return response;
      return Response.json({ error: "not authenticated" }, { status: 401 });
    }
    if (!isPublic(path)) {
      const url = request.nextUrl.clone();
      url.pathname = "/login";
      url.search = "";
      if (path !== "/") url.searchParams.set("next", path);
      return NextResponse.redirect(url);
    }
  }

  // "/" stays reachable when signed in — it is the smart landing page that
  // resolves to the last-opened workspace client-side.
  if (user && path === "/login") {
    const url = request.nextUrl.clone();
    url.pathname = "/";
    url.search = "";
    return NextResponse.redirect(url);
  }

  return response;
}

export const config = {
  // Everything except Next internals and static assets.
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|ico|webp)$).*)"],
};
