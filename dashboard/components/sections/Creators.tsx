import { topCreators, Video, fmtNum, LABEL_META } from "@/lib/data";
import { SectionTitle, Card, Badge } from "@/components/ui";

export function Creators({ videos }: { videos: Video[] }) {
  const creators = topCreators(videos, 12);
  return (
    <section>
      <SectionTitle
        kicker="La oferta"
        title="Los creadores que concentran el alcance"
        subtitle="Top por reproducciones acumuladas en el periodo. Clic en cualquiera para ver su video más visto. La etiqueta de color aparece cuando hay clasificación."
      />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {creators.map((c) => (
          <a key={c.author} href={c.topUrl} target="_blank" rel="noopener noreferrer" className="group block">
            <Card className="h-full p-4 transition-colors group-hover:border-zinc-600">
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0">
                  <div className="truncate font-semibold text-zinc-100">@{c.author}</div>
                  {c.nick && <div className="truncate text-xs text-zinc-500">{c.nick}</div>}
                </div>
                {c.label && LABEL_META[c.label] && (
                  <Badge color={LABEL_META[c.label].color}>{LABEL_META[c.label].es}</Badge>
                )}
              </div>
              <div className="mt-3 flex items-baseline gap-4 text-sm">
                <span><span className="font-semibold tabular-nums text-zinc-100">{fmtNum(c.plays)}</span> <span className="text-zinc-500">plays</span></span>
                <span><span className="font-semibold tabular-nums text-zinc-100">{c.videos}</span> <span className="text-zinc-500">videos</span></span>
                <span><span className="font-semibold tabular-nums text-zinc-100">{c.pctLatam}%</span> <span className="text-zinc-500">LATAM</span></span>
              </div>
              {c.topText && <p className="mt-2 line-clamp-2 text-xs leading-relaxed text-zinc-400">{c.topText}</p>}
              <div className="mt-2 flex flex-wrap gap-1">
                {c.keywords.slice(0, 3).map((k) => (
                  <span key={k} className="rounded bg-zinc-800/80 px-1.5 py-0.5 text-[10px] text-zinc-400">{k}</span>
                ))}
              </div>
            </Card>
          </a>
        ))}
      </div>
    </section>
  );
}
