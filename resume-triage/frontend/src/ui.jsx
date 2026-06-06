import React from "react";

export const TIER_COLOR = {
  A: "bg-emerald-100 text-emerald-800 border-emerald-200",
  B: "bg-amber-100 text-amber-800 border-amber-200",
  C: "bg-slate-100 text-slate-600 border-slate-200",
};

export function Badge({ children, className = "" }) {
  return (
    <span className={`inline-block rounded-full border px-2 py-0.5 text-xs font-medium ${className}`}>
      {children}
    </span>
  );
}

export function TierBadge({ tier, status }) {
  if (status === "KNOCKED_OUT")
    return <Badge className="bg-red-100 text-red-700 border-red-200">Knocked out</Badge>;
  if (!tier) return <Badge className="bg-slate-100 text-slate-500 border-slate-200">—</Badge>;
  return <Badge className={TIER_COLOR[tier] || ""}>Tier {tier}</Badge>;
}

export function Button({ children, variant = "primary", className = "", ...props }) {
  const styles = {
    primary: "bg-slate-900 text-white hover:bg-slate-700",
    ghost: "bg-white text-slate-700 border border-slate-300 hover:bg-slate-100",
    danger: "bg-red-600 text-white hover:bg-red-500",
  };
  return (
    <button
      className={`rounded-md px-3 py-1.5 text-sm font-medium transition disabled:opacity-50 ${styles[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}

export function Card({ title, children, right }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
      {title && (
        <div className="flex items-center justify-between border-b border-slate-100 px-4 py-3">
          <h3 className="text-sm font-semibold text-slate-700">{title}</h3>
          {right}
        </div>
      )}
      <div className="p-4">{children}</div>
    </div>
  );
}

export function ScoreBar({ value, max = 5 }) {
  const pct = Math.max(0, Math.min(100, (value / max) * 100));
  const color = pct >= 70 ? "bg-emerald-500" : pct >= 40 ? "bg-amber-500" : "bg-red-400";
  return (
    <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
      <div className={`h-full ${color}`} style={{ width: `${pct}%` }} />
    </div>
  );
}
