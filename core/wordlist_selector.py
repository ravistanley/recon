from pathlib import Path
from config.wordlist_registry import WordlistRegistry

registry = WordlistRegistry()

async def detect_task_type(host: str, port: int, ssl: bool, service_category) -> str:
    return "dir"

async def get_wordlist_for_task(task_type: str) -> str | None:
    wl = registry.get_best(task_type)
    if wl and Path(wl).exists():
        return wl
    fallbacks = [
        "/usr/share/wordlists/dirb/common.txt",
        "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt",
        "/usr/share/wordlists/rockyou.txt",
    ]
    for fb in fallbacks:
        if Path(fb).exists():
            print(f"[!] Using fallback wordlist: {fb}")
            return fb
    return None