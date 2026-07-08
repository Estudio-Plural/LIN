"""Sondeo barato (punto (a) del correo de Camino, 2026-07-08): ¿el corpus manosfera ACTUAL ya pisa
ecosistemas adyacentes — apuestas, trading/cripto, emprendimiento, productividad?

Método (mismo rigor que el precedente fitness→manosfera "2/37 hashtags"): no se asume, se mide sobre
el corpus ya clasificado. Se busca cada léxico en texto + hashtags y se cuantifica el cruce **con la
manosfera sincera** (la señal real), no la mera presencia. Es un sondeo: mide adyacencia que los propios
creadores manosfera hacen aflorar; la ausencia en ESTE corpus (muestreado por keywords manosfera) NO
prueba ausencia en el fenómeno — eso lo decidiría el barrido (b) de esas keywords.

Uso:  python -m src.analyze.probe_adyacencias
"""
from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VIDEOS = ROOT / "data" / "dashboard" / "videos.json"
SINCERA = "manosfera_sincera"

# Léxicos normalizados (minúscula, sin acentos). Términos multi-palabra permitidos.
LEX = {
    "apuestas": ["apuesta", "apostar", "casino", "1xbet", "bet365", "betano", "betcris", "rushbet",
                 "codere", "tragamonedas", "ruleta", "quiniela", "pronostico deportivo", "aviator",
                 "tirada gratis", "bono de bienvenida"],
    "trading_cripto": ["trading", "trader", "cripto", "crypto", "bitcoin", "btc", "ethereum", "forex",
                        "binance", "invertir", "inversion", "day trading", "apalancamiento", "altcoin",
                        "memecoin", "hodl", "broker", "senales de trading"],
    "emprendimiento": ["emprender", "emprendimiento", "emprendedor", "negocio propio", "libertad financiera",
                        "side hustle", "hustle", "dropshipping", "ecommerce", "infoproducto", "marca personal",
                        "facturar", "cerrar ventas", "mentoria", "millonario", "hazte rico", "genera ingresos",
                        "ingresos pasivos"],
    "productividad": ["productividad", "disciplina", "monk mode", "sigma", "grindset", "mindset", "mentalidad",
                      "alto rendimiento", "5am", "despierta temprano", "dopamina", "mejora personal",
                      "desarrollo personal", "estoicismo", "estoico", "autodisciplina", "habitos"],
}


def norm(s: object) -> str:
    s = unicodedata.normalize("NFKD", str(s or "").lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def main() -> int:
    videos = json.loads(VIDEOS.read_text(encoding="utf-8"))
    pats = {eco: [(t, re.compile(r"(?<!\w)" + re.escape(t) + r"(?!\w)")) for t in terms]
            for eco, terms in LEX.items()}

    tot = len(videos)
    n_sincera = sum(1 for v in videos if v.get("label") == SINCERA)

    eco_all, eco_sincera = Counter(), Counter()
    terms_hit = defaultdict(Counter)
    creators = defaultdict(set)          # eco -> autores (cualquier label)
    bridge_creators = defaultdict(set)   # eco -> autores con el término EN un video sincera
    plays_bridge = defaultdict(int)
    examples = defaultdict(list)

    for v in videos:
        blob = norm(v.get("text", "")) + " " + " ".join(norm(h) for h in (v.get("hashtags") or []))
        matched = {eco: [t for t, p in ps if p.search(blob)] for eco, ps in pats.items()}
        for eco, ts in matched.items():
            if not ts:
                continue
            eco_all[eco] += 1
            creators[eco].add(v.get("author"))
            for t in ts:
                terms_hit[eco][t] += 1
            if v.get("label") == SINCERA:
                eco_sincera[eco] += 1
                bridge_creators[eco].add(v.get("author"))
                plays_bridge[eco] += int(v.get("plays") or 0)
                if len(examples[eco]) < 4:
                    examples[eco].append((v.get("author"), ts, (v.get("text") or "").strip()[:80]))

    print(f"Corpus clasificado: {tot} videos · manosfera_sincera: {n_sincera} ({n_sincera/tot:.0%})\n")
    print(f"{'ecosistema':16}{'corpus':>10}{'en sincera':>12}{'creadores':>11}{'puente*':>9}")
    for eco in LEX:
        print(f"{eco:16}{eco_all[eco]:>4} ({eco_all[eco]/tot:3.0%}){eco_sincera[eco]:>9}"
              f"{len(creators[eco]):>11}{len(bridge_creators[eco]):>9}")
    print("  *puente = creadores con un video manosfera_sincera que además usa el término\n")

    print("Términos que disparan cada match:")
    for eco in LEX:
        top = terms_hit[eco].most_common(10)
        print(f"  {eco:16} " + (", ".join(f"{t}×{c}" for t, c in top) if top else "— (sin señal)"))

    print("\nEjemplos del puente (autor · términos · texto):")
    for eco in LEX:
        if not examples[eco]:
            continue
        print(f"  [{eco}]")
        for a, ts, txt in examples[eco]:
            print(f"    @{a}: {ts} :: {txt}")

    out = {
        "corpus": tot, "manosfera_sincera": n_sincera,
        "ecosistemas": {eco: {
            "videos_corpus": eco_all[eco], "videos_sincera": eco_sincera[eco],
            "creadores": len(creators[eco]), "creadores_puente": len(bridge_creators[eco]),
            "plays_puente": plays_bridge[eco],
            "terminos": dict(terms_hit[eco].most_common(20)),
        } for eco in LEX},
    }
    dest = ROOT / "data" / "processed" / "adyacencias_sondeo.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[ok] resumen → {dest.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
