import { ReactNode } from "react";

export function Card({
  children,
  className = "",
  id,
}: {
  children: ReactNode;
  className?: string;
  id?: string;
}) {
  return (
    <div
      id={id}
      className={`rounded-xl border border-zinc-800 bg-[#131316] ${className}`}
    >
      {children}
    </div>
  );
}

export function SectionTitle({
  kicker,
  title,
  subtitle,
}: {
  kicker?: string;
  title: string;
  subtitle?: ReactNode;
}) {
  return (
    <div className="mb-6 max-w-3xl">
      {kicker && (
        <div className="mb-2 text-xs font-semibold uppercase tracking-widest text-red-500">
          {kicker}
        </div>
      )}
      <h2 className="text-2xl font-bold tracking-tight text-zinc-50 sm:text-3xl">{title}</h2>
      {subtitle && <p className="mt-2 text-sm leading-relaxed text-zinc-400">{subtitle}</p>}
    </div>
  );
}

export function Stat({
  value,
  label,
  hint,
  accent = false,
}: {
  value: ReactNode;
  label: string;
  hint?: string;
  accent?: boolean;
}) {
  return (
    <div className="flex flex-col">
      <span
        className={`text-3xl font-bold tracking-tight sm:text-4xl tabular-nums ${accent ? "text-red-500" : "text-zinc-50"}`}
      >
        {value}
      </span>
      <span className="mt-1 text-sm font-medium text-zinc-400">{label}</span>
      {hint && <span className="mt-0.5 text-xs text-zinc-600">{hint}</span>}
    </div>
  );
}

export function Badge({
  children,
  color,
  className = "",
}: {
  children: ReactNode;
  color?: string;
  className?: string;
}) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium ${className}`}
      style={
        color
          ? { borderColor: `${color}55`, backgroundColor: `${color}1a`, color }
          : { borderColor: "#3f3f46", color: "#d4d4d8" }
      }
    >
      {color && <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: color }} />}
      {children}
    </span>
  );
}

export function Callout({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={`rounded-lg border-l-2 border-red-500/60 bg-red-500/5 px-4 py-3 text-sm text-zinc-300 ${className}`}
    >
      {children}
    </div>
  );
}
