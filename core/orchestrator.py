import asyncio
import aiohttp
from datetime import datetime
from core.scanner import rustscan_ports, nmap_scan
from core.service_classifier import classify_service
from core.loot import Loot
from core.cve_lookup import lookup_cves_for_service  # defined below
from plugins.manager import PluginManager
from models.report import ReportData

class Orchestrator:
    def __init__(self, target: str):
        self.target = target
        self.loot = Loot(target)
        self.plugin_manager = PluginManager()

    async def run(self):
        # 1. Port scan
        ports = await rustscan_ports(self.target)
        # 2. Nmap detailed
        nmap_raw = await nmap_scan(self.target, ports)
        self.loot.save_nmap(nmap_raw)

        # 3. Banner grabbing (simplified – just reuse nmap banner if present)
        services = []
        for port, info in nmap_raw.items():
            banner = info.get("version", "")  # placeholder
            svc = classify_service(port, info, banner)
            services.append(svc)
            if banner:
                self.loot.save_banner(port, banner)

        # 4. CVE lookup (cached)
        cves = []
        async with aiohttp.ClientSession() as session:
            for svc in services:
                if svc.cpe:
                    cves_for_svc = await lookup_cves_for_service(svc.cpe, session)
                    cves.extend(cves_for_svc)

        # 5. Prepare scan_data for plugins
        scan_data = {
            "classified_services": services,
            "loot": self.loot,
            "nmap_raw": nmap_raw,
        }

        # 6. Plugin execution
        self.plugin_manager.resolve_dependencies()
        async with aiohttp.ClientSession() as session:
            plugin_outputs = await self.plugin_manager.execute_plugins(self.target, scan_data, session)

        # 7. Build report
        report = ReportData(
            target=self.target,
            timestamp=datetime.utcnow(),
            services=services,
            cves=cves,
            plugin_outputs=plugin_outputs,
            loot_dir=str(self.loot.base),
        )
        return report