"use client";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceArea,
} from "recharts";
import { GrowthData, fmtNum } from "@/lib/data";
import { Card, SectionTitle, Stat, Callout } from "@/components/ui";

export function GrowthCurve({ growth }: { growth: GrowthData }) {
  const data = growth.velocity_by_age.filter((d) => d.age <= 10);
  const peak = growth.peak_before_2d;
  const top = growth.creators[0];
  const maxNew = growth.creators[0]?.new_plays || 1;

  return (
    <section>
      <SectionTitle
        kicker="Monitor de crecimiento"
        title="La curva de vida: el alcance se decide en las primeras 72 horas"
        subtitle={
          <>
            El barrido es una foto; esto es la película. Seguimos a diario videos frescos de creadores
            manosfera curados y medimos cuánto crecen según su edad. {growth.n_snapshots} mediciones diarias
            ({growth.window.start} → {growth.window.end}), {growth.n_videos} videos.
          </>
        }
      />

      <Card className="p-5 sm:p-6">
        <div className="mb-6 grid grid-cols-2 gap-5 sm:grid-cols-4">
          <Stat value={`${peak.pct}%`} label="pican antes de 48h" hint={`${peak.count} de ${peak.total} videos`} accent />
          <Stat value="~72h" label="ventana de crecimiento" hint="luego se desploma" />
          <Stat value={fmtNum(growth.total_new_plays)} label="plays nuevos" hint="en la ventana medida" />
          <Stat value={growth.n_snapshots.toString()} label="mediciones diarias" hint="monitor activo" />
        </div>

        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={data} margin={{ left: 6, right: 16, top: 8, bottom: 4 }}>
            <defs>
              <linearGradient id="velFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#ef4444" stopOpacity={0.5} />
                <stop offset="100%" stopColor="#ef4444" stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="#27272a" vertical={false} />
            {/* Ventana caliente: primeros ~3 días antes del colapso */}
            <ReferenceArea x1={0} x2={3} fill="#ef4444" fillOpacity={0.06} />
            <XAxis
              dataKey="age"
              type="number"
              domain={[0, 10]}
              stroke="#52525b"
              tick={{ fill: "#a1a1aa", fontSize: 12 }}
              tickFormatter={(d) => `${d}d`}
              label={{ value: "edad del video (días)", position: "insideBottom", offset: -2, fill: "#71717a", fontSize: 11 }}
            />
            <YAxis stroke="#52525b" tick={{ fill: "#a1a1aa", fontSize: 12 }} tickFormatter={fmtNum} width={44} />
            <Tooltip
              cursor={{ stroke: "#52525b", strokeDasharray: 3 }}
              contentStyle={{ background: "#0a0a0aee", border: "1px solid #3f3f46", borderRadius: 8, fontSize: 12 }}
              labelStyle={{ color: "#fafafa" }}
              labelFormatter={(d) => `Día ${d} de vida`}
              formatter={(value, _n, item) => {
                const n = (item?.payload as { n?: number })?.n ?? 0;
                return [`${fmtNum(Number(value))} plays/día · ${n} mediciones`, "velocidad media"];
              }}
            />
            <Area
              type="monotone"
              dataKey="plays_per_day"
              stroke="#ef4444"
              strokeWidth={2}
              fill="url(#velFill)"
              dot={{ r: 2.5, fill: "#ef4444" }}
            />
          </AreaChart>
        </ResponsiveContainer>
        <p className="mt-2 text-xs text-zinc-500">
          Velocidad media de plays por día, según la edad del video. Casi plana los primeros 3 días
          (~20k plays/día) y luego cae en picado: pasado el día 3–4 los videos viven de una cola larga
          de pocos miles diarios.
        </p>
      </Card>

      <div className="mt-5 grid gap-5 lg:grid-cols-[1.1fr_1fr]">
        <Card className="p-5 sm:p-6">
          <div className="mb-4 text-sm font-semibold text-zinc-200">Quién aporta el crecimiento</div>
          <div className="space-y-2.5">
            {growth.creators.slice(0, 8).map((c) => (
              <div key={c.author} className="flex items-center gap-3 text-xs">
                <span className="w-36 shrink-0 truncate text-zinc-400">@{c.author}</span>
                <div className="h-2 flex-1 overflow-hidden rounded-full bg-zinc-800">
                  <div
                    className="h-full rounded-full bg-red-500/80"
                    style={{ width: `${Math.max(1.5, (100 * c.new_plays) / maxNew)}%` }}
                  />
                </div>
                <span className="w-20 shrink-0 text-right tabular-nums text-zinc-300">
                  +{fmtNum(c.new_plays)}
                </span>
                <span className="w-10 shrink-0 text-right tabular-nums text-zinc-500">{c.share_new}%</span>
              </div>
            ))}
          </div>
        </Card>

        <div className="space-y-4">
          <Callout>
            <strong className="text-zinc-100">Un outlier domina la cohorte.</strong> @{top?.author} concentra
            el <strong className="text-zinc-100">{growth.top_creator_share}%</strong> de los plays nuevos de la
            ventana. No es crecimiento parejo de “la manosfera”: es un puñado de videos virales tirando del agregado.
          </Callout>
          <Card className="p-5 text-xs leading-relaxed text-zinc-500">
            <div className="mb-2 font-semibold text-zinc-300">Cómo leerlo</div>
            <ul className="list-inside list-disc space-y-1.5">
              <li>
                Ventana corta ({growth.n_snapshots} días): las edades altas se observan solo en su cola
                —no vimos la juventud de los videos viejos—, así que la curva es más firme en los primeros días.
              </li>
              <li>Solo creadores curados (sinceros/ambiguos, hispanos): mide la dinámica del fenómeno, no su tamaño total.</li>
              <li>El monitor sigue corriendo a diario: la curva se afina con cada snapshot.</li>
            </ul>
          </Card>
        </div>
      </div>
    </section>
  );
}
