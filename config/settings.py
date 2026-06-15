import os
from pathlib import Path

NVD_API_KEY = os.getenv("NVD_API_KEY", "")
SHODAN_API_KEY = os.getenv("SHODAN_API_KEY", "")

RUSTSCAN_TIMEOUT = 120
NMAP_TIMEOUT = 300
HTTP_TIMEOUT = 10

MAX_CONCURRENT_PLUGINS = 5

BASE_DIR = Path(__file__).parent.parent
LOOT_DIR = BASE_DIR / "loot"
CACHE_DIR = BASE_DIR / "cache"
REPORT_DIR = BASE_DIR / "reports"

WORDLIST_ROOTS = [
    "/usr/share/wordlists",
    "/usr/share/seclists",
    "/usr/share/dirb/wordlists",
    "/usr/share/dirbuster/wordlists",
]

CACHE_TTL_HOURS = 24