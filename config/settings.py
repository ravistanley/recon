import os
from pathlib import Path

# API Keys (set in environment)
NVD_API_KEY = os.getenv("NVD_API_KEY", "")
SHODAN_API_KEY = os.getenv("SHODAN_API_KEY", "")

# Timeouts (seconds)
RUSTSCAN_TIMEOUT = 60
NMAP_TIMEOUT = 300
HTTP_TIMEOUT = 10

# Concurrency
MAX_CONCURRENT_PLUGINS = 5

# Paths
BASE_DIR = Path(__file__).parent.parent
LOOT_DIR = BASE_DIR / "loot"
CACHE_DIR = BASE_DIR / "cache"
REPORT_DIR = BASE_DIR / "reports"

# Wordlist discovery roots
WORDLIST_ROOTS = [
    "/usr/share/wordlists",
    "/usr/share/seclists",
    "/usr/share/dirb/wordlists",
    "/usr/share/dirbuster/wordlists",
]

# NVD cache TTL (hours)
CACHE_TTL_HOURS = 24