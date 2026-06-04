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
        kicker="El puente invisible"
        title="La ruta fitness → manosfera no está en los hashtags"
        subtitle="La hipótesis del brief: el algoritmo lleva de calistenia/gym a contenido manosfera extremo. Pero los creadores no lo declaran."
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
          Solo <strong className="text-zinc-100">{bridge.length} de {fit.length}</strong> videos fitness co-etiquetan manosfera.
          Si el pipeline de radicalización existe, <strong className="text-zinc-100">vive en el feed, no en los hashtags</strong> — es el
          algoritmo el que conecta calistenia con &ldquo;alto valor&rdquo; y red pill, no los creadores.
          Por eso medirlo no se puede con scraping de keywords: requiere un <strong className="text-zinc-100">experimento de exposición</strong>
          {" "}(cuentas-títere controladas que registren qué les empuja el For You).
        </p>
      </Card>
    </section>
  );
}
