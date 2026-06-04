"""Clasifica los videos del barrido con gemini-2.5-flash vía OpenRouter.

Cada video -> {label, subtema, confianza, razon}. Cachea por id en
data/processed/classified.json (re-correr NO re-clasifica; es resumible). Batchea para
abaratar. Requiere OPENROUTER_API_KEY en .env.

Uso:
    .venv/bin/python -m src.analyze.classify
    .venv/bin/python -m src.analyze.classify --limit 30   # prueba chica
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import time
import urllib.request
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
PROCESSED = ROOT / "data" / "processed"
CACHE = PROCESSED / "classified.json"
MODEL = "google/gemini-2.5-flash"
BATCH = 15

SYSTEM = (
    "Sos analista de la manosfera/machosfera digital hispana. Clasificás videos de TikTok según su "
    "RELACIÓN con el discurso manosfera (hipergamia, 'hombre de alto valor', red pill, alfa, "
    "antifeminismo, looksmaxxing como ideología). Devolvés SOLO un array JSON, un objeto por video, "
    "en el mismo orden recibido, cada uno con: id, label, subtema, confianza (0-1), razon (<=12 palabras).\n"
    "labels: manosfera_sincera (promueve genuinamente esas ideas) | contra_critica (las critica/cuestiona, "
    "feminista/progresista/educativo) | satira_humor (parodia/comedia/ironía) | medio_periodismo (cobertura "
    "mediática del fenómeno) | falso_positivo (la keyword matcheó por azar, no es del tema) | ambiguo.\n"
    "subtema: hipergamia | alto_valor | red_pill | alfa | looksmax | antifeminismo | fitness | gaming | otro."
)


def load_videos(limit=None):
    seen, vids = set(), []
    for f in sorted(glob.glob(str(ROOT / "data/raw/tiktok/20260604T*"))):
        d = json.load(open(f))
        kw = (d.get("extra") or {}).get("keyword")
        for it in d.get("items", []):
            i = it.get("id")
            if not i or i in seen:
                continue
            seen.add(i)
            vids.append({
                "id": i, "kw": kw,
                "text": (it.get("text") or "")[:280],
                "hashtags": [h.get("name", "") for h in (it.get("hashtags") or []) if isinstance(h, dict)][:12],
            })
    return vids[:limit] if limit else vids


def parse_json_array(s: str):
    s = s.strip()
    if s.startswith("```"):
        s = s.split("```")[1]
        if s[:4].lower() == "json":
            s = s[4:]
    a, b = s.find("["), s.rfind("]")
    return json.loads(s[a:b + 1])


def call_openrouter(key: str, videos: list[dict]):
    payload = [{"id": v["id"], "keyword": v["kw"], "text": v["text"], "hashtags": v["hashtags"]} for v in videos]
    body = json.dumps({
        "model": MODEL,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": "Clasificá estos videos:\n" + json.dumps(payload, ensure_ascii=False)},
        ],
    }).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions", data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        resp = json.loads(r.read())
    return parse_json_array(resp["choices"][0]["message"]["content"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, help="Clasificar solo N (prueba)")
    args = ap.parse_args()

    load_dotenv(ROOT / ".env")
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        print("Falta OPENROUTER_API_KEY en .env. Pegalo y volvé a correr.", file=sys.stderr)
        return 1

    cache = json.load(open(CACHE)) if CACHE.exists() else {}
    vids = load_videos(args.limit)
    todo = [v for v in vids if v["id"] not in cache]
    print(f"[classify] {len(vids)} videos · {len(cache)} en caché · {len(todo)} por clasificar · modelo {MODEL}")

    for i in range(0, len(todo), BATCH):
        batch = todo[i:i + BATCH]
        res = None
        for attempt in (1, 2):
            try:
                res = call_openrouter(key, batch)
                break
            except Exception as e:
                print(f"  batch {i // BATCH}: error {e} (intento {attempt})", file=sys.stderr)
                time.sleep(5)
        if res is None:
            continue
        by_id = {str(r.get("id")): r for r in res if isinstance(r, dict)}
        for v in batch:
            r = by_id.get(str(v["id"]))
            if r:
                cache[v["id"]] = {"label": r.get("label"), "subtema": r.get("subtema"),
                                  "confianza": r.get("confianza"), "razon": r.get("razon")}
        json.dump(cache, open(CACHE, "w"), ensure_ascii=False, indent=1)
        print(f"  {min(i + BATCH, len(todo))}/{len(todo)} · cache {len(cache)}")

    print("[classify] distribución:", dict(Counter(v.get("label") for v in cache.values())))
    print(f"[classify] → {CACHE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
