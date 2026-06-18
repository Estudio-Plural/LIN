"""Construye data/dashboard/growth.json para la sección "Curva de vida" del dashboard.

Lee los CSV que produce build_curves_apify (monitor_curves_long.csv + _summary.csv) y
resume la dinámica de crecimiento de los videos frescos de los creadores curados:

  - velocidad media de plays/día por edad del video (la curva de vida)
  - cuántos videos alcanzan su pico de velocidad antes de los 2 días
  - reparto de plays nuevos por creador (para mostrar la concentración en outliers)

Uso: python -m src.monitor.build_growth_data
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from datetime import datetime, date
from pathlib import Path

PROC = Path("data/processed")
OUT = Path("data/dashboard/growth.json")
LONG = PROC / "monitor_curves_long.csv"
SUMMARY = PROC / "monitor_curves_summary.csv"

# Umbral mínimo de intervalos por bucket de edad para que entre a la curva (evita ruido).
MIN_INTERVALS = 5
# Edad máxima (días) a graficar: más allá la muestra es tu cola, no su juventud.
MAX_AGE = 12


def _parse(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def _f(x: str) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def build() -> dict:
    long_rows = list(csv.DictReader(LONG.open()))
    sum_rows = list(csv.DictReader(SUMMARY.open()))

    # --- Curva de vida: velocidad plays/día por bucket de edad (1 día) ---
    series: dict[str, list[tuple[datetime, float, datetime]]] = defaultdict(list)
    for r in long_rows:
        series[r["id"]].append((_parse(r["captured_at"]), _f(r["playCount"]), _parse(r["created_at"])))

    buckets: dict[int, list[float]] = defaultdict(list)  # edad(d) -> [plays/día]
    peak_young = peak_total = 0
    for pts in series.values():
        pts.sort()
        vels: list[tuple[float, float]] = []
        for (t0, p0, cr), (t1, p1, _cr) in zip(pts, pts[1:]):
            dt = (t1 - t0).total_seconds() / 86400
            if dt <= 0:
                continue
            vel = (p1 - p0) / dt
            age_mid = (t0 - cr).total_seconds() / 86400 + dt / 2
            vels.append((age_mid, vel))
            buckets[int(age_mid)].append(vel)
        if len(vels) >= 3:
            peak_total += 1
            if max(vels, key=lambda x: x[1])[0] < 2:
                peak_young += 1

    velocity_by_age = [
        {
            "age": age,
            "plays_per_day": round(sum(v) / len(v)),
            "n": len(v),
        }
        for age, v in sorted(buckets.items())
        if age <= MAX_AGE and len(v) >= MIN_INTERVALS
    ]

    # --- Reparto de plays nuevos por creador (concentración) ---
    by_auth: dict[str, dict[str, float]] = defaultdict(lambda: {"videos": 0, "new": 0.0, "base": 0.0})
    snaps = set()
    cap_min = cap_max = None
    for r in sum_rows:
        a = r["author"]
        by_auth[a]["videos"] += 1
        by_auth[a]["new"] += _f(r["playCount_delta"])
        by_auth[a]["base"] += _f(r["playCount_last"])
    for r in long_rows:
        t = _parse(r["captured_at"])
        snaps.add(t.date().isoformat())
        cap_min = t if cap_min is None or t < cap_min else cap_min
        cap_max = t if cap_max is None or t > cap_max else cap_max

    total_new = sum(d["new"] for d in by_auth.values())
    creators = sorted(
        (
            {
                "author": a,
                "videos": int(d["videos"]),
                "new_plays": round(d["new"]),
                "share_new": round(100 * d["new"] / total_new) if total_new else 0,
                "base_plays": round(d["base"]),
            }
            for a, d in by_auth.items()
        ),
        key=lambda x: -x["new_plays"],
    )

    n_days = (cap_max - cap_min).days if cap_min and cap_max else 0
    return {
        "generated_at": date.today().isoformat(),
        "window": {
            "start": cap_min.date().isoformat() if cap_min else None,
            "end": cap_max.date().isoformat() if cap_max else None,
            "days": n_days,
        },
        "n_snapshots": len(snaps),
        "n_videos": len(series),
        "total_new_plays": round(total_new),
        "peak_before_2d": {
            "count": peak_young,
            "total": peak_total,
            "pct": round(100 * peak_young / peak_total) if peak_total else 0,
        },
        "top_creator_share": creators[0]["share_new"] if creators else 0,
        "velocity_by_age": velocity_by_age,
        "creators": creators,
    }


def main() -> None:
    if not LONG.exists() or not SUMMARY.exists():
        raise SystemExit(
            "Faltan los CSV de curvas. Corré primero: python -m src.monitor.build_curves_apify"
        )
    data = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1))
    w = data["window"]
    print(
        f"[growth] {data['n_videos']} videos · {data['n_snapshots']} snapshots "
        f"({w['start']} → {w['end']}) · {len(data['velocity_by_age'])} buckets de edad"
    )
    print(
        f"[growth]   pico <2d: {data['peak_before_2d']['count']}/{data['peak_before_2d']['total']} "
        f"({data['peak_before_2d']['pct']}%) · outlier top: {data['top_creator_share']}% de plays nuevos"
    )
    print(f"[growth]   → {OUT}")


if __name__ == "__main__":
    main()
