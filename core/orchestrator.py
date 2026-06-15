import asyncio
import subprocess
import aiohttp
from datetime import datetime
from core.scanner import rustscan_ports, nmap_scan
from core.service_classifier import classify_service
from core.loot import Loot
from core.cve_lookup import lookup_cves_for_service
from plugins.manager import PluginManager
from models.report import ReportData

class Orchestrator:
    def __init__(self, target: str):
        self.target = target
        self.loot = Loot(target)
        self.plugin_manager = PluginManager()

    async def ping_host(self) -> bool:
        try:
            proc = await asyncio.create_subprocess_shell(
                f"ping -c 1 -W 2 {self.target}",
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            await proc.communicate()
            return proc.returncode == 0
        except:
            return False

    async def grab_banner(self, port: int, service_name: str) -> str | None:
        try:
            reader, writer = await asyncio.open_connection(self.target, port)
            service_lower = service_name.lower()
            if service_lower == "ssh":
                banner = await reader.readline()
                writer.close()
                await writer.wait_closed()
                return banner.decode().strip()
            elif service_lower in ["http", "https"]:
                writer.write(b"HEAD / HTTP/1.0\r\nHost: " + self.target.encode() + b"\r\n\r\n")
                await writer.drain()
                banner = await reader.read(1024)
                writer.close()
                return banner.decode(errors="ignore")[:500]
            else:
                writer.write(b"\r\n")
                await writer.drain()
                banner = await reader.read(256)
                writer.close()
                return banner.decode(errors="ignore").strip()
        except Exception:
            return None

    async def run(self, skip_ping: bool = False):
        if not skip_ping and not await self.ping_host():
            print(f"[-] Target {self.target} does not respond to ICMP. Use --skip-ping if host is up but blocks ping.")
            return None

        print(f"[+] Scanning ports on {self.target}...")
        ports = await rustscan_ports(self.target)
        if not ports:
            print("[-] No open ports found. Aborting.")
            return None
        print(f"[+] rustscan found open ports: {', '.join(map(str, ports))}")

        print(f"[+] Running Nmap version/script scan on {', '.join(map(str, ports))}...")
        nmap_raw = await nmap_scan(self.target, ports)
        self.loot.save_nmap(nmap_raw)

        print("[+] Nmap identified:")
        services = []
        for port, info in nmap_raw.items():
            banner = await self.grab_banner(port, info.get("name", ""))
            if banner:
                self.loot.save_banner(port, banner)
            svc = classify_service(port, info, banner, ssl_detected=(port == 443))
            services.append(svc)
            print(f"     {port}/tcp → {svc.category.value} ({svc.product} {svc.version})")

        print("[+] Fetching CVEs from NVD...")
        cves = []
        async with aiohttp.ClientSession() as session:
            for svc in services:
                if svc.cpe:
                    cves_for_svc = await lookup_cves_for_service(svc.cpe, session)
                elif svc.product and svc.version:
                    pseudo_cpe = f"cpe:/a:{svc.product}:{svc.version}"
                    cves_for_svc = await lookup_cves_for_service(pseudo_cpe, session)
                else:
                    cves_for_svc = []
                cves.extend(cves_for_svc)
        print(f"[+] Found {len(cves)} CVEs")

        scan_data = {
            "classified_services": services,
            "loot": self.loot,
            "nmap_raw": nmap_raw,
        }

        print("[+] Running plugins...")
        self.plugin_manager.resolve_dependencies()
        async with aiohttp.ClientSession() as session:
            plugin_outputs = await self.plugin_manager.execute_plugins(self.target, scan_data, session)
        print("[+] Plugins finished.")

        report = ReportData(
            target=self.target,
            timestamp=datetime.utcnow(),
            services=services,
            cves=cves,
            plugin_outputs=plugin_outputs,
            loot_dir=str(self.loot.base),
        )
        return report