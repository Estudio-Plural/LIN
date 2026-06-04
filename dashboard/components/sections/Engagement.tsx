"use client";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell } from "recharts";
import { byKeywordEngagement, Video, fmtNum, CATEGORY_COLORS, CATEGORY_LABELS } from "@/lib/data";
import { Card, SectionTitle } from "@/components/ui";

export function Engagement({ videos }: { videos: Video[] }) {
  const data = byKeywordEngagement(videos).slice(0, 12);
  return (
    <section>
      <SectionTitle
        kicker="Engagement"
        title="Qué temas vuelan (y cuáles están saturados)"
        subtitle="Plays mediana por keyword — mide viralidad típica, no volumen. 'Hombre alfa' es alto volumen pero bajo alcance (saturado); 'hipergamia' y 'mewing' traccionan de verdad."
      />
      <Card className="p-5">
        <ResponsiveContainer width="100%" height={440}>
          <BarChart data={data} layout="vertical" margin={{ left: 10, right: 50, top: 4, bottom: 4 }}>
            <CartesianGrid horizontal={false} stroke="#27272a" />
            <XAxis
              type="number" stroke="#52525b" tick={{ fill: "#a1a1aa", fontSize: 12 }} tickFormatter={fmtNum}
            />
            <YAxis type="category" dataKey="keyword" width={130} stroke="#52525b" tick={{ fill: "#d4d4d8", fontSize: 12 }} />
            <Tooltip
              cursor={{ fill: "#ffffff08" }}
              contentStyle={{ background: "#0a0a0aee", border: "1px solid #3f3f46", borderRadius: 8, fontSize: 12 }}
              labelStyle={{ color: "#fafafa" }}
              formatter={(value, _name, item) => {
                const n = (item?.payload as { n?: number })?.n ?? 0;
                return [`${fmtNum(Number(value))} plays · ${n} videos`, "mediana"];
              }}
            />
            <Bar dataKey="playsMedian" radius={[0, 4, 4, 0]}>
              {data.map((d) => (
                <Cell key={d.keyword} fill={CATEGORY_COLORS[d.category] ?? "#52525b"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        <div className="mt-4 flex flex-wrap gap-3 text-xs text-zinc-500">
          {Object.entries(CATEGORY_LABELS).map(([k, v]) => (
            <span key={k} className="inline-flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full" style={{ background: CATEGORY_COLORS[k] }} />
              {v}
            </span>
          ))}
        </div>
      </Card>
    </section>
  );
}
