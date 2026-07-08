"""Construye data/dashboard/validation.json para la sección "Validación" del dashboard.

Lee el xlsx de Fase 1 que Camino devolvió completado (doble anotación ciega) + la CLAVE con la
etiqueta del modelo, y resume el acuerdo:

  - κ de Cohen y % de acuerdo humano-humano (6 clases y binario sincera/no)
  - κ y acuerdo humano-modelo
  - consenso humano y aciertos del modelo sobre ese consenso
  - filas donde ambos humanos coinciden y el modelo difiere (errores claros)
  - videos que un anotador no pudo etiquetar por barrera de idioma / cuenta privada

Recordar el diseño: el set está cargado A PROPÓSITO a la frontera de baja confianza, así que estas
cifras son un PISO (el caso más difícil), no la accuracy del corpus. Ver §Validación en CLAUDE.md.

Uso: python -m src.analyze.build_validation_data
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
VDIR = ROOT / "data" / "processed" / "validacion_fase1"
XLSX = VDIR / "LIN_validacion_fase1_COMPLETADO.xlsx"
CLAVE = VDIR / "CLAVE_fase1.csv"
OUT = ROOT / "data" / "dashboard" / "validation.json"

# etiqueta amable (como aparece en el xlsx) -> clave canónica (como en lib/data.ts LABEL_META)
FRIENDLY_TO_KEY = {
    "manosfera sincera": "manosfera_sincera",
    "contra-crítica": "contra_critica",
    "sátira / humor": "satira_humor",
    "medio / periodismo": "medio_periodismo",
    "falso positivo": "falso_positivo",
    "ambiguo": "ambiguo",
}


def to_key(val: object) -> str | None:
    if not isinstance(val, str) or not val.strip():
        return None
    head = val.split("—")[0].strip().lower()
    return FRIENDLY_TO_KEY.get(head)


def cohen_kappa(pairs: list[tuple[str, str]]) -> tuple[float | None, float, int]:
    n = len(pairs)
    if n == 0:
        return None, 0.0, 0
    cats = sorted({c for p in pairs for c in p})
    po = sum(1 for a, b in pairs if a == b) / n
    px = {c: sum(1 for a, _ in pairs if a == c) / n for c in cats}
    py = {c: sum(1 for _, b in pairs if b == c) / n for c in cats}
    pe = sum(px[c] * py[c] for c in cats)
    k = (po - pe) / (1 - pe) if pe < 1 else 1.0
    return round(k, 3), round(po, 3), n


def main() -> int:
    clave = pd.read_csv(CLAVE)
    xls = pd.ExcelFile(XLSX)
    sheets = [s for s in xls.sheet_names if s.lower().startswith("etiquetado")]
    ann = [pd.read_excel(XLSX, sheet_name=s) for s in sheets]

    # alinear por orden de fila (# = 1..30, mismo orden en clave y en cada hoja)
    model = [k for k in clave["etiqueta_modelo"]]
    conf = list(clave["confianza"])
    ids = list(clave["#"])
    humans = [[to_key(v) for v in a["Tu etiqueta"]] for a in ann]

    # notas del primer anotador (barrera de idioma / cuenta privada)
    notes0 = [str(x) if isinstance(x, str) else "" for x in ann[0].get("Notas / dudas", [""] * len(ids))]
    lang_barrier = sum(1 for h, n in zip(humans[0], notes0) if h is None and "idioma" in n.lower())
    private = sum(1 for h, n in zip(humans[0], notes0) if h is None and "privad" in n.lower())

    def binize(k: str | None) -> str | None:
        return None if k is None else ("sincera" if k == "manosfera_sincera" else "no")

    # humano-humano (usa las dos primeras hojas)
    hh6 = [(a, b) for a, b in zip(humans[0], humans[1]) if a and b]
    hhb = [(binize(a), binize(b)) for a, b in zip(humans[0], humans[1]) if a and b]
    k_hh6, po_hh6, n_hh6 = cohen_kappa(hh6)
    k_hhb, po_hhb, _ = cohen_kappa(hhb)  # type: ignore[arg-type]

    # humano-modelo (por anotador)
    hm = []
    for i, h in enumerate(humans):
        pairs6 = [(x, m) for x, m in zip(h, model) if x]
        k6, po6, n6 = cohen_kappa(pairs6)
        hm.append({"annotator": i + 1, "kappa": k6, "agreement": po6, "n": n6})

    # consenso humano y aciertos del modelo
    both = [(i, humans[0][i], humans[1][i]) for i in range(len(ids)) if humans[0][i] and humans[1][i]]
    consensus = [(i, a) for i, a, b in both if a == b]
    model_hits = sum(1 for i, a in consensus if a == model[i])
    model_errors = [
        {"n": int(ids[i]), "conf": float(conf[i]), "model": model[i], "human": a}
        for i, a in consensus if a != model[i]
    ]

    def dist(labels: list[str | None]) -> dict[str, int]:
        out: dict[str, int] = {}
        for l in labels:
            if l:
                out[l] = out.get(l, 0) + 1
        return out

    data = {
        "n_videos": len(ids),
        "n_annotators": len(humans),
        "frontier_note": "muestra estratificada y cargada a la frontera de baja confianza (piso, no accuracy del corpus)",
        "annotator_labeled": [sum(1 for x in h if x) for h in humans],
        "lang_barrier": lang_barrier,
        "private": private,
        "human_human": {
            "kappa_6class": k_hh6, "agreement_6class": po_hh6, "n": n_hh6,
            "kappa_binary": k_hhb, "agreement_binary": po_hhb,
        },
        "human_model": hm,
        "consensus": {
            "n_both": len(both), "n_consensus": len(consensus),
            "model_hits": model_hits,
            "model_agreement": round(model_hits / len(consensus), 3) if consensus else None,
        },
        "model_errors": sorted(model_errors, key=lambda r: r["human"]),
        "dist_model": dist(model),
        "dist_annotators": [dist(h) for h in humans],
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[ok] {OUT.relative_to(ROOT)}")
    print(f"  humano-humano: κ={k_hh6} (6 clases) / {k_hhb} (binario) · acuerdo {po_hh6:.0%} / {po_hhb:.0%}")
    print(f"  humano-modelo: " + ", ".join(f"A{h['annotator']} κ={h['kappa']}" for h in hm))
    print(f"  consenso {len(consensus)}/{len(both)} · modelo acierta {model_hits} · errores claros {len(model_errors)}")
    print(f"  sin etiqueta por idioma: {lang_barrier} · cuenta privada: {private}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
