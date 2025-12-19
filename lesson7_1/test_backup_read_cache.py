import os
import json
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / 'data'
BACKUP = ROOT / 'backup' / 'data'
MAIN = DATA / 'rates_cache.json'
BACK = BACKUP / 'rates_cache.json'
SAMPLE = DATA / 'sample_cache.json'

from rates.storage import read_cache

# helper to safe rename

def safe_rename(src, dst):
    try:
        if src.exists():
            src.rename(dst)
            return True
    except Exception as e:
        print('rename error', src, e)
    return False

# record state
main_bak = MAIN.with_suffix('.json.bak')
back_bak = BACK.with_suffix('.json.bak')

# Step 1: rename main -> main.bak
moved_main = safe_rename(MAIN, main_bak)
print('main renamed:', moved_main)
print('\n-- read_cache() (expect fallback to backup)')
print(json.dumps(read_cache(), ensure_ascii=False, indent=2))

# Step 2: rename backup -> backup.bak
moved_back = safe_rename(BACK, back_bak)
print('backup renamed:', moved_back)
print('\n-- read_cache() (expect fallback to sample)')
print(json.dumps(read_cache(), ensure_ascii=False, indent=2))

# restore files
if moved_back and back_bak.exists():
    try:
        back_bak.rename(BACK)
    except Exception as e:
        print('restore backup error', e)
if moved_main and main_bak.exists():
    try:
        main_bak.rename(MAIN)
    except Exception as e:
        print('restore main error', e)

print('\nrestored')
