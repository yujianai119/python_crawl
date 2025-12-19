from pathlib import Path
from datetime import datetime, timezone
import shutil
import os
import sys

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / 'data'
CACHE_FILE = DATA_DIR / 'rates_cache.json'
BACKUP_DIR = ROOT / 'backup' / 'data'

LOG_FILE = BACKUP_DIR / 'backup.log'

def ensure_dirs():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def backup():
    ensure_dirs()
    if not CACHE_FILE.exists():
        msg = f"{datetime.now().isoformat()} - no source cache file: {CACHE_FILE}\n"
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(msg)
        return 1

    ts = datetime.now().astimezone().strftime('%Y%m%dT%H%M%S%z')
    dest = BACKUP_DIR / f"rates_cache_{ts}.json"
    try:
        shutil.copy2(str(CACHE_FILE), str(dest))
        # also update a latest copy
        latest = BACKUP_DIR / 'rates_cache.json'
        shutil.copy2(str(CACHE_FILE), str(latest))
        msg = f"{datetime.now().isoformat()} - backed up {CACHE_FILE} -> {dest}\n"
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(msg)
        return 0
    except Exception as e:
        msg = f"{datetime.now().isoformat()} - backup failed: {e}\n"
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(msg)
        return 2


if __name__ == '__main__':
    code = backup()
    sys.exit(code)
