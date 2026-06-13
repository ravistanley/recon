from pathlib import Path
from datetime import datetime
import json
from config.settings import LOOT_DIR

class Loot:
    def __init__(self, target: str):
        self.target = target
        self.timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.base = LOOT_DIR / target / self.timestamp
        self.scans = self.base / "scans"
        self.screenshots = self.base / "screenshots"
        self.reports = self.base / "reports"
        self.raw = self.base / "raw"
        self.parsed = self.base / "parsed"
        for p in [self.scans, self.screenshots, self.reports, self.raw, self.parsed]:
            p.mkdir(parents=True, exist_ok=True)

    def save_nmap(self, data: dict):
        (self.scans / "nmap.json").write_text(json.dumps(data, indent=2))

    def save_banner(self, port: int, banner: str):
        (self.raw / f"banner_{port}.txt").write_text(banner)

    def save_screenshot(self, name: str, png_bytes: bytes):
        (self.screenshots / f"{name}.png").write_bytes(png_bytes)

    def save_raw(self, filename: str, content: str):
        (self.raw / filename).write_text(content)