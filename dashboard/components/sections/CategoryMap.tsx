"use client";
import {
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  CartesianGrid,
  Tooltip,
  Cell,
  LabelList,
} from "recharts";
import { aggregateByCategory, Video, fmtNum } from "@/lib/data";
import { Card, SectionTitle, Badge } from "@/components/ui";

function TooltipBox({ active, payload }: { active?: boolean; payload?: { payload: ReturnType<typeof aggregateByCategory>[number] }[] }) {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="rounded-lg border border-zinc-700 bg-zinc-950/95 px-3 py-2 text-xs shadow-xl">
      <div className="mb-1 font-semibold" style={{ color: d.color }}>{d.label}</div>
      <div className="text-zinc-300">{d.videos} videos · mediana {fmtNum(d.playsMedian)} plays</div>
      <div className="text-zinc-400">{d.pctLatam}% LATAM · {d.pctEsPt}% ES/PT</div>
    </div>
  );
}

export function CategoryMap({ videos }: { videos: Video[] }) {
  const data = aggregateByCategory(videos);
  return (
    <section>
      <SectionTitle
        kicker="Dónde vive la conversación"
        title="Lo emocional tracciona y es lo más hispano"
        subtitle="Cada burbuja es una categoría temática. Arriba-derecha = más viral y más LATAM. Lo emocional (hipergamia, crisis de masculinidad) domina las dos cosas — confirma la tesis del 'vacío emocional'. Lo estético y lo gamer pegan pero son anglos."
      />
      <Card className="p-5">
        <div className="mb-4 flex flex-wrap gap-2">
          {data.map((d) => (
            <Badge key={d.category} color={d.color}>{d.label} · {d.videos}</Badge>
          ))}
        </div>
        <ResponsiveContainer width="100%" height={380}>
          <ScatterChart margin={{ top: 20, right: 30, bottom: 30, left: 10 }}>
            <CartesianGrid stroke="#27272a" />
            <XAxis
              type="number" dataKey="pctLatam" name="% LATAM" domain={[0, 100]} unit="%"
              stroke="#52525b" tick={{ fill: "#a1a1aa", fontSize: 12 }}
              label={{ value: "% LATAM →", position: "insideBottom", offset: -12, fill: "#71717a", fontSize: 12 }}
            />
            <YAxis
              type="number" dataKey="playsMedian" name="plays mediana" scale="log" domain={[100, 100000]}
              stroke="#52525b" tick={{ fill: "#a1a1aa", fontSize: 12 }} tickFormatter={fmtNum}
              label={{ value: "↑ plays (mediana, log)", angle: -90, position: "insideLeft", fill: "#71717a", fontSize: 12 }}
            />
            <ZAxis type="number" dataKey="videos" range={[400, 2800]} />
            <Tooltip content={<TooltipBox />} cursor={{ strokeDasharray: "3 3", stroke: "#52525b" }} />
            <Scatter data={data}>
              {data.map((d) => (
                <Cell key={d.category} fill={d.color} fillOpacity={0.65} stroke={d.color} strokeWidth={1.5} />
              ))}
              <LabelList dataKey="label" position="top" style={{ fill: "#e4e4e7", fontSize: 12, fontWeight: 600 }} />
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </Card>
    </section>
  );
}
