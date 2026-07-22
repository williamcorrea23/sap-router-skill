"use client";

import { useEffect, useState } from "react";

export interface Profile {
  name: string;
  company: string;
  email: string;
  role: "admin" | "member" | "";
  loaded: boolean;
}

const EMPTY: Profile = { name: "", company: "", email: "", role: "", loaded: false };
const EVENT = "profile-changed";
const STORAGE_KEY = "profile-cache";
// How long a fetched profile is served without revalidating. Role/company
// changes are rare; in-session edits go through profileChanged() which
// bypasses the TTL.
const TTL_MS = 60_000;

// Shared across all useProfile() consumers so a navigation never waits on the
// network for data we already have (e.g. the Settings sidebar deciding
// whether to show the admin-only Company item).
let cache: Profile | null = null;
let fetchedAt = 0;
let inflight: Promise<void> | null = null;

function readStorage(): Profile | null {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const d = JSON.parse(raw);
    return {
      name: typeof d.name === "string" ? d.name : "",
      company: typeof d.company === "string" ? d.company : "",
      email: typeof d.email === "string" ? d.email : "",
      role: d.role === "admin" || d.role === "member" ? d.role : "",
      loaded: true,
    };
  } catch {
    return null;
  }
}

function revalidate(): Promise<void> {
  if (!inflight) {
    inflight = fetch("/api/profile")
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => {
        if (d) {
          cache = {
            name: d.display_name ?? "",
            company: d.company ?? "",
            email: d.email ?? "",
            role: d.role ?? "",
            loaded: true,
          };
          fetchedAt = Date.now();
          try {
            sessionStorage.setItem(STORAGE_KEY, JSON.stringify(cache));
          } catch {
            /* storage full/blocked — cache still works in-memory */
          }
          window.dispatchEvent(new Event(EVENT));
        }
      })
      .catch(() => {})
      .finally(() => {
        inflight = null;
      });
  }
  return inflight;
}

/** Notify all useProfile() consumers to re-fetch (after saving settings). */
export function profileChanged() {
  fetchedAt = 0;
  void revalidate();
}

/** Drop the cached profile (call on logout, before navigating away). */
export function clearProfileCache() {
  cache = null;
  fetchedAt = 0;
  try {
    sessionStorage.removeItem(STORAGE_KEY);
  } catch {
    /* ignore */
  }
}

/**
 * The signed-in user's profile — server-backed (Change Order 03): display
 * name and role from the profiles table, company from the companies table.
 * Cached module-wide + in sessionStorage (stale-while-revalidate), so
 * consumers render instantly on navigation instead of waiting a round-trip.
 */
export function useProfile(): Profile {
  // Initialize from the in-memory cache only: on a full page load the cache
  // is empty on both server and client, so hydration stays consistent; on
  // client-side navigation the cache serves the profile synchronously.
  const [profile, setProfile] = useState<Profile>(() => cache ?? EMPTY);
  useEffect(() => {
    if (!cache) {
      const stored = readStorage();
      if (stored) {
        cache = stored;
        // Session-restored data may be stale — repaint now, revalidate below.
        fetchedAt = 0;
      }
    }
    if (cache) setProfile(cache);
    if (Date.now() - fetchedAt > TTL_MS) void revalidate();
    const onUpdate = () => {
      if (cache) setProfile(cache);
    };
    window.addEventListener(EVENT, onUpdate);
    return () => window.removeEventListener(EVENT, onUpdate);
  }, []);
  return profile;
}
