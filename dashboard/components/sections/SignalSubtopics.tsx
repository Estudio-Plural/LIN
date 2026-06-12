import { subtopicsOfSignal, Video, fmtNum } from "@/lib/data";
import { SectionTitle, Card, Callout } from "@/components/ui";

export function SignalSubtopics({ videos }: { videos: Video[] }) {
  const rows = subtopicsOfSignal(videos);
  if (!rows.length) return null;
  const total = rows.reduce((s, r) => s + r.count, 0);
  const max = rows[0].count;
  const top = rows[0];

  return (
    <section id="subtemas">
      <SectionTitle
        kicker="★ Dentro de la señal"
        title="De qué habla la manosfera cuando habla en serio"
        subtitle={`Subtemas de los ${total} videos clasificados como manosfera sincera. La barra mide cuánto pesa cada marco dentro de la señal; al lado, su viralidad típica.`}
      />
      <Card className="p-6">
        <div className="space-y-3">
          {rows.map((r) => (
            <div
              key={r.subtema}
              className="grid grid-cols-[105px_1fr] items-center gap-x-3 gap-y-1 sm:grid-cols-[150px_1fr_230px]"
            >
              <div className="truncate text-sm font-medium text-zinc-200">{r.label}</div>
              <div className="h-5 overflow-hidden rounded bg-zinc-800/50">
                <div
                  className="h-full rounded"
                  style={{
                    width: `${Math.max(2, (100 * r.count) / max)}%`,
                    background: "linear-gradient(90deg, #7f1d1d, #ef4444)",
                  }}
                />
              </div>
              <div className="col-span-2 text-xs tabular-nums text-zinc-500 sm:col-span-1 sm:text-right">
                <span className="font-semibold text-zinc-100">{r.count}</span> · {r.share}% · mediana{" "}
                {fmtNum(r.playsMedian)} plays
              </div>
            </div>
          ))}
        </div>
        <Callout className="mt-6">
          <strong className="text-zinc-100">«{top.label}»</strong> es el marco que más pesa dentro de la señal
          ({top.share}% de los videos sinceros)
          {rows.length > 2 && (
            <>
              , seguido de <strong className="text-zinc-100">{rows[1].label.toLowerCase()}</strong> y{" "}
              <strong className="text-zinc-100">{rows[2].label.toLowerCase()}</strong>
            </>
          )}
          . La señal no es un bloque: va de lo estético (looksmaxxing) a lo ideológico (red pill, antifeminismo) —
          intervenir cada marco requiere lenguajes distintos.
        </Callout>
      </Card>
    </section>
  );
}
