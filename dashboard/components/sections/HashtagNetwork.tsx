"use client";
import dynamic from "next/dynamic";
import { useEffect, useMemo, useRef, useState } from "react";
import { NetworkData, CATEGORY_COLORS, CATEGORY_LABELS, LABEL_META } from "@/lib/data";
import { Card, SectionTitle } from "@/components/ui";

const ForceGraph2D = dynamic(() => import("react-force-graph-2d"), { ssr: false }) as unknown as React.ComponentType<
  Record<string, unknown>
>;

type FNode = {
  id: string;
  val: number;
  r: number;
  color: string;
  top_url?: string;
  x?: number;
  y?: number;
};

export function HashtagNetwork({ network }: { network: NetworkData }) {
  const [mode, setMode] = useState<"hashtag" | "creators">("hashtag");
  const wrapRef = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(0);

  useEffect(() => {
    if (!wrapRef.current) return;
    const ro = new ResizeObserver((entries) => setWidth(entries[0].contentRect.width));
    ro.observe(wrapRef.current);
    return () => ro.disconnect();
  }, []);

  const graph = useMemo(() => {
    if (mode === "hashtag") {
      const nodes: FNode[] = network.hashtag.nodes.map((n) => ({
        id: n.id,
        val: n.freq ?? 1,
        r: Math.min(15, Math.max(3, Math.sqrt(n.freq ?? 1) * 1.4)),
        color: CATEGORY_COLORS[n.cluster ?? ""] ?? "#71717a",
      }));
      return { nodes, links: network.hashtag.links.map((l) => ({ ...l })) };
    }
    const maxReach = Math.max(...network.creators.nodes.map((n) => n.reach ?? 1), 1);
    const nodes: FNode[] = network.creators.nodes.map((n) => ({
      id: n.id,
      val: n.videos ?? 1,
      r: 4 + Math.sqrt((n.reach ?? 1) / maxReach) * 18,
      color: (n.label && LABEL_META[n.label]?.color) || "#71717a",
      top_url: n.top_url,
    }));
    return { nodes, links: network.creators.links.map((l) => ({ ...l })) };
  }, [mode, network]);

  const height = 560;

  return (
    <section id="red">
      <SectionTitle
        kicker="★ La red"
        title="Cómo se conecta la conversación"
        subtitle={
          mode === "hashtag"
            ? "Cada nodo es un hashtag; el grosor de la línea, cuántas veces co-ocurren en un mismo video. El color es la categoría dominante. Arrastrá, hacé zoom, explorá los clusters."
            : "Cada nodo es un creador (tamaño = alcance); se conectan si comparten hashtags. El color es su clasificación. Clic en un creador para abrir su video más visto."
        }
      />
      <Card className="overflow-hidden p-0">
        <div className="flex items-center justify-between border-b border-zinc-800 px-4 py-3">
          <div className="inline-flex rounded-lg border border-zinc-800 bg-zinc-900/60 p-0.5 text-sm">
            <button
              onClick={() => setMode("hashtag")}
              className={`rounded-md px-3 py-1 font-medium transition-colors ${mode === "hashtag" ? "bg-zinc-700 text-zinc-50" : "text-zinc-400 hover:text-zinc-200"}`}
            >
              Hashtags
            </button>
            <button
              onClick={() => setMode("creators")}
              className={`rounded-md px-3 py-1 font-medium transition-colors ${mode === "creators" ? "bg-zinc-700 text-zinc-50" : "text-zinc-400 hover:text-zinc-200"}`}
            >
              Creadores
            </button>
          </div>
          <div className="flex flex-wrap gap-x-3 gap-y-1 text-[11px] text-zinc-500">
            {mode === "hashtag"
              ? Object.entries(CATEGORY_LABELS).map(([k, v]) => (
                  <span key={k} className="inline-flex items-center gap-1">
                    <span className="h-2 w-2 rounded-full" style={{ background: CATEGORY_COLORS[k] }} />
                    {v}
                  </span>
                ))
              : Object.entries(LABEL_META).map(([k, m]) => (
                  <span key={k} className="inline-flex items-center gap-1">
                    <span className="h-2 w-2 rounded-full" style={{ background: m.color }} />
                    {m.es}
                  </span>
                ))}
          </div>
        </div>
        <div ref={wrapRef} style={{ height }} className="relative bg-[#0a0a0c]">
          {width > 0 && (
            <ForceGraph2D
              graphData={graph}
              width={width}
              height={height}
              backgroundColor="#0a0a0c"
              cooldownTicks={120}
              linkColor={() => "#3f3f4666"}
              linkWidth={(l: { weight?: number }) => Math.min(4, Math.sqrt(l.weight ?? 1))}
              nodeLabel={(n: FNode) => n.id}
              onNodeClick={(n: FNode) => {
                if (mode === "creators" && n.top_url) window.open(n.top_url, "_blank");
              }}
              nodeCanvasObject={(n: FNode, ctx: CanvasRenderingContext2D, scale: number) => {
                const r = n.r;
                ctx.beginPath();
                ctx.arc(n.x ?? 0, n.y ?? 0, r, 0, 2 * Math.PI);
                ctx.fillStyle = n.color;
                ctx.globalAlpha = 0.85;
                ctx.fill();
                ctx.globalAlpha = 1;
                if (r * scale > 7) {
                  const fontSize = Math.max(2.5, 11 / scale);
                  ctx.font = `${fontSize}px var(--font-geist-sans), sans-serif`;
                  ctx.fillStyle = "#d4d4d8";
                  ctx.textAlign = "center";
                  ctx.textBaseline = "middle";
                  ctx.fillText(n.id, n.x ?? 0, (n.y ?? 0) + r + fontSize);
                }
              }}
            />
          )}
        </div>
      </Card>
    </section>
  );
}
