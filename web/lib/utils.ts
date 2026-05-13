import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * "in X minutes" / "in 2 hours" / "tomorrow at 7:00 AM"
 * Human-friendly relative time for next_run.
 */
export function formatRelativeTime(iso: string | null): string {
  if (!iso) return "—";
  const date = new Date(iso);
  const now = new Date();
  const diffMs = date.getTime() - now.getTime();
  const diffMin = Math.round(diffMs / 60_000);

  if (diffMin < 0) return "overdue";
  if (diffMin < 1) return "in <1m";
  if (diffMin < 60) return `in ${diffMin}m`;

  const diffHr = Math.round(diffMin / 60);
  if (diffHr < 24) return `in ${diffHr}h`;

  const diffDays = Math.round(diffHr / 24);
  if (diffDays < 7) return `in ${diffDays}d`;

  return date.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
  });
}

/** "2 minutes ago" / "yesterday 3:00 PM" */
export function formatRelativePast(iso: string | null): string {
  if (!iso) return "—";
  const date = new Date(iso);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.round(diffMs / 1000);

  if (diffSec < 60) return "just now";
  const diffMin = Math.round(diffSec / 60);
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHr = Math.round(diffMin / 60);
  if (diffHr < 24) return `${diffHr}h ago`;
  const diffDays = Math.round(diffHr / 24);
  if (diffDays < 30) return `${diffDays}d ago`;

  return date.toLocaleDateString();
}
