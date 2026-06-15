import json
import os
from pathlib import Path
from config.settings import WORDLIST_ROOTS, CACHE_DIR

class WordlistRegistry:
    def __init__(self):
        self.cache_file = CACHE_DIR / "wordlist_index.json"
        self.lists = {}
        self._load_or_scan()

    def _load_or_scan(self):
        if self.cache_file.exists():
            self.lists = json.loads(self.cache_file.read_text())
            return
        self._scan()
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.cache_file.write_text(json.dumps(self.lists))

    def _scan(self):
        for root in WORDLIST_ROOTS:
            root_path = Path(root)
            if not root_path.exists():
                continue
            for f in root_path.rglob("*"):
                if f.is_file() and f.suffix in ("", ".txt", ".lst"):
                    self._categorize(f)

    def _categorize(self, filepath: Path):
        name = str(filepath).lower()
        if "common" in name or "directory" in name or "dirb" in name:
            self.lists.setdefault("dir", []).append(str(filepath))
        if "subdomain" in name or "vhost" in name:
            self.lists.setdefault("vhost", []).append(str(filepath))
        if "api" in name:
            self.lists.setdefault("api", []).append(str(filepath))
        if "param" in name:
            self.lists.setdefault("param", []).append(str(filepath))
        if "rockyou" in name or "password" in name:
            self.lists.setdefault("password", []).append(str(filepath))
        self.lists.setdefault("fallback", []).append(str(filepath))

    def get_best(self, category: str) -> str | None:
        candidates = self.lists.get(category, []) or self.lists.get("fallback", [])
        if not candidates:
            return None
        return max(candidates, key=lambda p: os.path.getsize(p))