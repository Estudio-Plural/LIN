"""Monitoreo de crecimiento — un snapshot de métricas de los posts recientes de creadores top.

Para cada handle, scrapea sus últimos N posts vía perfil (profileSorting=latest) y guarda
las métricas actuales (plays, likes, comments, shares, collects) con timestamp de captura.
Corriendo esto a diario, `src.monitor.build_curves` reconstruye la curva de crecimiento por
video. Solo da curvas reales para contenido JOVEN (los videos viejos ya están planos).

Uso:
    .venv/bin/python -m src.monitor.snapshot --handles growingmind.arg brightrsports
    .venv/bin/python -m src.monitor.snapshot --handles-file data/processed/monitor_handles.txt
    .venv/bin/python -m src.monitor.snapshot --handles-file ... --posts 8
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.scrape._common import get_client

ROOT = Path(__file__).resolve().parents[2]
MONITOR_DIR = ROOT / "data" / "raw" / "monitor"
ACTOR_ID = "clockworks/tiktok-scraper"

# Métricas que evolucionan en el tiempo (lo que diffeamos snapshot a snapshot)
METRIC_FIELDS = ["playCount", "diggCount", "commentCount", "shareCount", "collectCount"]


def run_snapshot(client, handles: list[str], posts_per_handle: int,
                 since_date: str | None = None) -> tuple[list[dict], dict]:
    run_input = {
        "profiles": handles,
        "resultsPerPage": posts_per_handle,
        "profileScrapeSections": ["videos"],
        "profileSorting": "latest",
        "shouldDownloadVideos": False,
        "shouldDownloadCovers": False,
        "shouldDownloadSlideshowImages": False,
        "shouldDownloadAvatars": False,
        "shouldDownloadMusicCovers": False,
    }
    if since_date:
        # Filtro absoluto del actor para perfiles: solo posts publicados desde esta fecha.
        # Más fiable que confiar en el orden de profileSorting=latest.
        run_input["oldestPostDateUnified"] = since_date
    run = client.actor(ACTOR_ID).call(run_input=run_input)
    items = list(client.dataset(run.default_dataset_id).iterate_items())
    cost = getattr(run, "usage_total_usd", None)
    if cost is None:
        try:
            cost = run.model_dump().get("usageTotalUsd")
        except Exception:
            cost = None
    return items, {"run_id": run.id, "dataset_id": run.default_dataset_id, "usd": cost}


def slim(it: dict, captured_at: str) -> dict:
    author = it.get("authorMeta") or {}
    return {
        "captured_at": captured_at,
        "id": it.get("id"),
        "author": author.get("name") if isinstance(author, dict) else None,
        "created_at": it.get("createTimeISO"),
        "url": it.get("webVideoUrl"),
        "text": (it.get("text") or "")[:200],
        **{m: it.get(m) or 0 for m in METRIC_FIELDS},
    }


def read_handles(args) -> list[str]:
    handles = list(args.handles or [])
    if args.handles_file:
        p = Path(args.handles_file)
        handles += [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines()
                    if ln.strip() and not ln.lstrip().startswith("#")]
    # dedupe preservando orden, sin @
    return [h for h in dict.fromkeys(x.lstrip("@") for x in handles)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--handles", nargs="*", help="Handles sueltos (sin @)")
    ap.add_argument("--handles-file", help="Archivo con un handle por línea (# = comentario)")
    ap.add_argument("--posts", type=int, default=30, help="Máx posts por handle / cap (default 30)")
    ap.add_argument("--since-days", type=int, default=14,
                    help="Solo posts de los últimos N días (oldestPostDateUnified). 0 = sin filtro de fecha.")
    args = ap.parse_args()

    handles = read_handles(args)
    if not handles:
        print("No hay handles. Pasá --handles o --handles-file.", file=sys.stderr)
        return 1

    since_date = None
    if args.since_days and args.since_days > 0:
        since_date = (datetime.now(timezone.utc) - timedelta(days=args.since_days)).strftime("%Y-%m-%d")

    client = get_client()
    captured_at = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    print(f"[snapshot] {len(handles)} handles · cap {args.posts}/handle · desde {since_date or 'sin filtro'} · {captured_at}")
    items, meta = run_snapshot(client, handles, args.posts, since_date)
    rows = [slim(it, captured_at) for it in items if it.get("id")]

    MONITOR_DIR.mkdir(parents=True, exist_ok=True)
    out = MONITOR_DIR / f"snapshot_{captured_at}.json"
    out.write_text(json.dumps({
        "captured_at": captured_at,
        "handles": handles,
        "posts_per_handle": args.posts,
        "since_date": since_date,
        "count": len(rows),
        "meta": meta,
        "items": rows,
    }, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    n_authors = len({r["author"] for r in rows if r["author"]})
    print(f"[snapshot]   → {len(rows)} videos de {n_authors} autores · costo≈${meta.get('usd')} · {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
