"""Genera un reporte ejecutivo del barrido LIN.

Uso:
    .venv/bin/python -m src.analyze.report

Lee todos los JSON en data/raw/{tiktok,reddit}/, calcula métricas y produce:
  - data/processed/tiktok_posts.csv  (un row por post)
  - data/processed/reddit_items.csv  (un row por post/comment)
  - data/processed/report.md         (resumen ejecutivo para correo a Laura)
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.scrape._common import get_client

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

# Códigos ISO de países hispanohablantes (incluye España y Brasil para LATAM amplio)
LATAM_CODES = {"CO", "MX", "AR", "CL", "PE", "EC", "VE", "UY", "PY", "BO",
               "GT", "CR", "PA", "DO", "PR", "SV", "HN", "NI", "CU", "ES", "BR"}
LATAM_LANGS = {"es", "pt"}


def load_runs(platform: str) -> list[dict]:
    files = sorted((RAW / platform).glob("*.json"))
    out = []
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            data["_file"] = f.name
            out.append(data)
        except json.JSONDecodeError:
            print(f"  ⚠️  skipping malformed: {f.name}", file=sys.stderr)
    return out


def flatten_tiktok(runs: list[dict]) -> pd.DataFrame:
    rows = []
    for run in runs:
        extra = run.get("extra", {})
        category = extra.get("category", "?")
        keyword = extra.get("keyword", "?")
        for it in run.get("items", []):
            author = it.get("authorMeta") or {}
            loc = it.get("locationCreated")
            rows.append({
                "category": category,
                "keyword": keyword,
                "id": it.get("id"),
                "created_at": it.get("createTimeISO"),
                "url": it.get("webVideoUrl"),
                "author": author.get("name") if isinstance(author, dict) else None,
                "author_verified": author.get("verified") if isinstance(author, dict) else None,
                "text": it.get("text"),
                "language": it.get("textLanguage"),
                "location": loc,
                "is_latam": (loc in LATAM_CODES) if loc else None,
                "is_hispanic_lang": (it.get("textLanguage") in LATAM_LANGS),
                "plays": it.get("playCount") or 0,
                "likes": it.get("diggCount") or 0,
                "shares": it.get("shareCount") or 0,
                "comments": it.get("commentCount") or 0,
                "collects": it.get("collectCount") or 0,
                "hashtags": ", ".join(h.get("name", "") for h in (it.get("hashtags") or []) if isinstance(h, dict)),
                "is_ad": it.get("isAd"),
                "is_sponsored": it.get("isSponsored"),
            })
    return pd.DataFrame(rows)


def flatten_reddit(runs: list[dict]) -> pd.DataFrame:
    rows = []
    for run in runs:
        extra = run.get("extra", {})
        mode = extra.get("mode", "?")
        keyword = extra.get("keyword")
        subreddit_in = extra.get("subreddit")
        for it in run.get("items", []):
            dtype = it.get("dataType") or "?"
            community = (it.get("parsedCommunityName")
                         or it.get("category")
                         or (it.get("communityName") or "").lstrip("r/")
                         or None)
            rows.append({
                "mode": mode,
                "keyword": keyword,
                "subreddit_input": subreddit_in,
                "type": dtype,
                "id": it.get("id"),
                "created_at": it.get("createdAt"),
                "community": community,
                "username": it.get("username"),
                "title": it.get("title"),
                "body": (it.get("body") or "")[:500],
                "url": it.get("url"),
                "upvotes": it.get("upVotes") or 0,
                "upvote_ratio": it.get("upVoteRatio"),
                "n_comments": it.get("numberOfComments"),
                "n_replies": it.get("numberOfreplies"),
                "flair": it.get("flair"),
                "over18": it.get("over18"),
                "is_video": it.get("isVideo"),
            })
    return pd.DataFrame(rows)


def get_actor_runs_cost() -> tuple[float, int]:
    """Consulta Apify API por costo total de runs hoy."""
    try:
        c = get_client()
        runs = list(c.runs().list(limit=200).items)
        today = datetime.now(timezone.utc).date()
        total = 0.0
        count = 0
        for r in runs:
            started = getattr(r, "started_at", None)
            if started and started.date() == today:
                cost = getattr(r, "usage_total_usd", None) or 0
                total += float(cost)
                count += 1
        return total, count
    except Exception as e:
        return -1.0, 0


def build_report(tk: pd.DataFrame, rd: pd.DataFrame, cost: float, n_runs: int) -> str:
    lines = []
    lines.append("# LIN — Barrido exploratorio · reporte")
    lines.append(f"\n_Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}_\n")

    lines.append("## Resumen")
    lines.append("")
    lines.append("| Plataforma | Keywords corridas | Items capturados | Costo runs hoy |")
    lines.append("|---|---|---|---|")
    n_tk_kw = tk["keyword"].nunique() if not tk.empty else 0
    n_rd_kw = rd["keyword"].dropna().nunique() if not rd.empty else 0
    cost_str = f"${cost:.2f}" if cost >= 0 else "(error consulta)"
    lines.append(f"| TikTok | {n_tk_kw} | {len(tk):,} | — |")
    lines.append(f"| Reddit | {n_rd_kw} | {len(rd):,} | — |")
    lines.append(f"| **Total** | — | {len(tk)+len(rd):,} | **{cost_str}** ({n_runs} runs) |")
    lines.append("")

    # ===== TikTok =====
    if not tk.empty:
        lines.append("## TikTok\n")
        # Volumen por keyword
        vol = (tk.groupby(["category", "keyword"])
                 .agg(items=("id", "count"),
                      plays_total=("plays", "sum"),
                      plays_median=("plays", "median"),
                      likes_total=("likes", "sum"),
                      pct_latam_geo=("is_latam", lambda s: 100 * s.fillna(False).mean()),
                      pct_es_pt=("is_hispanic_lang", lambda s: 100 * s.mean()))
                 .reset_index()
                 .sort_values("items", ascending=False))
        lines.append("### Volumen por keyword\n")
        lines.append("| Categoría | Keyword | Items | Plays totales | Plays mediana | % geo LATAM | % idioma ES/PT |")
        lines.append("|---|---|---:|---:|---:|---:|---:|")
        for _, r in vol.iterrows():
            lines.append(f"| {r['category']} | {r['keyword']} | {int(r['items'])} | "
                         f"{int(r['plays_total']):,} | {int(r['plays_median']):,} | "
                         f"{r['pct_latam_geo']:.0f}% | {r['pct_es_pt']:.0f}% |")
        lines.append("")

        # Geo top
        geo = tk["location"].dropna().value_counts().head(10)
        lines.append("### Distribución geográfica (top 10)\n")
        lines.append("| País | Posts | % |")
        lines.append("|---|---:|---:|")
        total_with_geo = int(tk["location"].notna().sum())
        for country, n in geo.items():
            pct = 100 * n / total_with_geo if total_with_geo else 0
            mark = " 🌎" if country in LATAM_CODES else ""
            lines.append(f"| {country}{mark} | {n} | {pct:.0f}% |")
        n_latam = int(tk["is_latam"].fillna(False).sum())
        lines.append(f"\n**Total LATAM (geo):** {n_latam}/{total_with_geo} posts con geo conocido ({100*n_latam/total_with_geo:.0f}% si hay geo).")
        lines.append("")

        # Idioma
        lang = tk["language"].fillna("?").value_counts().head(10)
        lines.append("### Distribución por idioma (top 10)\n")
        lines.append("| Idioma | Posts | % |")
        lines.append("|---|---:|---:|")
        for l, n in lang.items():
            pct = 100 * n / len(tk)
            mark = " 🌎" if l in LATAM_LANGS else ""
            lines.append(f"| {l}{mark} | {n} | {pct:.0f}% |")
        lines.append("")

        # Top 5 posts
        lines.append("### Top 5 TikToks por plays\n")
        top = tk.nlargest(5, "plays")[["keyword", "author", "plays", "likes", "comments", "language", "location", "url"]]
        for _, r in top.iterrows():
            lines.append(f"- **{r['plays']:,} plays** · @{r['author']} · `{r['keyword']}` · "
                         f"{r['language']}/{r['location']} · {r['likes']:,}👍 · {r['comments']}💬\n  {r['url']}")
        lines.append("")

    # ===== Reddit =====
    if not rd.empty:
        lines.append("## Reddit\n")

        # Posts vs comments
        type_counts = rd["type"].value_counts()
        lines.append(f"**Composición:** {type_counts.get('post', 0)} posts · {type_counts.get('comment', 0)} comments\n")

        # Volumen por keyword
        rd_kw = rd[rd["mode"] == "keyword"]
        if not rd_kw.empty:
            vol = (rd_kw.groupby("keyword")
                       .agg(items=("id", "count"),
                            posts=("type", lambda s: (s == "post").sum()),
                            comments=("type", lambda s: (s == "comment").sum()),
                            upvotes_total=("upvotes", "sum"))
                       .reset_index()
                       .sort_values("items", ascending=False))
            lines.append("### Volumen por keyword (búsqueda)\n")
            lines.append("| Keyword | Items | Posts | Comments | Upvotes totales |")
            lines.append("|---|---:|---:|---:|---:|")
            for _, r in vol.iterrows():
                lines.append(f"| {r['keyword']} | {int(r['items'])} | {int(r['posts'])} | "
                             f"{int(r['comments'])} | {int(r['upvotes_total']):,} |")
            lines.append("")

        # Volumen por subreddit (modo subreddit)
        rd_sub = rd[rd["mode"] == "subreddit"]
        if not rd_sub.empty:
            vol = (rd_sub.groupby("subreddit_input")
                        .agg(items=("id", "count"),
                             posts=("type", lambda s: (s == "post").sum()),
                             comments=("type", lambda s: (s == "comment").sum()),
                             upvotes_total=("upvotes", "sum"))
                        .reset_index()
                        .sort_values("items", ascending=False))
            lines.append("### Volumen por subreddit\n")
            lines.append("| Subreddit | Items | Posts | Comments | Upvotes totales |")
            lines.append("|---|---:|---:|---:|---:|")
            for _, r in vol.iterrows():
                lines.append(f"| r/{r['subreddit_input']} | {int(r['items'])} | "
                             f"{int(r['posts'])} | {int(r['comments'])} | {int(r['upvotes_total']):,} |")
            lines.append("")

        # Top comunidades (todas las pasadas)
        top_comm = rd["community"].dropna().value_counts().head(10)
        lines.append("### Top comunidades donde aparecen las conversaciones\n")
        lines.append("| Comunidad | Items |")
        lines.append("|---|---:|")
        for comm, n in top_comm.items():
            lines.append(f"| r/{comm} | {n} |")
        lines.append("")

        # Top posts por upvotes
        rd_posts = rd[rd["type"] == "post"].nlargest(5, "upvotes")
        if not rd_posts.empty:
            lines.append("### Top 5 posts Reddit por upvotes\n")
            for _, r in rd_posts.iterrows():
                lines.append(f"- **{int(r['upvotes'])} upvotes** · r/{r['community']} · "
                             f"`{r['keyword'] or r['subreddit_input']}` · {r['n_comments']}💬\n"
                             f"  *{(r['title'] or '')[:120]}*  \n  {r['url']}")
            lines.append("")

    # ===== Conclusiones técnicas =====
    lines.append("## Conclusiones técnicas (para correo a Laura)\n")
    lines.append("- **Factibilidad:** scraping funciona en TikTok y Reddit, sin las restricciones de API directa.")
    lines.append("- **TikTok devuelve:** texto + idioma detectado + geolocalización a nivel país + métricas completas (plays, likes, shares, comments, collects) + autor + hashtags. La ventana temporal funciona con filtro server-side `PAST_WEEK` + filtro exacto en post-proceso.")
    lines.append("- **Reddit devuelve:** posts + comentarios en una sola pasada (bono inesperado) + métricas (upvotes, ratio, threads) + comunidad + flair. Estructura permite reconstruir threads por `parentId`/`postId`.")
    lines.append("- **Cobertura LATAM:** ver tabla por keyword arriba — las keywords en español tienden a traer % LATAM más alto.")
    lines.append("- **Costo del barrido completo:** ver costo arriba. Escalable proporcionalmente para el piloto final.")
    return "\n".join(lines)


def main() -> int:
    PROCESSED.mkdir(parents=True, exist_ok=True)

    print("[report] cargando runs...")
    tk_runs = load_runs("tiktok")
    rd_runs = load_runs("reddit")
    print(f"[report]   TikTok: {len(tk_runs)} runs · Reddit: {len(rd_runs)} runs")

    tk = flatten_tiktok(tk_runs)
    rd = flatten_reddit(rd_runs)
    print(f"[report]   TikTok: {len(tk)} items · Reddit: {len(rd)} items")

    tk_csv = PROCESSED / "tiktok_posts.csv"
    rd_csv = PROCESSED / "reddit_items.csv"
    tk.to_csv(tk_csv, index=False)
    rd.to_csv(rd_csv, index=False)
    print(f"[report]   → {tk_csv.relative_to(ROOT)}")
    print(f"[report]   → {rd_csv.relative_to(ROOT)}")

    print("[report] consultando costos a Apify...")
    cost, n_runs = get_actor_runs_cost()
    print(f"[report]   costo hoy: ${cost:.2f} ({n_runs} runs)")

    report = build_report(tk, rd, cost, n_runs)
    out_md = PROCESSED / "report.md"
    out_md.write_text(report, encoding="utf-8")
    print(f"[report]   → {out_md.relative_to(ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
