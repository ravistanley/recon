import asyncio
import subprocess
from plugins.base import ReconPlugin

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
            cmd = f"nikto -h {url} -Format txt -nostatus"
            proc = await asyncio.create_subprocess_shell(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, _ = await proc.communicate()
            results[f"{svc.port}"] = stdout.decode()
        return results