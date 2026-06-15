import asyncio
import subprocess
from plugins.base import ReconPlugin
from core.wordlist_selector import detect_task_type, get_wordlist_for_task

GOBUSTER_TIMEOUT = 180

class GobusterPlugin(ReconPlugin):
    name = "gobuster"
    dependencies = ["service_classifier"]

    async def run(self, target: str, scan_data: dict, session):
        services = scan_data.get("classified_services", [])
        results = {}
        for svc in services:
            if svc.category not in ("http", "https"):
                continue
            task_type = await detect_task_type(target, svc.port, svc.is_ssl, svc.category)
            wordlist = await get_wordlist_for_task(task_type)
            if not wordlist:
                results[str(svc.port)] = "No wordlist found for gobuster"
                continue
            proto = "https" if svc.is_ssl else "http"
            url = f"{proto}://{target}:{svc.port}"
            print(f"   [gobuster] Scanning {url} with wordlist {wordlist} (timeout {GOBUSTER_TIMEOUT}s)...")
            if task_type == "vhost":
                cmd = f"gobuster vhost -u {url} -w {wordlist} -t 30 --no-color"
            else:
                cmd = f"gobuster dir -u {url} -w {wordlist} -t 30 --no-color -b 404,403"
            try:
                proc = await asyncio.create_subprocess_shell(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=GOBUSTER_TIMEOUT)
                results[str(svc.port)] = stdout.decode()
            except asyncio.TimeoutError:
                results[str(svc.port)] = f"Timeout after {GOBUSTER_TIMEOUT}s"
            except Exception as e:
                results[str(svc.port)] = f"Error: {e}"
        return results