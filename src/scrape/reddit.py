"""Reddit scraper vía actor Apify trudax/reddit-scraper-lite.

Uso:
    .venv/bin/python -m src.scrape.reddit                            # todas las keywords + subreddits del config
    .venv/bin/python -m src.scrape.reddit --keyword "looksmaxxing"   # smoke test por keyword
    .venv/bin/python -m src.scrape.reddit --subreddit "MensRights"   # smoke test por subreddit
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.scrape._common import (
    flat_keywords,
    get_client,
    load_config,
    save_run_output,
)

ACTOR_ID = "trudax/reddit-scraper-lite"


def _filter_by_window(items: list[dict], start_unix: float, end_unix: float) -> list[dict]:
    """Reddit lite no filtra por fecha exacta; lo hacemos en post-procesamiento."""
    out = []
    for it in items:
        ts = it.get("createdAt") or it.get("created") or it.get("createdAtIso")
        epoch = None
        if isinstance(ts, (int, float)):
            epoch = float(ts)
        elif isinstance(ts, str):
            try:
                epoch = datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
            except ValueError:
                pass
        if epoch is None or start_unix <= epoch <= end_unix:
            out.append(it)
    return out


def run_search(client, query: str, max_posts: int, max_comments: int) -> tuple[list[dict], dict]:
    run_input = {
        "searches": [query],
        "type": "posts",
        "sort": "new",
        "time": "week",
        "maxItems": max_posts,
        "maxPostCount": max_posts,
        "maxComments": max_comments,
        "maxCommunitiesCount": 0,
        "maxUserCount": 0,
        "scrollTimeout": 40,
        "proxy": {"useApifyProxy": True},
    }
    run = client.actor(ACTOR_ID).call(run_input=run_input)
    dataset_id = run.default_dataset_id
    items = list(client.dataset(dataset_id).iterate_items())
    return items, {"actor": ACTOR_ID, "run_id": run.id, "dataset_id": dataset_id, "input": run_input}


def run_subreddit(client, subreddit: str, max_posts: int, max_comments: int) -> tuple[list[dict], dict]:
    run_input = {
        "startUrls": [{"url": f"https://www.reddit.com/r/{subreddit}/new/"}],
        "type": "posts",
        "sort": "new",
        "maxItems": max_posts,
        "maxPostCount": max_posts,
        "maxComments": max_comments,
        "maxCommunitiesCount": 0,
        "maxUserCount": 0,
        "scrollTimeout": 40,
        "proxy": {"useApifyProxy": True},
    }
    run = client.actor(ACTOR_ID).call(run_input=run_input)
    dataset_id = run.default_dataset_id
    items = list(client.dataset(dataset_id).iterate_items())
    return items, {"actor": ACTOR_ID, "run_id": run.id, "dataset_id": dataset_id, "input": run_input}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--keyword", help="Smoke test: solo esta keyword")
    parser.add_argument("--subreddit", help="Smoke test: solo este subreddit (sin r/)")
    parser.add_argument("--skip-keywords", action="store_true", help="No correr búsqueda por keyword")
    parser.add_argument("--skip-subreddits", action="store_true", help="No correr captura por subreddit")
    args = parser.parse_args()

    cfg = load_config()
    client = get_client()

    start = cfg["window"]["start"]
    end = cfg["window"]["end"]
    start_unix = datetime(start.year, start.month, start.day, tzinfo=timezone.utc).timestamp()
    end_unix = datetime(end.year, end.month, end.day, 23, 59, 59, tzinfo=timezone.utc).timestamp()

    max_kw_posts = cfg["limits"]["reddit_posts_per_keyword"]
    max_sub_posts = cfg["limits"]["reddit_posts_per_subreddit"]
    max_comments = cfg["limits"]["reddit_comments_per_post"]

    # --- modo smoke test ---
    if args.keyword:
        print(f"[reddit] smoke keyword: {args.keyword}")
        items, meta = run_search(client, args.keyword, max_kw_posts, max_comments)
        filtered = _filter_by_window(items, start_unix, end_unix)
        path = save_run_output("reddit", f"kw__{args.keyword}", filtered,
                               extra={"mode": "keyword", "keyword": args.keyword, "raw_count": len(items), **meta})
        print(f"[reddit]   → {len(filtered)}/{len(items)} items en ventana · {path.name}")
        return 0

    if args.subreddit:
        print(f"[reddit] smoke subreddit: r/{args.subreddit}")
        items, meta = run_subreddit(client, args.subreddit, max_sub_posts, max_comments)
        filtered = _filter_by_window(items, start_unix, end_unix)
        path = save_run_output("reddit", f"sub__{args.subreddit}", filtered,
                               extra={"mode": "subreddit", "subreddit": args.subreddit, "raw_count": len(items), **meta})
        print(f"[reddit]   → {len(filtered)}/{len(items)} items en ventana · {path.name}")
        return 0

    # --- modo barrido completo ---
    if not args.skip_keywords:
        kws = flat_keywords(cfg)
        print(f"[reddit] búsqueda por keyword: {len(kws)} queries")
        for category, kw in kws:
            print(f"[reddit] · {category}/{kw}")
            items, meta = run_search(client, kw, max_kw_posts, max_comments)
            filtered = _filter_by_window(items, start_unix, end_unix)
            path = save_run_output("reddit", f"kw__{category}__{kw}", filtered,
                                   extra={"mode": "keyword", "category": category, "keyword": kw,
                                          "raw_count": len(items), **meta})
            print(f"[reddit]   → {len(filtered)}/{len(items)} en ventana · {path.name}")

    if not args.skip_subreddits:
        subs = cfg["subreddits"]
        print(f"[reddit] captura por subreddit: {len(subs)} subs")
        for sub in subs:
            print(f"[reddit] · r/{sub}")
            items, meta = run_subreddit(client, sub, max_sub_posts, max_comments)
            filtered = _filter_by_window(items, start_unix, end_unix)
            path = save_run_output("reddit", f"sub__{sub}", filtered,
                                   extra={"mode": "subreddit", "subreddit": sub,
                                          "raw_count": len(items), **meta})
            print(f"[reddit]   → {len(filtered)}/{len(items)} en ventana · {path.name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
