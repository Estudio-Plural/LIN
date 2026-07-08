import { Meta } from "@/lib/data";
import { SectionTitle, Card } from "@/components/ui";

export function Methodology({ meta }: { meta: Meta }) {
  return (
    <section>
      <SectionTitle
        kicker="Metodología"
        title="Cómo leer (y cómo no leer) estos datos"
        subtitle="La honestidad metodológica es parte del valor: decimos qué es señal y qué es artefacto."
      />
      <Card className="space-y-4 p-6 text-sm leading-relaxed text-zinc-400">
        <div>
          <div className="mb-2 font-semibold text-zinc-200">Captura</div>
          <p>
            {meta.total_videos.toLocaleString("es")} videos públicos de TikTok ({meta.period.start} → {meta.period.end}),
            vía scraper de Apify sobre 20 keywords del léxico manosfera. Devuelve texto, idioma, geolocalización a nivel país,
            métricas (plays, likes, comentarios, shares) y hashtags.
          </p>
        </div>
        <div>
          <div className="mb-2 font-semibold text-zinc-200">Limitaciones (importante)</div>
          <ul className="list-inside list-disc space-y-1.5">
            {meta.caveats.map((c, i) => (
              <li key={i}>{c}</li>
            ))}
            <li>
              Geografía: TikTok expone el país de creación de prácticamente todos los videos
              ({meta.geo_coverage ?? 100}% de cobertura). El {meta.pct_latam}% es de Latinoamérica
              —incluye Brasil; España queda fuera por europea—, no una cobertura parcial.
            </li>
            <li>
              Idioma vs. geografía: por lengua detectada solo ~{meta.pct_es_pt ?? "—"}% es español/portugués
              y ~{meta.pct_lang_undet ?? "—"}% queda sin determinar, así que el peso hispano por idioma es
              más conservador que por geografía.
            </li>
          </ul>
        </div>
        <div>
          <div className="mb-2 font-semibold text-zinc-200">Clasificación</div>
          <p>
            Cada video se etiqueta con <code className="text-zinc-300">gemini-2.5-flash</code> (manosfera sincera / contra-crítica /
            sátira / medio / falso positivo / ambiguo) para separar señal de ruido. Es una capa asistida por IA,
            auditable video por video en el explorador. La <strong className="text-zinc-300">validación humana está en
            curso</strong> (ver sección Validación): la Fase 1 anotó a mano la frontera de baja confianza; la Fase 2
            (~100–150 videos) dará un número reportable. Hasta entonces el 35% de “señal real” es una estimación del
            modelo, no una medición con margen de error.
          </p>
        </div>
        <p className="border-t border-zinc-800 pt-4 text-xs text-zinc-600">
          Piloto de escucha digital · Estudio Plural × Camino · datos generados {meta.generated_at}.
        </p>
      </Card>
    </section>
  );
}
