"""Arma el bundle de datos del dashboard.

Salida:
  - data/dashboard/videos.json  (array con los ~742 videos slim + clasificación si existe)
  - data/dashboard/meta.json    (totales + caveats de método)

El dashboard calcula agregados / filtros / switch de ruido client-side desde videos.json.

Uso: .venv/bin/python -m src.analyze.build_dashboard_data
"""
from __future__ import annotations

import glob
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "dashboard"
CLASSIFIED = ROOT / "data" / "processed" / "classified.json"
# Latinoamérica para el stat geográfico: incluye Brasil (lusófona, parte de la región),
# excluye España (europea). Decisión 2026-06-17 — el foco es la región, no la lengua.
LATAM = {"CO", "MX", "AR", "CL", "PE", "EC", "VE", "UY", "PY", "BO",
         "GT", "CR", "PA", "DO", "PR", "SV", "HN", "NI", "CU", "BR"}


def load_videos() -> list[dict]:
    seen, vids = set(), []
    for f in sorted(glob.glob(str(ROOT / "data/raw/tiktok/20260604T*"))):
        d = json.load(open(f))
        cat = (d.get("extra") or {}).get("category")
        kw = (d.get("extra") or {}).get("keyword")
        for it in d.get("items", []):
            i = it.get("id")
            if not i or i in seen:
                continue
            seen.add(i)
            a = it.get("authorMeta") or {}
            loc = it.get("locationCreated")
            vids.append({
                "id": i, "category": cat, "keyword": kw,
                "author": a.get("name"), "nick": a.get("nickName"), "fans": a.get("fans"),
                "created": (it.get("createTimeISO") or "")[:10],
                "month": (it.get("createTimeISO") or "")[:7],
                "plays": it.get("playCount") or 0, "likes": it.get("diggCount") or 0,
                "comments": it.get("commentCount") or 0, "shares": it.get("shareCount") or 0,
                "loc": loc, "is_latam": loc in LATAM, "lang": it.get("textLanguage"),
                "text": (it.get("text") or "").replace("\n", " ")[:200],
                "hashtags": [h.get("name", "").lower() for h in (it.get("hashtags") or []) if isinstance(h, dict)],
                "url": it.get("webVideoUrl"),
            })
    return vids


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    vids = load_videos()
    labels = json.load(open(CLASSIFIED)) if CLASSIFIED.exists() else {}
    for v in vids:
        lab = labels.get(v["id"]) or {}
        v["label"] = lab.get("label")
        v["subtema"] = lab.get("subtema")
        v["razon"] = lab.get("razon")
    json.dump(vids, open(OUT / "videos.json", "w"), ensure_ascii=False)

    geo = [v for v in vids if v["loc"]]
    es_pt = sum(1 for v in vids if v["lang"] in ("es", "pt"))
    undet = sum(1 for v in vids if not v["lang"] or v["lang"] == "un")
    meta = {
        "total_videos": len(vids),
        "period": {"start": "2026-02-01", "end": "2026-05-31"},
        "total_plays": sum(v["plays"] for v in vids),
        "n_creators": len({v["author"] for v in vids if v["author"]}),
        # pct_latam = share sobre TODOS los videos (la geo está al ~100%, no es una fracción)
        "pct_latam": round(100 * sum(1 for v in vids if v["is_latam"]) / len(vids)) if vids else None,
        "geo_coverage": round(100 * len(geo) / len(vids)) if vids else None,
        "pct_es_pt": round(100 * es_pt / len(vids)) if vids else None,
        "pct_lang_undet": round(100 * undet / len(vids)) if vids else None,
        "classified": bool(labels),
        "label_dist": dict(Counter(v["label"] for v in vids if v["label"])),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "caveats": [
            "El conteo por mes está sesgado por el scraping (sort LATEST sobre-muestrea lo reciente): no leer como crecimiento.",
            "El volumen de keywords sobreestima el fenómeno: incluye crítica, sátira, medios y falsos positivos.",
        ],
    }
    json.dump(meta, open(OUT / "meta.json", "w"), ensure_ascii=False, indent=1)
    print(f"[dashboard-data] {len(vids)} videos · clasificados={bool(labels)} · → {(OUT / 'videos.json').relative_to(ROOT)}")
    print("[dashboard-data] meta:", {k: meta[k] for k in ("total_videos", "total_plays", "pct_latam", "n_creators")})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
