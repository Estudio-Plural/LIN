"""Construye las curvas de crecimiento leyendo los runs del Task de Apify (modo nube).

Para cada run exitoso del Task de monitoreo, toma su dataset, marca captured_at = inicio del
run, y reconstruye las curvas reusando la lógica de `build_curves`. Así el monitoreo corre en
la nube (Apify Schedule) y las curvas se arman on-demand desde acá, sin depender de archivos
locales ni de que tu Mac esté prendido.

Uso:
    .venv/bin/python -m src.monitor.build_curves_apify
    .venv/bin/python -m src.monitor.build_curves_apify --task-id <id>
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.scrape._common import get_client
from src.monitor.snapshot import slim
from src.monitor.build_curves import compute_curves, rows_to_df, write_outputs

DEFAULT_TASK_NAME = "lin-monitor-growth"


def asdict(o) -> dict:
    if isinstance(o, dict):
        return o
    for m in ("model_dump", "dict"):
        if hasattr(o, m):
            try:
                return getattr(o, m)()
            except Exception:
                pass
    return {}


def fmt_captured(dt) -> str | None:
    """Normaliza el startedAt del run a '%Y%m%dT%H%M%SZ' (lo que espera rows_to_df)."""
    if dt is None:
        return None
    try:
        if hasattr(dt, "strftime"):
            return dt.strftime("%Y%m%dT%H%M%SZ")
        return datetime.fromisoformat(str(dt).replace("Z", "+00:00")).strftime("%Y%m%dT%H%M%SZ")
    except Exception:
        return None


def find_task_id(client, name: str) -> str | None:
    for t in client.tasks().list(limit=1000).items:
        d = asdict(t)
        if d.get("name") == name:
            return d.get("id")
    return None


def pull_rows(client, task_id: str) -> list[dict]:
    rows = []
    runs = client.task(task_id).runs().list(limit=1000)
    for r in runs.items:
        d = asdict(r)
        if d.get("status") != "SUCCEEDED":
            continue
        ds = d.get("defaultDatasetId") or d.get("default_dataset_id")
        captured = fmt_captured(d.get("startedAt") or d.get("started_at"))
        if not ds or not captured:
            continue
        for it in client.dataset(ds).iterate_items():
            if it.get("id"):
                rows.append(slim(it, captured))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-id", help="ID del Task (si no, lo busca por nombre)")
    ap.add_argument("--task-name", default=DEFAULT_TASK_NAME)
    args = ap.parse_args()

    client = get_client()
    task_id = args.task_id or find_task_id(client, args.task_name)
    if not task_id:
        print(f"No encontré Task '{args.task_name}'. ¿Ya lo creaste con setup_apify_schedule?", file=sys.stderr)
        return 1

    print(f"[curves:apify] task {task_id}")
    rows = pull_rows(client, task_id)
    if not rows:
        print("No hay runs exitosos con items todavía (el Schedule aún no corrió).", file=sys.stderr)
        return 1
    long_df, summary = compute_curves(rows_to_df(rows))
    write_outputs(long_df, summary, source="apify")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
