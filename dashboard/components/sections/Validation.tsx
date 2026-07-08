import { ValidationData, LABEL_META } from "@/lib/data";
import { Card, SectionTitle, Stat, Callout, Badge } from "@/components/ui";

function LabelBadge({ k }: { k: string }) {
  const m = LABEL_META[k];
  return <Badge color={m?.color}>{m?.es ?? k}</Badge>;
}

export function Validation({ v }: { v: ValidationData }) {
  const pct = (x: number) => `${Math.round(x * 100)}%`;
  const k6 = v.human_human.kappa_6class?.toFixed(2) ?? "—";

  return (
    <section>
      <SectionTitle
        kicker="Validación · Fase 1"
        title="Dos personas etiquetaron a mano la frontera del modelo"
        subtitle={
          <>
            Camino anotó a ciegas una muestra de {v.n_videos} videos —estratificada y{" "}
            <strong className="text-zinc-300">cargada a propósito a los casos de menor confianza</strong>
            , donde el modelo más duda. Doble anotación para separar el error del modelo de la ambigüedad
            de la tarea. Estas cifras son el <strong className="text-zinc-300">caso más difícil</strong>, no
            la exactitud del corpus completo.
          </>
        }
      />

      <Card className="p-5 sm:p-6">
        <div className="mb-6 grid grid-cols-2 gap-5 sm:grid-cols-4">
          <Stat value={k6} label="acuerdo humano-humano" hint="κ de Cohen · 6 clases" />
          <Stat value={pct(v.human_human.agreement_binary)} label="acuerdo binario" hint="señal sincera vs. resto" />
          <Stat
            value={`${v.consensus.model_hits}/${v.consensus.n_consensus}`}
            label="modelo acierta en consenso"
            hint="donde ambos humanos coinciden"
            accent
          />
          <Stat value={v.n_videos.toString()} label={`videos · ${v.n_annotators} anotadores`} hint="frontera, baja confianza" />
        </div>

        <Callout>
          <strong className="text-zinc-100">La κ baja es el hallazgo, no un fracaso.</strong> Dos personas con
          las mismas instrucciones solo coinciden {pct(v.human_human.agreement_6class)}
          {" "}en la frontera → buena parte del &ldquo;error&rdquo; es <strong className="text-zinc-100">ambigüedad de la tarea, no del modelo</strong>.
          Fase 1 servía exactamente para separar esas dos cosas antes de escalar.
        </Callout>
      </Card>

      <div className="mt-5 grid gap-5 lg:grid-cols-[1fr_1fr]">
        <Card className="p-5 sm:p-6">
          <div className="mb-1 text-sm font-semibold text-zinc-200">Errores claros del modelo</div>
          <p className="mb-4 text-xs text-zinc-500">
            Casos donde <strong className="text-zinc-400">ambos humanos coincidieron</strong> y el modelo difirió
            ({v.model_errors.length} de {v.consensus.n_consensus} de consenso).
          </p>
          <div className="space-y-2.5">
            {v.model_errors.map((e) => (
              <div key={e.n} className="flex flex-wrap items-center gap-2 text-xs">
                <span className="w-8 shrink-0 tabular-nums text-zinc-600">#{e.n}</span>
                <LabelBadge k={e.model} />
                <span className="text-zinc-600">→</span>
                <LabelBadge k={e.human} />
                <span className="ml-auto tabular-nums text-zinc-600">conf. {e.conf.toFixed(2)}</span>
              </div>
            ))}
          </div>
          <p className="mt-4 border-t border-zinc-800 pt-3 text-xs leading-relaxed text-zinc-500">
            Dirección incipiente: en la frontera el modelo tiende a <strong className="text-zinc-400">sub-etiquetar
            &ldquo;sincera&rdquo;</strong> (la manda a contra-crítica o ambiguo). Si se confirma en Fase 2, el 35% sería
            un piso, no un techo. Con n={v.consensus.n_consensus} es señal, no medida.
          </p>
        </Card>

        <Card className="p-5 text-xs leading-relaxed text-zinc-500">
          <div className="mb-2 text-sm font-semibold text-zinc-300">Cómo leerlo</div>
          <ul className="list-inside list-disc space-y-1.5">
            <li>
              <strong className="text-zinc-400">Es el subconjunto más duro, no el corpus.</strong> Elegimos los
              videos de menor confianza; en el corpus completo (con los casos obvios) el acuerdo sería mucho mayor.
            </li>
            <li>
              <strong className="text-zinc-400">Sesgo entre anotadores:</strong>{" "}uno tiró a &ldquo;falso positivo&rdquo;
              ({v.dist_annotators[0]?.falso_positivo ?? 0}), el otro a &ldquo;manosfera sincera&rdquo;
              ({v.dist_annotators[1]?.manosfera_sincera ?? 0}) → el codebook necesita una pasada.
            </li>
            <li>
              <strong className="text-zinc-400">Barrera de idioma:</strong> {v.lang_barrier} videos no-hispanos
              (portugués/Brasil) quedaron sin anotar por un anotador — regla explícita pendiente para Fase 2.
            </li>
            <li>
              <strong className="text-zinc-400">n={v.n_videos} no da número reportable</strong> (IC ancho con 6 clases).
              Fase 2 (~100–150 videos) es para un κ estable y accuracy con margen.
            </li>
          </ul>
        </Card>
      </div>
    </section>
  );
}
