import hashlib
import json
from pathlib import Path
from datetime import datetime, timedelta
from config.settings import CACHE_DIR, CACHE_TTL_HOURS

CACHE_DIR.mkdir(parents=True, exist_ok=True)

def _key(*parts):
    return hashlib.md5(":".join(str(p) for p in parts).encode()).hexdigest()

async def get_cache(key_type: str, identifier: str):
    cache_file = CACHE_DIR / f"{key_type}_{_key(identifier)}.json"
    if cache_file.exists():
        mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
        if datetime.now() - mtime < timedelta(hours=CACHE_TTL_HOURS):
            return json.loads(cache_file.read_text())
    return None

async def set_cache(key_type: str, identifier: str, data):
    cache_file = CACHE_DIR / f"{key_type}_{_key(identifier)}.json"
    cache_file.write_text(json.dumps(data))