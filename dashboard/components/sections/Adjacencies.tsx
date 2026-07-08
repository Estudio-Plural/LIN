import { AdjacencyData, ECO_LABELS, fmtNum } from "@/lib/data";
import { Card, SectionTitle, Callout } from "@/components/ui";

export function Adjacencies({ a }: { a: AdjacencyData }) {
  const order = ["productividad", "emprendimiento", "trading_cripto", "apuestas"];
  const prod = a.ecosistemas["productividad"];
  const terms = Object.entries(prod?.terminos ?? {}).slice(0, 8);
  const maxTerm = terms.length ? terms[0][1] : 1;

  return (
    <section>
      <SectionTitle
        kicker="Ecosistemas adyacentes"
        title="El único puente vivo es productividad / mentalidad"
        subtitle={
          <>
            ¿Los creadores del corpus ya pisan apuestas, trading/cripto, emprendimiento o productividad? Se
            <strong className="text-zinc-300"> mide sobre los {a.corpus} videos clasificados</strong>, no se asume
            (mismo rigor que el puente fitness). Cuenta el cruce con la manosfera sincera, no la mera presencia.
          </>
        }
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {order.map((k) => {
          const e = a.ecosistemas[k];
          const live = (e?.videos_corpus ?? 0) > 0;
          return (
            <Card key={k} className={`p-5 ${live ? "border-red-500/30" : ""}`}>
              <div className="text-xs font-medium text-zinc-400">{ECO_LABELS[k] ?? k}</div>
              <div className={`mt-2 text-4xl font-bold tabular-nums ${live ? "text-red-500" : "text-zinc-700"}`}>
                {e?.videos_corpus ?? 0}
              </div>
              <div className="mt-1 text-xs text-zinc-500">
                {live ? (
                  <>
                    videos ({Math.round((100 * (e.videos_corpus ?? 0)) / a.corpus)}% del corpus)
                    <br />
                    {e.videos_sincera} en manosfera sincera · {e.creadores_puente} creadores puente
                  </>
                ) : (
                  "sin señal en el corpus"
                )}
              </div>
            </Card>
          );
        })}
      </div>

      <div className="mt-5 grid gap-5 lg:grid-cols-[1fr_1fr]">
        <Card className="p-5 sm:p-6">
          <div className="mb-4 text-sm font-semibold text-zinc-200">Qué dispara el puente de productividad</div>
          <div className="space-y-2.5">
            {terms.map(([t, c]) => (
              <div key={t} className="flex items-center gap-3 text-xs">
                <span className="w-28 shrink-0 truncate text-zinc-400">{t}</span>
                <div className="h-2 flex-1 overflow-hidden rounded-full bg-zinc-800">
                  <div className="h-full rounded-full bg-red-500/80" style={{ width: `${Math.max(4, (100 * c) / maxTerm)}%` }} />
                </div>
                <span className="w-8 shrink-0 text-right tabular-nums text-zinc-300">{c}</span>
              </div>
            ))}
          </div>
          <p className="mt-4 border-t border-zinc-800 pt-3 text-xs text-zinc-500">
            {prod?.videos_sincera} videos de manosfera sincera usan lenguaje de disciplina/mentalidad
            (~{fmtNum(prod?.plays_puente ?? 0)}
            {" "}plays). Es el brazo &ldquo;superación personal&rdquo; del fenómeno,
            no un ecosistema aparte.
          </p>
        </Card>

        <div className="space-y-4">
          <Callout>
            <strong className="text-zinc-100">Apuestas, trading/cripto y emprendimiento dan cero.</strong>{" "}
            Verificado con raíces amplias (negocio, cripto, bitcoin, trading, apuesta, casino, hustle…): no están
            en los datos. Pero el corpus se muestreó <strong className="text-zinc-100">por keywords de manosfera</strong>,
            así que solo revela lo que estos creadores hacen aflorar — no prueba ausencia del fenómeno.
          </Callout>
          <Card className="p-5 text-xs leading-relaxed text-zinc-500">
            <div className="mb-2 font-semibold text-zinc-300">Decisión sobre el barrido específico</div>
            <p>
              Productividad ya está <strong className="text-zinc-400">dentro</strong>, no hace falta barrido. Para
              apuestas/trading/emprendimiento, el sondeo dice &ldquo;no aflora solo&rdquo; → si interesa esa hipótesis,
              tiene sentido un barrido acotado de esas keywords para testearla con datos; si no, no se gasta alcance.
            </p>
          </Card>
        </div>
      </div>
    </section>
  );
}
