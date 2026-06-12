import { Meta, fmtNum } from "@/lib/data";
import { Stat } from "@/components/ui";

export function StatsBar({ meta }: { meta: Meta }) {
  const sinceras = meta.label_dist?.manosfera_sincera ?? 0;
  const pctSignal = meta.classified && meta.total_videos ? Math.round((100 * sinceras) / meta.total_videos) : null;
  return (
    <div
      className={`grid grid-cols-2 gap-6 rounded-xl border border-zinc-800 bg-[#131316] p-6 sm:grid-cols-3 ${
        pctSignal !== null ? "lg:grid-cols-6" : "lg:grid-cols-5"
      }`}
    >
      <Stat value={meta.total_videos.toLocaleString("es")} label="Videos capturados" />
      <Stat value={fmtNum(meta.total_plays)} label="Reproducciones totales" />
      <Stat value={`${meta.pct_latam}%`} label="LATAM" hint="de los geolocalizados" />
      <Stat value={meta.n_creators.toLocaleString("es")} label="Creadores únicos" />
      <Stat value="4 meses" label="Feb – May 2026" hint="TikTok · vía Apify" />
      {pctSignal !== null && (
        <Stat accent value={`${pctSignal}%`} label="Señal real" hint={`${sinceras} videos sinceros`} />
      )}
    </div>
  );
}
