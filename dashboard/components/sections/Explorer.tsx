"use client";
import { useMemo, useState } from "react";
import { Video, fmtNum, LABEL_META } from "@/lib/data";
import { SectionTitle, Card, Badge } from "@/components/ui";

const PAGE = 25;

export function Explorer({ videos }: { videos: Video[] }) {
  const [q, setQ] = useState("");
  const [label, setLabel] = useState<string | null>(null);
  const [sort, setSort] = useState<"plays" | "recent">("plays");
  const [limit, setLimit] = useState(PAGE);

  const labelCounts = useMemo(() => {
    const counts = new Map<string, number>();
    for (const v of videos) if (v.label) counts.set(v.label, (counts.get(v.label) ?? 0) + 1);
    return counts;
  }, [videos]);

  const rows = useMemo(() => {
    let vs = videos;
    if (label) vs = vs.filter((v) => v.label === label);
    const t = q.trim().toLowerCase();
    if (t) {
      vs = vs.filter(
        (v) =>
          v.text.toLowerCase().includes(t) ||
          (v.author ?? "").toLowerCase().includes(t) ||
          v.keyword.toLowerCase().includes(t) ||
          v.hashtags.some((h) => h.toLowerCase().includes(t))
      );
    }
    return [...vs].sort((a, b) => (sort === "plays" ? b.plays - a.plays : b.created.localeCompare(a.created)));
  }, [videos, q, label, sort]);

  const visible = rows.slice(0, limit);

  return (
    <section id="explorador">
      <SectionTitle
        kicker="Evidencia"
        title="El corpus, video por video"
        subtitle="Buscá por texto, autor, keyword o hashtag y filtrá por clasificación. Cada fila muestra la razón que dio el modelo al etiquetar — la capa de IA es auditable, no una caja negra."
      />
      <Card className="overflow-hidden p-0">
        <div className="flex flex-col gap-3 border-b border-zinc-800 px-5 py-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <input
              type="search"
              value={q}
              onChange={(e) => {
                setQ(e.target.value);
                setLimit(PAGE);
              }}
              placeholder="Buscar texto, autor, keyword…"
              className="w-full rounded-lg border border-zinc-800 bg-zinc-900/60 px-3 py-1.5 text-sm text-zinc-200 placeholder:text-zinc-600 focus:border-zinc-600 focus:outline-none sm:w-72"
            />
            <div className="flex items-center gap-3">
              <div className="inline-flex rounded-lg border border-zinc-800 bg-zinc-900/60 p-0.5 text-xs">
                <button
                  onClick={() => setSort("plays")}
                  className={`rounded-md px-2.5 py-1 font-medium transition-colors ${sort === "plays" ? "bg-zinc-700 text-zinc-50" : "text-zinc-400 hover:text-zinc-200"}`}
                >
                  Más vistos
                </button>
                <button
                  onClick={() => setSort("recent")}
                  className={`rounded-md px-2.5 py-1 font-medium transition-colors ${sort === "recent" ? "bg-zinc-700 text-zinc-50" : "text-zinc-400 hover:text-zinc-200"}`}
                >
                  Más recientes
                </button>
              </div>
              <span className="text-xs tabular-nums text-zinc-500">{rows.length.toLocaleString("es")} videos</span>
            </div>
          </div>
          {labelCounts.size > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {Object.entries(LABEL_META)
                .filter(([k]) => labelCounts.has(k))
                .map(([k, m]) => {
                  const active = label === k;
                  return (
                    <button
                      key={k}
                      onClick={() => {
                        setLabel(active ? null : k);
                        setLimit(PAGE);
                      }}
                      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium transition-colors ${
                        active ? "" : "border-zinc-800 text-zinc-400 hover:text-zinc-200"
                      }`}
                      style={active ? { borderColor: `${m.color}80`, backgroundColor: `${m.color}1a`, color: m.color } : undefined}
                    >
                      <span className="h-1.5 w-1.5 rounded-full" style={{ background: m.color }} />
                      {m.es} · {labelCounts.get(k)}
                    </button>
                  );
                })}
            </div>
          )}
        </div>

        <div className="divide-y divide-zinc-800/70">
          {visible.map((v) => (
            <div key={v.id} className="flex flex-col gap-2 px-5 py-4 sm:flex-row sm:items-start sm:gap-4">
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-zinc-500">
                  <a
                    href={v.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-semibold text-zinc-200 transition-colors hover:text-red-400"
                  >
                    @{v.author ?? "—"} ↗
                  </a>
                  <span className="tabular-nums">{v.created}</span>
                  <span className="rounded bg-zinc-800/80 px-1.5 py-0.5 text-[10px] text-zinc-400">{v.keyword}</span>
                </div>
                <p className="mt-1 line-clamp-2 text-sm leading-relaxed text-zinc-300">{v.text || "(sin texto)"}</p>
                {v.razon && (
                  <p className="mt-1.5 border-l-2 border-zinc-700 pl-2 text-xs italic leading-relaxed text-zinc-500">
                    {v.razon}
                  </p>
                )}
              </div>
              <div className="flex shrink-0 items-center gap-3 sm:flex-col sm:items-end sm:gap-1.5">
                {v.label && LABEL_META[v.label] && <Badge color={LABEL_META[v.label].color}>{LABEL_META[v.label].es}</Badge>}
                <div className="text-sm tabular-nums">
                  <span className="font-semibold text-zinc-100">{fmtNum(v.plays)}</span>{" "}
                  <span className="text-zinc-500">plays</span>
                </div>
              </div>
            </div>
          ))}
          {!visible.length && (
            <div className="px-5 py-10 text-center text-sm text-zinc-500">Nada matchea ese filtro.</div>
          )}
        </div>

        {limit < rows.length && (
          <div className="border-t border-zinc-800 p-3 text-center">
            <button
              onClick={() => setLimit((l) => l + PAGE)}
              className="rounded-full border border-zinc-700 px-4 py-1.5 text-xs font-medium text-zinc-300 transition-colors hover:border-zinc-500 hover:text-zinc-100"
            >
              Mostrar {Math.min(PAGE, rows.length - limit)} más · quedan {(rows.length - limit).toLocaleString("es")}
            </button>
          </div>
        )}
      </Card>
    </section>
  );
}
