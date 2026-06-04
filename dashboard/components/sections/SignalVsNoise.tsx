"use client";
import {
  ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid,
} from "recharts";
import { labelDistribution, labelByKeyword, Video, LABEL_META } from "@/lib/data";
import { Card, SectionTitle, Badge } from "@/components/ui";

export function SignalVsNoise({ videos, classified }: { videos: Video[]; classified: boolean }) {
  if (!classified) {
    return (
      <section id="senal-ruido">
        <SectionTitle
          kicker="★ Señal vs Ruido"
          title="No todo lo que matchea es manosfera"
          subtitle="El volumen crudo de keywords sobreestima el fenómeno: incluye crítica feminista, sátira, cobertura mediática y falsos positivos. Esta capa clasifica cada video para dar una cifra honesta."
        />
        <Card className="p-8">
          <div className="flex flex-col items-center gap-4 py-8 text-center">
            <div className="rounded-full border border-red-500/30 bg-red-500/10 px-3 py-1 text-xs font-medium text-red-400">
              Clasificación pendiente
            </div>
            <p className="max-w-xl text-sm text-zinc-400">
              Esta sección se enciende al correr la clasificación con <code className="text-zinc-300">gemini-2.5-flash</code>.
              Cada video se etiqueta en una de estas categorías:
            </p>
            <div className="flex flex-wrap justify-center gap-2">
              {Object.entries(LABEL_META).map(([k, m]) => (
                <Badge key={k} color={m.color}>{m.es}</Badge>
              ))}
            </div>
          </div>
        </Card>
      </section>
    );
  }

  const dist = labelDistribution(videos);
  const total = dist.reduce((s, d) => s + d.count, 0);
  const sincera = dist.find((d) => d.label === "manosfera_sincera")?.count ?? 0;
  const pctSincera = total ? Math.round((100 * sincera) / total) : 0;
  const byKw = labelByKeyword(videos).slice(0, 14);
  const labelKeys = Object.keys(LABEL_META);

  return (
    <section id="senal-ruido">
      <SectionTitle
        kicker="★ Señal vs Ruido"
        title={`Solo el ${pctSincera}% es manosfera sincera`}
        subtitle="De todo lo que matchea las keywords, esto es lo que realmente promueve el discurso vs. lo que lo critica, parodia, cubre periodísticamente o matchea por azar."
      />
      <div className="grid gap-5 lg:grid-cols-5">
        <Card className="p-5 lg:col-span-2">
          <div className="mb-3 text-sm font-semibold text-zinc-300">Composición del corpus</div>
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie data={dist} dataKey="count" nameKey="es" innerRadius={55} outerRadius={90} paddingAngle={2} stroke="none">
                {dist.map((d) => (
                  <Cell key={d.label} fill={d.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ background: "#0a0a0aee", border: "1px solid #3f3f46", borderRadius: 8, fontSize: 12 }}
                formatter={(value, _name, item) => {
                  const v = Number(value);
                  return [`${v} (${Math.round((100 * v) / total)}%)`, (item?.payload as { es?: string })?.es ?? ""];
                }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-3 space-y-1.5">
            {dist.map((d) => (
              <div key={d.label} className="flex items-center justify-between text-xs">
                <span className="inline-flex items-center gap-2 text-zinc-300">
                  <span className="h-2.5 w-2.5 rounded-sm" style={{ background: d.color }} />
                  {d.es}
                </span>
                <span className="tabular-nums text-zinc-500">{d.count} · {Math.round((100 * d.count) / total)}%</span>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-5 lg:col-span-3">
          <div className="mb-3 text-sm font-semibold text-zinc-300">Pureza por keyword <span className="font-normal text-zinc-500">— cuáles son limpias y cuáles puro ruido</span></div>
          <ResponsiveContainer width="100%" height={420}>
            <BarChart data={byKw} layout="vertical" margin={{ left: 10, right: 16, top: 4, bottom: 4 }} barCategoryGap={3}>
              <CartesianGrid horizontal={false} stroke="#27272a" />
              <XAxis type="number" stroke="#52525b" tick={{ fill: "#a1a1aa", fontSize: 11 }} />
              <YAxis type="category" dataKey="keyword" width={120} stroke="#52525b" tick={{ fill: "#d4d4d8", fontSize: 11 }} />
              <Tooltip
                cursor={{ fill: "#ffffff08" }}
                contentStyle={{ background: "#0a0a0aee", border: "1px solid #3f3f46", borderRadius: 8, fontSize: 12 }}
              />
              {labelKeys.map((k) => (
                <Bar key={k} dataKey={k} stackId="a" fill={LABEL_META[k].color} name={LABEL_META[k].es} />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>
    </section>
  );
}
