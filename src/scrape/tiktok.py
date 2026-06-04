"""TikTok scraper vía actor Apify clockworks/tiktok-scraper.

Uso:
    .venv/bin/python -m src.scrape.tiktok                       # corre todas las keywords del config
    .venv/bin/python -m src.scrape.tiktok --keyword "looksmaxxing"   # solo una keyword (smoke test)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Permitir correr como script o como módulo
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.scrape._common import (
    filter_by_window,
    flat_keywords,
    get_client,
    load_config,
    save_run_output,
    window_unix,
)

ACTOR_ID = "clockworks/tiktok-scraper"

# Campos donde TikTok suele exponer el timestamp del post
TS_FIELDS = ["createTimeISO", "createTime", "createdAt", "createdAtISO"]


def run_one(client, keyword: str, limit: int, date_filter: str, sorting: str) -> tuple[list[dict], dict]:
    run_input = {
        "searchQueries": [keyword],
        "resultsPerPage": limit,
        "searchSection": "/video",
        "videoSearchDateFilter": date_filter,
        "videoSearchSorting": sorting,
        "shouldDownloadVideos": False,
        "shouldDownloadCovers": False,
        "shouldDownloadSlideshowImages": False,
        "shouldDownloadAvatars": False,
        "shouldDownloadMusicCovers": False,
    }
    run = client.actor(ACTOR_ID).call(run_input=run_input)
    dataset_id = run.default_dataset_id
    items = list(client.dataset(dataset_id).iterate_items())
    return items, {"actor": ACTOR_ID, "run_id": run.id, "dataset_id": dataset_id, "input": run_input}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--keyword", help="Si se pasa, solo corre esta keyword (smoke test)")
    parser.add_argument("--limit", type=int, help="Override del límite de posts por keyword")
    args = parser.parse_args()

    cfg = load_config()
    client = get_client()

    start_unix, end_unix = window_unix(cfg["window"]["start"], cfg["window"]["end"])
    limit = args.limit or cfg["limits"]["tiktok_posts_per_keyword"]

    tk = cfg.get("tiktok", {})
    date_filter = tk.get("search_date_filter", "PAST_WEEK")
    sorting = tk.get("search_sorting", "MOST_RELEVANT")

    if args.keyword:
        targets = [("smoke", args.keyword)]
    else:
        targets = flat_keywords(cfg)

    print(f"[tiktok] {len(targets)} keyword(s), ventana {cfg['window']['start']} → {cfg['window']['end']}, filtro {date_filter}/{sorting}, limit {limit}/kw")

    for category, kw in targets:
        print(f"[tiktok] · {category}/{kw}")
        items, meta = run_one(client, kw, limit, date_filter, sorting)
        filtered = filter_by_window(items, start_unix, end_unix, TS_FIELDS)
        path = save_run_output(
            platform="tiktok",
            label=f"{category}__{kw}",
            items=filtered,
            extra={"category": category, "keyword": kw, "raw_count": len(items), **meta},
        )
        print(f"[tiktok]   → {len(filtered)}/{len(items)} items en ventana · {path.name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
