"use client";
import dynamic from "next/dynamic";
import { useEffect, useMemo, useRef, useState } from "react";
import { NetworkData, Community, LABEL_META, LABEL_ORDER, fmtNum } from "@/lib/data";
import { Card, SectionTitle, Callout } from "@/components/ui";

const ForceGraph2D = dynamic(() => import("react-force-graph-2d"), { ssr: false }) as unknown as React.ComponentType<
  Record<string, unknown>
>;

type FNode = {
  id: string;
  val: number;
  r: number;
  color: string;
  x?: number;
  y?: number;
};

function purity(c: Community): number {
  const total = Object.values(c.label_dist).reduce((a, b) => a + b, 0) || 1;
  return Math.round((100 * (c.label_dist["manosfera_sincera"] ?? 0)) / total);
}

function segments(c: Community) {
  const total = Object.values(c.label_dist).reduce((a, b) => a + b, 0) || 1;
  return LABEL_ORDER.filter((l) => c.label_dist[l]).map((l) => ({
    label: l,
    count: c.label_dist[l],
    pct: (100 * c.label_dist[l]) / total,
    color: LABEL_META[l]?.color ?? "#52525b",
  }));
}

export function HashtagNetwork({ network }: { network: NetworkData }) {
  const wrapRef = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(0);

  useEffect(() => {
    if (!wrapRef.current) return;
    const ro = new ResizeObserver((entries) => setWidth(entries[0].contentRect.width));
    ro.observe(wrapRef.current);
    return () => ro.disconnect();
  }, []);

  const communities = network.communities;
  const coverage = network.meta?.coverage_pct ?? 0;
  const noiseShare = communities
    .filter((c) => c.dominant_label === "medio_periodismo" || c.dominant_label === "falso_positivo")
    .reduce((s, c) => s + c.share, 0);

  const graph = useMemo(() => {
    const nodes: FNode[] = network.hashtag.nodes.map((n) => ({
      id: n.id,
      val: n.freq,
      r: Math.min(16, Math.max(3, Math.sqrt(n.freq) * 1.6)),
      color: n.color,
    }));
    return { nodes, links: network.hashtag.links.map((l) => ({ ...l })) };
  }, [network]);

  const height = 520;

  return (
    <section id="red">
      <SectionTitle
        kicker="★ La red"
        title="Las comunidades de la conversación"
        subtitle={
          <>
            Conectamos los hashtags que aparecen en un mismo video y los agrupamos por co-ocurrencia —no por
            la keyword con que se buscaron—. Cada grupo es una comunidad temática real. Cubre el {coverage}% de
            los videos (los que usan hashtags recurrentes).
          </>
        }
      />

      <Callout className="mb-6">
        <strong className="text-zinc-100">{noiseShare}% de la conversación etiquetada</strong> son comunidades
        dominadas por ruido —prensa anglosajona cubriendo el documental de Louis Theroux y fan-edits de “The
        Boys”— que inflan el volumen sin producir manosfera. El fenómeno hispano sincero se concentra en alto
        valor, autosuperación y “potencia masculina”.
      </Callout>

      {/* Panel de comunidades anotadas */}
      <ul className="grid gap-4 sm:grid-cols-2">
        {communities.map((c) => {
          const pur = purity(c);
          return (
            <li key={c.id} className="rounded-xl border border-zinc-800 bg-zinc-900/40 p-4">
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-2">
                  <span className="h-2.5 w-2.5 shrink-0 rounded-full" style={{ background: c.color }} />
                  <h3 className="font-semibold leading-tight text-zinc-100">{c.name}</h3>
                </div>
                <span className="shrink-0 text-sm font-semibold tabular-nums text-zinc-300">{c.share}%</span>
              </div>
              <p className="mt-1.5 text-xs leading-relaxed text-zinc-400">{c.desc || c.auto}</p>

              <div
                className="mt-3 flex h-1.5 w-full overflow-hidden rounded-full bg-zinc-800"
                role="img"
                aria-label={`${pur}% manosfera sincera`}
              >
                {segments(c).map((s) => (
                  <span
                    key={s.label}
                    style={{ width: `${s.pct}%`, background: s.color }}
                    title={`${LABEL_META[s.label]?.es ?? s.label}: ${s.count}`}
                  />
                ))}
              </div>
              <div className="mt-1.5 flex items-center justify-between text-[11px] text-zinc-500">
                <span>{pur}% señal sincera</span>
                <span>
                  {c.n_videos} videos · {fmtNum(c.plays)} plays
                </span>
              </div>

              <div className="mt-3 flex flex-wrap gap-1">
                {c.hashtags.slice(0, 6).map((h) => (
                  <span key={h} className="rounded bg-zinc-800/80 px-1.5 py-0.5 text-[11px] text-zinc-400">
                    #{h}
                  </span>
                ))}
              </div>
            </li>
          );
        })}
      </ul>

      {/* Grafo interactivo, coloreado por comunidad */}
      <Card className="mt-6 overflow-hidden p-0">
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 border-b border-zinc-800 px-4 py-3 text-[11px] text-zinc-500">
          <span className="mr-1 text-zinc-400">Comunidades:</span>
          {communities.map((c) => (
            <span key={c.id} className="inline-flex items-center gap-1">
              <span className="h-2 w-2 rounded-full" style={{ background: c.color }} />
              {c.name}
            </span>
          ))}
        </div>
        <div
          ref={wrapRef}
          style={{ height }}
          className="relative bg-[#0a0a0c]"
          role="img"
          aria-label="Grafo de co-ocurrencia de hashtags agrupado por comunidad temática. El detalle textual está en el panel de comunidades de arriba."
        >
          {width > 0 && (
            <ForceGraph2D
              graphData={graph}
              width={width}
              height={height}
              backgroundColor="#0a0a0c"
              cooldownTicks={120}
              linkColor={() => "#3f3f4666"}
              linkWidth={(l: { weight?: number }) => Math.min(4, Math.sqrt(l.weight ?? 1))}
              nodeLabel={(n: FNode) => `#${n.id}`}
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
