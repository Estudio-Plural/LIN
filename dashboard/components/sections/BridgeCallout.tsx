import { Video } from "@/lib/data";
import { SectionTitle, Card } from "@/components/ui";

const FIT = new Set(["gym", "gimnasio", "calistenia", "fitness", "workout", "gymtok", "gymrat", "calisthenics", "fit", "disciplina"]);
const MANO = new Set(["alfa", "alpha", "alphamale", "hombrealfa", "redpill", "red_pill", "pildoraroja", "hipergamia", "hypergamy", "sigma", "sigmamale", "masculinidad", "altovalor", "hombredealtovalor", "blackpill", "looksmaxxing", "mewing", "monkmode", "nofap"]);

export function BridgeCallout({ videos }: { videos: Video[] }) {
  const fit = videos.filter((v) => v.hashtags.some((h) => FIT.has(h)));
  const bridge = fit.filter((v) => v.hashtags.some((h) => MANO.has(h)));
  return (
    <section>
      <SectionTitle
        kicker="La hipótesis del puente"
        title="Fitness y manosfera casi no se cruzan en los hashtags"
        subtitle="El brief plantea que el algoritmo llevaría de calistenia/gym a contenido manosfera. En cómo etiquetan los creadores, ese cruce casi no aparece — lo que ni lo confirma ni lo descarta."
      />
      <Card className="grid gap-6 p-8 sm:grid-cols-[auto_1fr] sm:items-center">
        <div className="flex items-center gap-6">
          <div className="text-center">
            <div className="text-5xl font-bold text-zinc-100 tabular-nums">{fit.length}</div>
            <div className="mt-1 text-xs text-zinc-500">videos con<br />hashtag fitness</div>
          </div>
          <div className="text-3xl text-zinc-600">→</div>
          <div className="text-center">
            <div className="text-5xl font-bold text-red-500 tabular-nums">{bridge.length}</div>
            <div className="mt-1 text-xs text-zinc-500">también con<br />hashtag manosfera</div>
          </div>
        </div>
        <p className="text-sm leading-relaxed text-zinc-300">
          Solo <strong className="text-zinc-100">{bridge.length} de {fit.length}</strong> videos con hashtag fitness
          también etiquetan manosfera. Eso respalda una afirmación acotada: <strong className="text-zinc-100">el cruce no
          vive en cómo etiquetan los creadores</strong>. No prueba que el algoritmo sea el puente — la co-ocurrencia de
          hashtags no observa el feed, así que con estos datos la hipótesis del brief no se confirma ni se refuta.
          En la red, además, <strong className="text-zinc-100">&ldquo;fitness/gymcel&rdquo; forma su propia comunidad</strong>,
          separada del núcleo ideológico de &ldquo;alto valor&rdquo;. Resolverlo pide otro instrumento: un{" "}
          <strong className="text-zinc-100">experimento de exposición</strong> con cuentas-títere controladas que registren
          qué empuja el For You.
        </p>
      </Card>
    </section>
  );
}
