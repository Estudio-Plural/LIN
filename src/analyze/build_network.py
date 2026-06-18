"""Arma la red de co-ocurrencia de hashtags para el dashboard: data/dashboard/network.json.

A diferencia de la versión anterior (coloreaba por bucket de keyword y mezclaba medios +
falsos positivos), esta:
  - detecta COMUNIDADES reales por modularidad sobre la co-ocurrencia (no por categoría de búsqueda),
  - asigna cada video a su comunidad dominante y calcula su mezcla señal/ruido (label_dist),
    alcance (plays) y top hashtags -> cada comunidad se puede NOMBRAR y leer como hallazgo,
  - ya no produce la red de "creadores" (era engañosa: centraba medios anglos + falsos
    positivos y dejaba a los creadores hispanos como nodos sueltos; la sección Creators ya
    cubre el ranking de creadores).

Uso: .venv/bin/python -m src.analyze.build_network
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "dashboard"
VIDEOS = OUT / "videos.json"

MIN_HT_FREQ = 4       # hashtags con menos apariciones no entran (legibilidad)
MIN_EDGE = 2          # co-ocurrencia mínima para una arista
MIN_COMMUNITY_HT = 3  # comunidades con menos hashtags se agrupan en "otros / dispersos"

STOP = {"fyp", "foryou", "foryoupage", "viral", "parati", "capcut", "fypシ", "tiktok",
        "trending", "fy", "paratii", "viralvideo", "fypage", "tiktokviral",
        "fyppppppppppppppppppppppp", "fypシ゚viral"}

# Paleta para comunidades nombradas (orden = tamaño desc). "otros" va en gris.
PALETTE = ["#60a5fa", "#f87171", "#a78bfa", "#34d399", "#fbbf24",
           "#22d3ee", "#fb923c", "#f472b6", "#c084fc", "#4ade80"]
OTROS_COLOR = "#52525b"

# Curaduría: clave = hashtag "ancla" (el más frecuente de la comunidad).
# (name, descripción en lenguaje de política). Si una comunidad no matchea, usa auto-nombre.
CURATED: dict[str, tuple[str, str]] = {
    "manosphere": (
        "Cobertura mediática (inglés)",
        "Documental de Louis Theroux, Netflix y prensa anglo discutiendo el fenómeno. "
        "Mayoría medios y crítica: es ruido SOBRE la manosfera, no manosfera."),
    "masculinidad": (
        "Núcleo hispano: alto valor",
        "El corazón sincero en español — “hombre de alto valor”, hipergamia, seducción, "
        "antifeminismo. La señal más pura del barrido."),
    "monkmode": (
        "Autosuperación / monk mode",
        "Disciplina, motivación y “mejorar como hombre”. La puerta de entrada blanda, "
        "mayormente sincera."),
    "hypergamy": (
        "Dating advice / looksmax (inglés)",
        "Consejos de citas anglosajones: hipergamia, “high value man”, looksmaxxing y black pill."),
    "hombrealfa": (
        "“Potencia masculina” / testosterona (MX)",
        "Marketing de suplementos y testosterona en México, mezclado con estética rural “alfa”."),
    "gym": (
        "Fitness / gymcel",
        "El puente desde el gimnasio: rutina, gymtok y gymcel."),
    "hombre": (
        "Masculinidad de “maestro / sabio” (fe)",
        "Tono de consejo, fe y sabiduría masculina. El más ambiguo: entre superación "
        "personal y doctrina."),
    "theboys": (
        "Edits de “The Boys” (falso positivo)",
        "Fan-edits de la serie capturados por azar (“soldier boy”). Casi todo falso positivo, "
        "pero infla las reproducciones."),
}


def load_videos():
    if not VIDEOS.exists():
        print("Falta videos.json; corré build_dashboard_data primero.", file=sys.stderr)
        raise SystemExit(1)
    return json.load(open(VIDEOS))


def build():
    vids = load_videos()

    # --- co-ocurrencia de hashtags ---
    freq = Counter()
    pair = Counter()
    # hashtags limpios por video (set, sin stopwords)
    vhs = []
    for v in vids:
        hs = sorted({h for h in v.get("hashtags", []) if h and h not in STOP})
        vhs.append(hs)
        for h in hs:
            freq[h] += 1
        for a, b in combinations(hs, 2):
            pair[(a, b)] += 1

    keep = {h for h, c in freq.items() if c >= MIN_HT_FREQ}

    # --- grafo + detección de comunidades por modularidad ---
    G = nx.Graph()
    G.add_nodes_from(keep)
    for (a, b), w in pair.items():
        if w >= MIN_EDGE and a in keep and b in keep:
            G.add_edge(a, b, weight=w)

    raw_comms = list(nx.community.greedy_modularity_communities(G, weight="weight"))
    # comunidades "nombrables" (>= MIN_COMMUNITY_HT hashtags), ordenadas por tamaño
    named = [c for c in raw_comms if len(c) >= MIN_COMMUNITY_HT]
    node_comm: dict[str, int] = {}
    for idx, members in enumerate(named):
        for h in members:
            node_comm[h] = idx  # -1 implícito = otros

    # --- asignar cada video a su comunidad dominante (por mayoría de sus hashtags) ---
    comm_videos: dict[int, list] = defaultdict(list)
    for v, hs in zip(vids, vhs):
        counts = Counter(node_comm[h] for h in hs if h in node_comm)
        if counts:
            comm_videos[counts.most_common(1)[0][0]].append(v)

    total_assigned = sum(len(vs) for vs in comm_videos.values()) or 1

    # --- stats + nombre por comunidad ---
    communities = []
    for idx, members in enumerate(named):
        vs = comm_videos.get(idx, [])
        hts = sorted(members, key=lambda h: freq[h], reverse=True)
        anchor = hts[0]
        label_dist = Counter(v.get("label") for v in vs if v.get("label"))
        dominant = label_dist.most_common(1)[0][0] if label_dist else None
        auto = " · ".join("#" + h for h in hts[:3])
        name, desc = CURATED.get(anchor, (auto, ""))
        top_creators = [a for a, _ in Counter(
            v["author"] for v in vs if v.get("author")).most_common(3)]
        communities.append({
            "id": idx,
            "anchor": anchor,
            "name": name,
            "auto": auto,
            "color": PALETTE[idx % len(PALETTE)],
            "hashtags": hts[:8],
            "n_hashtags": len(members),
            "n_videos": len(vs),
            "share": round(100 * len(vs) / total_assigned),
            "plays": sum(v.get("plays", 0) for v in vs),
            "label_dist": dict(label_dist),
            "dominant_label": dominant,
            "top_creators": top_creators,
            "desc": desc,
        })

    communities.sort(key=lambda c: -c["n_videos"])  # orden del panel = por volumen

    # nodos del grafo (solo hashtags en comunidades nombradas, para legibilidad)
    color_by_comm = {c["id"]: c["color"] for c in communities}
    nodes = [{"id": h, "freq": freq[h], "community": node_comm[h],
              "color": color_by_comm[node_comm[h]]}
             for h in keep if h in node_comm]
    keep_named = {n["id"] for n in nodes}
    links = [{"source": a, "target": b, "weight": w}
             for (a, b), w in pair.items()
             if w >= MIN_EDGE and a in keep_named and b in keep_named]

    coverage = round(100 * total_assigned / len(vids))
    net = {
        "hashtag": {"nodes": nodes, "links": links},
        "communities": communities,
        "meta": {"n_videos": len(vids), "assigned": total_assigned,
                 "coverage_pct": coverage, "n_communities": len(communities)},
    }
    return net, communities, coverage


def main() -> int:
    inspect = "--inspect" in sys.argv
    net, communities, coverage = build()

    if inspect:
        print(f"\n{len(communities)} comunidades · cobertura {coverage}% de los videos\n")
        for c in communities:
            mix = " ".join(f"{k}={v}" for k, v in sorted(
                c["label_dist"].items(), key=lambda x: -x[1]))
            print(f"[{c['id']}] ancla=#{c['anchor']}  ({c['n_hashtags']} ht · "
                  f"{c['n_videos']} videos · {c['share']}% · {c['plays']:,} plays)")
            print(f"     hashtags: {' '.join('#'+h for h in c['hashtags'])}")
            print(f"     mezcla:   {mix}")
            print(f"     creators: {', '.join(c['top_creators'])}\n")
        return 0

    OUT.mkdir(parents=True, exist_ok=True)
    json.dump(net, open(OUT / "network.json", "w"), ensure_ascii=False)
    print(f"[network] {len(net['hashtag']['nodes'])} nodos / {len(net['hashtag']['links'])} aristas · "
          f"{len(communities)} comunidades · cobertura {coverage}%")
    print(f"[network] → {(OUT / 'network.json').relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
