from __future__ import annotations

import json
import os
from datetime import date, datetime, timezone
from pathlib import Path

import yaml
from apify_client import ApifyClient
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "config.yaml"
DATA_DIR = ROOT / "data" / "raw"


def load_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    # normalize dates to date objects
    cfg["window"]["start"] = _as_date(cfg["window"]["start"])
    cfg["window"]["end"] = _as_date(cfg["window"]["end"])
    return cfg


def _as_date(v) -> date:
    if isinstance(v, date):
        return v
    return datetime.strptime(str(v), "%Y-%m-%d").date()


def flat_keywords(cfg: dict) -> list[tuple[str, str]]:
    """Returns [(category, keyword), ...] flattened from config."""
    out = []
    for category, words in cfg["keywords"].items():
        for w in words:
            out.append((category, w))
    return out


def get_client() -> ApifyClient:
    load_dotenv(ROOT / ".env")
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        raise RuntimeError(
            "APIFY_TOKEN no encontrado. Pega el token en .env (ver .env.example)."
        )
    return ApifyClient(token)


def filter_by_window(items: list[dict], start_unix: float, end_unix: float, ts_fields: list[str]) -> list[dict]:
    """Filtra items por ventana temporal. Si no encuentra timestamp, conserva el item (no descarta sin info)."""
    out = []
    for it in items:
        epoch = None
        for field in ts_fields:
            ts = it.get(field)
            if ts is None:
                continue
            if isinstance(ts, (int, float)):
                epoch = float(ts)
                # algunos campos vienen en ms, no en s
                if epoch > 10**12:
                    epoch /= 1000
                break
            if isinstance(ts, str):
                try:
                    epoch = datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
                    break
                except ValueError:
                    continue
        if epoch is None or start_unix <= epoch <= end_unix:
            out.append(it)
    return out


def window_unix(start_date: date, end_date: date) -> tuple[float, float]:
    start_unix = datetime(start_date.year, start_date.month, start_date.day, tzinfo=timezone.utc).timestamp()
    end_unix = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59, tzinfo=timezone.utc).timestamp()
    return start_unix, end_unix


def save_run_output(platform: str, label: str, items: list[dict], extra: dict | None = None) -> Path:
    """Save raw items as JSON with timestamp. Returns the output path."""
    out_dir = DATA_DIR / platform
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    safe_label = "".join(c if c.isalnum() or c in "-_" else "_" for c in label)
    path = out_dir / f"{ts}__{safe_label}.json"
    payload = {
        "platform": platform,
        "label": label,
        "fetched_at_utc": ts,
        "count": len(items),
        "extra": extra or {},
        "items": items,
    }
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=str)
    return path
