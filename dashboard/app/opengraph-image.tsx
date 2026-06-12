import { ImageResponse } from "next/og";
import meta from "@/public/data/meta.json";
import { fmtNum } from "@/lib/data";

export const alt = "Radiografía de la manosfera hispana — piloto de escucha digital Estudio Plural × Camino";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

function Stat({ value, label, accent = false }: { value: string; label: string; accent?: boolean }) {
  return (
    <div style={{ display: "flex", flexDirection: "column" }}>
      <div style={{ fontSize: 64, fontWeight: 700, color: accent ? "#ef4444" : "#fafafa", lineHeight: 1.1 }}>
        {value}
      </div>
      <div style={{ fontSize: 22, color: "#a1a1aa", marginTop: 6 }}>{label}</div>
    </div>
  );
}

export default function Image() {
  const sinceras = meta.label_dist?.manosfera_sincera ?? 0;
  const pct = Math.round((100 * sinceras) / meta.total_videos);
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: "72px 80px",
          backgroundColor: "#09090b",
          backgroundImage: "linear-gradient(180deg, rgba(127,29,29,0.30) 0%, rgba(9,9,11,0) 45%)",
        }}
      >
        <div style={{ display: "flex", flexDirection: "column" }}>
          <div
            style={{
              fontSize: 21,
              fontWeight: 600,
              color: "#ef4444",
              textTransform: "uppercase",
              letterSpacing: 5,
            }}
          >
            Piloto de escucha digital · Estudio Plural × Camino
          </div>
          <div
            style={{
              marginTop: 30,
              maxWidth: 950,
              fontSize: 78,
              fontWeight: 800,
              color: "#fafafa",
              lineHeight: 1.05,
              letterSpacing: -2,
            }}
          >
            Radiografía de la manosfera hispana
          </div>
        </div>
        <div style={{ display: "flex", gap: 90, alignItems: "flex-end" }}>
          <Stat value={meta.total_videos.toLocaleString("es")} label="videos analizados" />
          <Stat value={fmtNum(meta.total_plays)} label="reproducciones" />
          <Stat value={`${pct}%`} label="señal real" accent />
        </div>
      </div>
    ),
    { ...size }
  );
}
