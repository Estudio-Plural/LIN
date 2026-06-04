"use client";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell } from "recharts";
import { byCountry, Video } from "@/lib/data";
import { Card, SectionTitle, Callout } from "@/components/ui";

const NAMES: Record<string, string> = {
  US: "EE.UU.", MX: "México", GB: "Reino Unido", BR: "Brasil", AU: "Australia",
  ES: "España", CO: "Colombia", AR: "Argentina", CL: "Chile", DE: "Alemania",
  VN: "Vietnam", IT: "Italia", FR: "Francia", PH: "Filipinas", CA: "Canadá",
  PE: "Perú", EC: "Ecuador", VE: "Venezuela", ID: "Indonesia", NL: "P. Bajos",
};

export function Geography({ videos }: { videos: Video[] }) {
  const data = byCountry(videos, 12).map((d) => ({ ...d, name: NAMES[d.country] ?? d.country }));
  const co = videos.filter((v) => v.loc === "CO").length;
  return (
    <section>
      <SectionTitle
        kicker="Geografía"
        title="México manda; Colombia casi no produce"
        subtitle="País de creación del contenido (cuando TikTok lo expone). LATAM resaltado en rosa."
      />
      <Card className="p-5">
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={data} layout="vertical" margin={{ left: 10, right: 24, top: 4, bottom: 4 }}>
            <CartesianGrid horizontal={false} stroke="#27272a" />
            <XAxis type="number" stroke="#52525b" tick={{ fill: "#a1a1aa", fontSize: 12 }} />
            <YAxis type="category" dataKey="name" width={78} stroke="#52525b" tick={{ fill: "#d4d4d8", fontSize: 12 }} />
            <Tooltip
              cursor={{ fill: "#ffffff08" }}
              contentStyle={{ background: "#0a0a0aee", border: "1px solid #3f3f46", borderRadius: 8, fontSize: 12 }}
              labelStyle={{ color: "#fafafa" }}
            />
            <Bar dataKey="count" name="videos" radius={[0, 4, 4, 0]}>
              {data.map((d) => (
                <Cell key={d.country} fill={d.isLatam ? "#fb7185" : "#52525b"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        <Callout className="mt-4">
          Colombia aparece en solo <strong className="text-zinc-100">{co} videos</strong> ({Math.round((100 * co) / videos.length)}% del total).
          El contenido manosfera que llega al público colombiano es mayormente <strong className="text-zinc-100">pan-hispano y mexicano</strong>, no producido localmente.
        </Callout>
      </Card>
    </section>
  );
}
