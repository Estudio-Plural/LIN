"""Arma la red de co-ocurrencia para el dashboard: data/dashboard/network.json.

- hashtag: nodos = hashtags (freq), aristas = co-ocurrencia en un mismo video, cluster = categoría dominante.
- creators: nodos = top creadores por alcance, aristas = hashtags compartidos, label = clasificación mayoritaria.

Uso: .venv/bin/python -m src.analyze.build_network
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "dashboard"
VIDEOS = OUT / "videos.json"

MIN_HT_FREQ = 4   # hashtags con menos apariciones no entran (legibilidad)
MIN_EDGE = 2      # co-ocurrencia mínima para una arista
TOP_CREATORS = 60
STOP = {"fyp", "foryou", "foryoupage", "viral", "parati", "capcut", "fypシ", "tiktok",
        "trending", "fy", "paratii", "viralvideo", "fypage", "tiktokviral"}


def main() -> int:
    if not VIDEOS.exists():
        print("Falta videos.json; corré build_dashboard_data primero.", file=sys.stderr)
        return 1
    vids = json.load(open(VIDEOS))

    # --- red de hashtags ---
    freq = Counter()
    ht_cat = defaultdict(Counter)
    pair = Counter()
    for v in vids:
        hs = [h for h in set(v["hashtags"]) if h and h not in STOP]
        for h in hs:
            freq[h] += 1
            ht_cat[h][v["category"]] += 1
        for a, b in combinations(sorted(hs), 2):
            pair[(a, b)] += 1
    keep = {h for h, c in freq.items() if c >= MIN_HT_FREQ}
    nodes = [{"id": h, "freq": freq[h],
              "cluster": (ht_cat[h].most_common(1)[0][0] if ht_cat[h] else None)} for h in keep]
    links = [{"source": a, "target": b, "weight": w}
             for (a, b), w in pair.items() if w >= MIN_EDGE and a in keep and b in keep]

    # --- red de creadores ---
    by_author = defaultdict(list)
    for v in vids:
        if v["author"]:
            by_author[v["author"]].append(v)
    reach = {a: sum(x["plays"] for x in vs) for a, vs in by_author.items()}
    top = sorted(reach, key=reach.get, reverse=True)[:TOP_CREATORS]
    a_tags = {a: {h for v in by_author[a] for h in v["hashtags"] if h not in STOP} for a in top}

    def majority_label(vs):
        c = Counter(v.get("label") for v in vs if v.get("label"))
        return c.most_common(1)[0][0] if c else None

    cnodes = [{"id": a, "reach": reach[a], "videos": len(by_author[a]),
               "label": majority_label(by_author[a]),
               "top_url": max(by_author[a], key=lambda x: x["plays"])["url"]} for a in top]
    clinks = []
    for a, b in combinations(top, 2):
        shared = len(a_tags[a] & a_tags[b])
        if shared >= 2:
            clinks.append({"source": a, "target": b, "weight": shared})

    net = {"hashtag": {"nodes": nodes, "links": links},
           "creators": {"nodes": cnodes, "links": clinks}}
    OUT.mkdir(parents=True, exist_ok=True)
    json.dump(net, open(OUT / "network.json", "w"), ensure_ascii=False)
    print(f"[network] hashtags: {len(nodes)} nodos / {len(links)} aristas · "
          f"creators: {len(cnodes)} nodos / {len(clinks)} aristas")
    print(f"[network] → {(OUT / 'network.json').relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
