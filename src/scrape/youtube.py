"""YouTube scraper vía actor Apify streamers/youtube-scraper.

Uso:
    .venv/bin/python -m src.scrape.youtube                       # corre todas las keywords del config
    .venv/bin/python -m src.scrape.youtube --keyword "looksmaxxing"   # solo una keyword (smoke test)
    .venv/bin/python -m src.scrape.youtube --with-comments        # scrape videos + comentarios (2 pasadas)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.scrape._common import (
    filter_by_window,
    flat_keywords,
    get_client,
    load_config,
    save_run_output,
    window_unix,
)

ACTOR_VIDEOS = "streamers/youtube-scraper"
ACTOR_COMMENTS = "streamers/youtube-comments-scraper"

# Campos de timestamp en YouTube
TS_FIELDS = ["date", "uploadDate", "publishedTimeText", "publishDate"]


def run_search(client, keyword: str, limit: int, start_date: str, end_date: str) -> tuple[list[dict], dict]:
    """Búsqueda de videos por keyword con filtro de fecha."""
    run_input = {
        "searchQueries": [keyword],
        "maxResults": limit,
        # No usamos uploadDate filter — el actor no permite rangos custom, solo presets (hour/day/week/month/year)
        # que no alinean con nuestra ventana exacta. Confiamos en post-filtrado por campo 'date'.
    }
    run = client.actor(ACTOR_VIDEOS).call(run_input=run_input)
    dataset_id = run.default_dataset_id
    items = list(client.dataset(dataset_id).iterate_items())
    return items, {"actor": ACTOR_VIDEOS, "run_id": run.id, "dataset_id": dataset_id, "input": run_input}


def run_comments(client, video_urls: list[str], max_comments: int) -> tuple[list[dict], dict]:
    """Scrape comentarios de una lista de videos (requiere URLs completas)."""
    run_input = {
        "startUrls": [{"url": url} for url in video_urls],
        "maxComments": max_comments,
    }
    run = client.actor(ACTOR_COMMENTS).call(run_input=run_input)
    dataset_id = run.default_dataset_id
    items = list(client.dataset(dataset_id).iterate_items())
    return items, {"actor": ACTOR_COMMENTS, "run_id": run.id, "dataset_id": dataset_id, "input": run_input}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--keyword", help="Si se pasa, solo corre esta keyword (smoke test)")
    parser.add_argument("--limit", type=int, help="Override del límite de videos por keyword")
    parser.add_argument("--with-comments", action="store_true", help="Scrape comentarios de los videos capturados")
    parser.add_argument("--comments-limit", type=int, help="Límite de comentarios por video (default: config)")
    args = parser.parse_args()

    cfg = load_config()
    client = get_client()

    start_unix, end_unix = window_unix(cfg["window"]["start"], cfg["window"]["end"])
    limit = args.limit or cfg["limits"]["youtube_videos_per_keyword"]
    comments_limit = args.comments_limit or cfg["limits"]["youtube_comments_per_video"]

    if args.keyword:
        targets = [("smoke", args.keyword)]
    else:
        targets = flat_keywords(cfg)

    print(f"[youtube] {len(targets)} keyword(s), ventana {cfg['window']['start']} → {cfg['window']['end']}, limit {limit}/kw")

    all_video_urls = []

    # Fase 1: scrape videos
    for category, kw in targets:
        print(f"[youtube] · {category}/{kw}")
        items, meta = run_search(
            client, kw, limit, str(cfg["window"]["start"]), str(cfg["window"]["end"])
        )
        filtered = filter_by_window(items, start_unix, end_unix, TS_FIELDS)

        # Guardar URLs para comentarios (si --with-comments)
        if args.with_comments:
            for item in filtered:
                url = item.get("url") or item.get("link")
                if url:
                    all_video_urls.append(url)

        path = save_run_output(
            platform="youtube",
            label=f"videos__{category}__{kw}",
            items=filtered,
            extra={"category": category, "keyword": kw, "raw_count": len(items), **meta},
        )
        print(f"[youtube]   → {len(filtered)}/{len(items)} items en ventana · {path.name}")

    # Fase 2: scrape comentarios (si --with-comments)
    if args.with_comments and all_video_urls:
        print(f"\n[youtube] scraping comentarios de {len(all_video_urls)} videos (max {comments_limit}/video)")
        # Scrapeamos en batches de 50 videos para no saturar el actor
        batch_size = 50
        for i in range(0, len(all_video_urls), batch_size):
            batch = all_video_urls[i:i+batch_size]
            print(f"[youtube] · batch {i//batch_size + 1} ({len(batch)} videos)")
            items, meta = run_comments(client, batch, comments_limit)
            path = save_run_output(
                platform="youtube",
                label=f"comments__batch_{i//batch_size + 1}",
                items=items,
                extra={"video_count": len(batch), "max_comments_per_video": comments_limit, **meta},
            )
            print(f"[youtube]   → {len(items)} comentarios · {path.name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
