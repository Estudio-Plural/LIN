"""Crea (o actualiza) el Task de Apify para el monitoreo de crecimiento y, opcionalmente, el
Schedule diario que lo dispara.

SEGURIDAD: sin flags es DRY-RUN — imprime lo que haría y NO toca la nube. Tocar Apify requiere
flags explícitos. La activación del Schedule está gateada por --enable (si no, queda creado
pero deshabilitado).

Flujo previsto (post-barrido, cuando decidamos mandarlo a correr):
    # 1. ver qué se crearía (no toca nada)
    .venv/bin/python -m src.monitor.setup_apify_schedule
    # 2. crear el Task + primer snapshot manual (valida el camino, arranca la curva)
    .venv/bin/python -m src.monitor.setup_apify_schedule --create-task --first-run
    #    -> luego: python -m src.monitor.build_curves_apify
    # 3. cuando confirmemos, activar el Schedule diario
    .venv/bin/python -m src.monitor.setup_apify_schedule --create-schedule --enable

Handles: data/processed/monitor_handles.txt (lo genera src.analyze.top_creators).
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.scrape._common import get_client

ROOT = Path(__file__).resolve().parents[2]
HANDLES_FILE = ROOT / "data" / "processed" / "monitor_handles.txt"
ACTOR_ID = "clockworks/tiktok-scraper"
TASK_NAME = "lin-monitor-growth"
SCHEDULE_NAME = "lin-monitor-growth-daily"


def read_handles() -> list[str]:
    if not HANDLES_FILE.exists():
        return []
    return [ln.strip().lstrip("@") for ln in HANDLES_FILE.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.lstrip().startswith("#")]


def build_task_input(handles: list[str], since_days: int, posts: int) -> dict:
    since = (datetime.now(timezone.utc) - timedelta(days=since_days)).strftime("%Y-%m-%d")
    return {
        "profiles": handles,
        "resultsPerPage": posts,
        "profileScrapeSections": ["videos"],
        "profileSorting": "latest",
        "oldestPostDateUnified": since,
        "shouldDownloadVideos": False,
        "shouldDownloadCovers": False,
        "shouldDownloadSlideshowImages": False,
        "shouldDownloadAvatars": False,
        "shouldDownloadMusicCovers": False,
    }


def _id_of(obj):
    return getattr(obj, "id", None) or (obj.get("id") if isinstance(obj, dict) else None)


def find_task_id(client, name: str) -> str | None:
    for t in client.tasks().list(limit=1000).items:
        d = t if isinstance(t, dict) else (t.model_dump() if hasattr(t, "model_dump") else {})
        if d.get("name") == name:
            return d.get("id")
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since-days", type=int, default=7, help="oldestPostDateUnified = hoy - N (default 7)")
    ap.add_argument("--posts", type=int, default=30, help="cap de posts por handle (default 30)")
    ap.add_argument("--cron", default="0 13 * * *", help="cron del schedule (default 13:00 UTC = 08:00 Colombia)")
    ap.add_argument("--create-task", action="store_true", help="crear/actualizar el Task en Apify")
    ap.add_argument("--first-run", action="store_true", help="disparar un run manual del Task (primer snapshot)")
    ap.add_argument("--create-schedule", action="store_true", help="crear el Schedule diario")
    ap.add_argument("--enable", action="store_true", help="activar el Schedule (si no, queda deshabilitado)")
    args = ap.parse_args()

    handles = read_handles()
    if not handles:
        print(f"No hay handles en {HANDLES_FILE.relative_to(ROOT)}. Corré src.analyze.top_creators primero.",
              file=sys.stderr)
        return 1
    task_input = build_task_input(handles, args.since_days, args.posts)

    touching_cloud = args.create_task or args.first_run or args.create_schedule
    print(f"[setup] {len(handles)} handles · cap {args.posts}/handle · desde {task_input['oldestPostDateUnified']} · cron '{args.cron}'")

    if not touching_cloud:
        print("[setup] DRY-RUN (sin flags) — no toco Apify. Esto es lo que se crearía:")
        print(f"   Task '{TASK_NAME}' (actor {ACTOR_ID}) con {len(handles)} perfiles")
        print(f"   Schedule '{SCHEDULE_NAME}' diario @ cron '{args.cron}'")
        print("   Handles:", ", ".join(handles[:10]) + (" ..." if len(handles) > 10 else ""))
        print("\n   Para ejecutar: --create-task --first-run   (y luego --create-schedule --enable)")
        return 0

    client = get_client()
    task_id = find_task_id(client, TASK_NAME)

    if args.create_task:
        if task_id:
            client.task(task_id).update(task_input=task_input)
            print(f"[setup] Task existente actualizado: {task_id}")
        else:
            created = client.tasks().create(actor_id=ACTOR_ID, name=TASK_NAME, task_input=task_input)
            task_id = _id_of(created)
            print(f"[setup] Task creado: {task_id}")

    if not task_id:
        print("[setup] No hay task_id (corré --create-task primero).", file=sys.stderr)
        return 1

    if args.first_run:
        print("[setup] disparando primer snapshot (run manual del Task)...")
        run = client.task(task_id).call()
        print(f"[setup]   run {_id_of(run)} — luego corré: python -m src.monitor.build_curves_apify")

    if args.create_schedule:
        actions = [{"type": "RUN_ACTOR_TASK", "actorTaskId": task_id}]
        sched = client.schedules().create(
            cron_expression=args.cron,
            is_enabled=bool(args.enable),
            is_exclusive=True,
            name=SCHEDULE_NAME,
            actions=actions,
            description="LIN — snapshot diario de crecimiento de creadores manosfera",
        )
        print(f"[setup] Schedule creado: {_id_of(sched)} · enabled={args.enable} · cron '{args.cron}'")
        if not args.enable:
            print("[setup]   (deshabilitado — activalo con --enable cuando confirmemos)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
