import asyncio
import subprocess
from plugins.base import ReconPlugin

NIKTO_TIMEOUT = 120

class NiktoPlugin(ReconPlugin):
    name = "nikto"
    dependencies = ["service_classifier"]

    async def run(self, target: str, scan_data: dict, session):
        services = scan_data.get("classified_services", [])
        results = {}
        for svc in services:
            if svc.category not in ("http", "https"):
                continue
            proto = "https" if svc.is_ssl else "http"
            url = f"{proto}://{target}:{svc.port}"
            print(f"   [nikto] Scanning {url} (timeout {NIKTO_TIMEOUT}s)...")
            cmd = f"nikto -h {url} -Format json -nointeractive 2>/dev/null"
            try:
                proc = await asyncio.create_subprocess_shell(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=NIKTO_TIMEOUT)
                if not stdout.strip():
                    cmd = f"nikto -h {url} -Format txt -nointeractive 2>/dev/null"
                    proc = await asyncio.create_subprocess_shell(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=NIKTO_TIMEOUT)
                results[str(svc.port)] = stdout.decode() if stdout else "Nikto produced no output"
            except asyncio.TimeoutError:
                results[str(svc.port)] = f"Timeout after {NIKTO_TIMEOUT}s"
            except Exception as e:
                results[str(svc.port)] = f"Error: {e}"
        return results