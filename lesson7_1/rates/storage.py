import json
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import os

ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(ROOT, "data")
CACHE_FILE = os.path.join(DATA_DIR, "rates_cache.json")
# backup dir inside repository to keep a recent copy
BACKUP_DIR = os.path.join(ROOT, "backup", "data")
BACKUP_CACHE_FILE = os.path.join(BACKUP_DIR, "rates_cache.json")


def _ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)


def write_cache(rates: Any, all_banks_usd: Any = None, gold_price: Any = None, rates_update_time: str = None) -> None:
    _ensure_dir()
    # store as UTC with explicit tzinfo to avoid ambiguity
    payload = {"updated_at": datetime.now(timezone.utc).isoformat(), "rates": rates}
    if all_banks_usd is not None:
        payload["all_banks_usd"] = all_banks_usd
    if gold_price is not None:
        payload["gold_price"] = gold_price
    if rates_update_time is not None:
        payload["rates_update_time"] = rates_update_time
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    # Also write a backup copy for resiliency
    try:
        with open(BACKUP_CACHE_FILE, "w", encoding="utf-8") as bf:
            json.dump(payload, bf, ensure_ascii=False, indent=2)
        # also keep a timestamped version for historical debugging
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        ts_file = os.path.join(BACKUP_DIR, f"rates_cache_{ts}.json")
        with open(ts_file, "w", encoding="utf-8") as tf:
            json.dump(payload, tf, ensure_ascii=False)
    except Exception:
        # best-effort backup; do not raise to avoid breaking callers
        pass


def read_cache() -> Optional[Dict[str, Any]]:
    # Try primary cache
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    # Fallback to backup cache copy
    if os.path.exists(BACKUP_CACHE_FILE):
        try:
            with open(BACKUP_CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    # Final fallback to sample bundled data
    sample = os.path.join(DATA_DIR, "sample_cache.json")
    if os.path.exists(sample):
        try:
            with open(sample, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    return None


def is_expired(max_age_seconds: int = 600) -> bool:
    """Return True if cached data is older than max_age_seconds."""
    payload = read_cache()
    if not payload:
        return True
    updated = payload.get("updated_at")
    if not updated:
        return True
    try:
        t = datetime.fromisoformat(updated)
    except Exception:
        return True
    # if naive, assume it's UTC (legacy data)
    if t.tzinfo is None:
        t = t.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - t) > timedelta(seconds=max_age_seconds)


__all__ = ["write_cache", "read_cache", "is_expired"]
