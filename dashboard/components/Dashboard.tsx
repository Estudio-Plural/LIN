"use client";
import { useEffect, useMemo, useState } from "react";
import { Video, Meta, NetworkData, CATEGORY_LABELS, CATEGORY_COLORS } from "@/lib/data";
import { StatsBar } from "./sections/StatsBar";
import { SignalVsNoise } from "./sections/SignalVsNoise";
import { HashtagNetwork } from "./sections/HashtagNetwork";
import { CategoryMap } from "./sections/CategoryMap";
import { Geography } from "./sections/Geography";
import { Engagement } from "./sections/Engagement";
import { Creators } from "./sections/Creators";
import { BridgeCallout } from "./sections/BridgeCallout";
import { Methodology } from "./sections/Methodology";

export function Dashboard() {
  const [videos, setVideos] = useState<Video[] | null>(null);
  const [meta, setMeta] = useState<Meta | null>(null);
  const [network, setNetwork] = useState<NetworkData | null>(null);
  const [cat, setCat] = useState<string | null>(null);
  const [hideNoise, setHideNoise] = useState(false);

  useEffect(() => {
    Promise.all([
      fetch("/data/videos.json").then((r) => r.json()),
      fetch("/data/meta.json").then((r) => r.json()),
      fetch("/data/network.json").then((r) => r.json()),
    ])
      .then(([v, m, n]) => {
        setVideos(v);
        setMeta(m);
        setNetwork(n);
      })
      .catch(() => setVideos([]));
  }, []);

  const filtered = useMemo(() => {
    if (!videos) return [];
    let vs = videos;
    if (cat) vs = vs.filter((v) => v.category === cat);
    if (hideNoise && meta?.classified) vs = vs.filter((v) => v.label === "manosfera_sincera");
    return vs;
  }, [videos, cat, hideNoise, meta]);

  if (!videos || !meta || !network) {
    return (
      <div className="flex min-h-screen items-center justify-center text-sm text-zinc-500">
        <div className="animate-pulse">Cargando datos…</div>
      </div>
    );
  }

  return (
    <div>
      <header className="border-b border-zinc-800 bg-gradient-to-b from-red-950/20 to-transparent">
        <div className="mx-auto max-w-6xl px-6 py-16 sm:py-20">
          <div className="text-xs font-semibold uppercase tracking-widest text-red-500">
            Piloto de escucha digital · Estudio Plural × Camino
          </div>
          <h1 className="mt-3 max-w-3xl text-4xl font-bold tracking-tight text-zinc-50 sm:text-5xl">
            Radiografía de la manosfera hispana
          </h1>
          <p className="mt-4 max-w-2xl text-base leading-relaxed text-zinc-400 sm:text-lg">
            Qué se dice, quién lo dice y cuánto de eso es señal real.{" "}
            {meta.total_videos.toLocaleString("es")} videos de TikTok, febrero–mayo 2026.
          </p>
        </div>
      </header>

      <div className="sticky top-0 z-20 border-b border-zinc-800 bg-[#09090b]/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-6 py-3">
          <div className="flex flex-wrap gap-1.5">
            <FilterBtn active={cat === null} onClick={() => setCat(null)}>Todas</FilterBtn>
            {Object.entries(CATEGORY_LABELS).map(([k, v]) => (
              <FilterBtn key={k} active={cat === k} color={CATEGORY_COLORS[k]} onClick={() => setCat(cat === k ? null : k)}>
                {v}
              </FilterBtn>
            ))}
          </div>
          <button
            disabled={!meta.classified}
            onClick={() => setHideNoise((x) => !x)}
            title={meta.classified ? "" : "Requiere clasificación"}
            className={`inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-medium transition-colors ${
              hideNoise ? "border-red-500/50 bg-red-500/15 text-red-300" : "border-zinc-700 text-zinc-400 hover:text-zinc-200"
            } ${!meta.classified ? "cursor-not-allowed opacity-40" : ""}`}
          >
            <span className={`h-2 w-2 rounded-full ${hideNoise ? "bg-red-400" : "bg-zinc-600"}`} />
            Solo manosfera real
          </button>
        </div>
      </div>

      <main className="mx-auto max-w-6xl space-y-16 px-6 py-12">
        <StatsBar meta={meta} />
        <SignalVsNoise videos={filtered} classified={meta.classified} />
        <HashtagNetwork network={network} />
        <CategoryMap videos={filtered} />
        <div className="grid gap-5 lg:grid-cols-2">
          <Geography videos={filtered} />
          <Engagement videos={filtered} />
        </div>
        <BridgeCallout videos={filtered} />
        <Creators videos={filtered} />
        <Methodology meta={meta} />
      </main>

      <footer className="border-t border-zinc-800 py-8 text-center text-xs text-zinc-600">
        LIN · Estudio Plural × Camino · {meta.total_videos.toLocaleString("es")} videos · datos {meta.generated_at}
      </footer>
    </div>
  );
}

function FilterBtn({
  active,
  color,
  onClick,
  children,
}: {
  active: boolean;
  color?: string;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={`rounded-full border px-3 py-1.5 text-xs font-medium transition-colors ${
        active ? "border-zinc-500 bg-zinc-800 text-zinc-50" : "border-zinc-800 text-zinc-400 hover:text-zinc-200"
      }`}
      style={active && color ? { borderColor: `${color}80`, color } : undefined}
    >
      {children}
    </button>
  );
}
