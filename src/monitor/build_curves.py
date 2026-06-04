"""Construye curvas de crecimiento a partir de snapshots (modo local).

Lee data/raw/monitor/snapshot_*.json, agrupa por video (id) y arma la serie temporal de
métricas. La lógica de curvas (rows_to_df / compute_curves / write_outputs) la reusa también
el modo nube `src.monitor.build_curves_apify`.

Salidas:
  - data/processed/monitor_curves_long.csv     (un row por (video, snapshot) — para graficar)
  - data/processed/monitor_curves_summary.csv  (un row por video: primer/último valor, delta, velocidad)

Uso:
    .venv/bin/python -m src.monitor.build_curves
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

ROOT = Path(__file__).resolve().parents[2]
MONITOR_DIR = ROOT / "data" / "raw" / "monitor"
PROCESSED = ROOT / "data" / "processed"
METRICS = ["playCount", "diggCount", "commentCount", "shareCount", "collectCount"]


def load_local_rows() -> list[dict]:
    rows = []
    for f in sorted(MONITOR_DIR.glob("snapshot_*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"  ⚠️  skipping malformed: {f.name}", file=sys.stderr)
            continue
        rows.extend(data.get("items", []))
    return rows


def rows_to_df(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["captured_at"] = pd.to_datetime(df["captured_at"], format="%Y%m%dT%H%M%SZ", utc=True, errors="coerce")
    df["created_at"] = pd.to_datetime(df["created_at"], utc=True, errors="coerce")
    for m in METRICS:
        df[m] = pd.to_numeric(df.get(m), errors="coerce").fillna(0)
    return df.sort_values(["id", "captured_at"])


def compute_curves(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Devuelve (df_long ordenado, summary_df). summary = un row por video con delta y velocidad."""
    summary = []
    for vid, sub in df.groupby("id"):
        sub = sub.sort_values("captured_at")
        first, last = sub.iloc[0], sub.iloc[-1]
        span_h = (last["captured_at"] - first["captured_at"]).total_seconds() / 3600
        age_days = ((last["captured_at"] - last["created_at"]).total_seconds() / 86400
                    if pd.notna(last["created_at"]) else None)
        rec = {
            "id": vid,
            "author": last.get("author"),
            "created_at": last.get("created_at"),
            "age_days_at_last": round(age_days, 1) if age_days is not None else None,
            "url": last.get("url"),
            "snapshots": len(sub),
            "span_hours": round(span_h, 1),
        }
        for m in METRICS:
            delta = last[m] - first[m]
            rec[f"{m}_first"] = int(first[m])
            rec[f"{m}_last"] = int(last[m])
            rec[f"{m}_delta"] = int(delta)
            rec[f"{m}_per_day"] = round(delta / (span_h / 24), 1) if span_h > 0 else 0.0
        summary.append(rec)
    sdf = pd.DataFrame(summary)
    if not sdf.empty:
        sdf = sdf.sort_values("playCount_delta", ascending=False)
    return df, sdf


def write_outputs(df_long: pd.DataFrame, summary: pd.DataFrame, source: str = "local") -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    long_csv = PROCESSED / "monitor_curves_long.csv"
    sum_csv = PROCESSED / "monitor_curves_summary.csv"
    df_long.to_csv(long_csv, index=False)
    summary.to_csv(sum_csv, index=False)

    n_vid = df_long["id"].nunique() if not df_long.empty else 0
    n_snap = df_long["captured_at"].nunique() if not df_long.empty else 0
    print(f"[curves:{source}] {n_vid} videos · {len(df_long)} puntos · {n_snap} snapshots")
    if not df_long.empty:
        print(f"[curves:{source}]   ventana: {df_long['captured_at'].min()} → {df_long['captured_at'].max()}")
    print(f"[curves:{source}]   → {long_csv.relative_to(ROOT)}")
    print(f"[curves:{source}]   → {sum_csv.relative_to(ROOT)}")
    if n_snap < 2:
        print(f"[curves:{source}]   ⚠️  <2 snapshots — todavía no hay curva (hace falta otra captura).")


def main() -> int:
    rows = load_local_rows()
    if not rows:
        print("No hay snapshots en data/raw/monitor/. Corré src.monitor.snapshot primero.", file=sys.stderr)
        return 1
    long_df, summary = compute_curves(rows_to_df(rows))
    write_outputs(long_df, summary, source="local")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
