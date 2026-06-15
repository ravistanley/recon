import asyncio
import subprocess
from plugins.base import ReconPlugin
from models.service import ServiceCategory

class NSEPlugin(ReconPlugin):
    name = "nse"
    dependencies = ["service_classifier"]

    async def run(self, target: str, scan_data: dict, session):
        services = scan_data.get("classified_services", [])
        results = {}
        for svc in services:
            script_map = {
                ServiceCategory.HTTP: "http-title,http-headers,http-enum",
                ServiceCategory.HTTPS: "http-title,http-headers,http-enum",
                ServiceCategory.SMB: "smb-os-discovery,smb-enum-shares",
                ServiceCategory.FTP: "ftp-anon",
                ServiceCategory.SSH: "ssh-hostkey",
            }
            scripts = script_map.get(svc.category, "")
            if not scripts:
                continue
            cmd = f"nmap -p {svc.port} --script {scripts} {target} -oN -"
            proc = await asyncio.create_subprocess_shell(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, _ = await proc.communicate()
            results[f"{svc.port}_{svc.category.value}"] = stdout.decode()
        return results