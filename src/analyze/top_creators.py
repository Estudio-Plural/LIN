"""Ranking de creadores del barrido TikTok (4 meses) — insumo para #3 (recomendar cuentas
clave) y para elegir a quién monitorear en el job de crecimiento.

Lee data/raw/tiktok/*.json, dedup por video id, filtra a la ventana del config y agrupa por
autor. Salidas:
  - data/processed/top_creators.csv      (ranking completo, una fila por autor)
  - data/processed/monitor_handles.txt   (top-N handles activos → src.monitor.snapshot)

Uso:
    .venv/bin/python -m src.analyze.top_creators
    .venv/bin/python -m src.analyze.top_creators --top 20 --active-days 30
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.scrape._common import load_config

ROOT = Path(__file__).resolve().parents[2]
RAW_TT = ROOT / "data" / "raw" / "tiktok"
PROCESSED = ROOT / "data" / "processed"

# Hispanohablantes + Brasil (LATAM amplio) — consistente con report.py
LATAM_CODES = {"CO", "MX", "AR", "CL", "PE", "EC", "VE", "UY", "PY", "BO",
               "GT", "CR", "PA", "DO", "PR", "SV", "HN", "NI", "CU", "ES", "BR"}


def load_items() -> list[dict]:
    rows = []
    for f in sorted(RAW_TT.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        kw = (data.get("extra") or {}).get("keyword")
        for it in data.get("items", []):
            author = it.get("authorMeta") or {}
            rows.append({
                "id": it.get("id"),
                "author": author.get("name") if isinstance(author, dict) else None,
                "nick": author.get("nickName") if isinstance(author, dict) else None,
                "fans": author.get("fans") if isinstance(author, dict) else None,
                "created_at": it.get("createTimeISO"),
                "keyword": kw,
                "plays": it.get("playCount") or 0,
                "likes": it.get("diggCount") or 0,
                "comments": it.get("commentCount") or 0,
                "location": it.get("locationCreated"),
                "url": it.get("webVideoUrl"),
            })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=20, help="Cuántos handles escribir para el monitor (default 20)")
    ap.add_argument("--active-days", type=int, default=30,
                    help="Para monitorear, exigir post en los últimos N días del periodo (default 30)")
    args = ap.parse_args()

    cfg = load_config()
    w0 = pd.Timestamp(cfg["window"]["start"], tz="UTC")
    w1 = pd.Timestamp(cfg["window"]["end"], tz="UTC") + pd.Timedelta(hours=23, minutes=59, seconds=59)

    rows = load_items()
    if not rows:
        print("No hay items en data/raw/tiktok/.", file=sys.stderr)
        return 1

    df = pd.DataFrame(rows).dropna(subset=["id", "author"]).drop_duplicates(subset="id")
    df["created_at"] = pd.to_datetime(df["created_at"], utc=True, errors="coerce")
    in_win = df[(df["created_at"] >= w0) & (df["created_at"] <= w1)].copy()
    if in_win.empty:
        print("⚠️  ningún item cae en la ventana del config; uso todos.", file=sys.stderr)
        in_win = df.copy()
    df = in_win
    df["is_latam"] = df["location"].isin(LATAM_CODES)

    g = df.groupby("author")
    agg = g.agg(
        videos=("id", "count"),
        plays_total=("plays", "sum"),
        plays_median=("plays", "median"),
        likes_total=("likes", "sum"),
        keywords=("keyword", "nunique"),
        pct_latam=("is_latam", lambda s: round(100 * s.mean())),
        fans=("fans", "max"),
        first_post=("created_at", "min"),
        last_post=("created_at", "max"),
    ).reset_index()

    top_vid = (df.sort_values("plays", ascending=False)
                 .drop_duplicates("author")[["author", "url", "plays"]]
                 .rename(columns={"url": "top_url", "plays": "top_plays"}))
    agg = agg.merge(top_vid, on="author", how="left")
    kw_list = (g["keyword"].agg(lambda s: ", ".join(sorted({x for x in s if x})))
                 .reset_index().rename(columns={"keyword": "keyword_list"}))
    agg = agg.merge(kw_list, on="author", how="left")
    agg = agg.sort_values(["videos", "plays_total"], ascending=False)

    PROCESSED.mkdir(parents=True, exist_ok=True)
    out_csv = PROCESSED / "top_creators.csv"
    agg.to_csv(out_csv, index=False)

    # Para monitorear: activos (post reciente dentro del periodo), con varias apariciones y con
    # reach real (filtra spam de bajo engagement), priorizados por alcance total.
    cutoff = w1 - pd.Timedelta(days=args.active_days)
    cand = agg[(agg["last_post"] >= cutoff) & (agg["videos"] >= 2) & (agg["plays_median"] >= 500)]
    monitor = cand.sort_values("plays_total", ascending=False).head(args.top)
    handles_txt = PROCESSED / "monitor_handles.txt"
    header = [
        f"# Top {len(monitor)} creadores activos del barrido {cfg['window']['start']}→{cfg['window']['end']}",
        f"# (post en los últimos {args.active_days} días del periodo y >=2 videos). Editá a mano si querés.",
    ]
    handles_txt.write_text("\n".join(header + monitor["author"].tolist()) + "\n", encoding="utf-8")

    print(f"[top_creators] {len(agg)} autores · ventana {cfg['window']['start']}→{cfg['window']['end']} · {len(df)} videos únicos")
    print(f"[top_creators]   → {out_csv.relative_to(ROOT)}")
    print(f"[top_creators]   → {handles_txt.relative_to(ROOT)} ({len(monitor)} handles para monitorear)")
    print("\nTop 15 por # de videos en el periodo:")
    show = agg.head(15)[["author", "videos", "plays_total", "pct_latam", "keywords", "last_post"]].copy()
    show["last_post"] = show["last_post"].dt.date
    with pd.option_context("display.max_rows", None, "display.width", 180):
        print(show.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
