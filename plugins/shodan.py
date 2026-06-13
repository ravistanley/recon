import aiohttp
from plugins.base import ReconPlugin
from config.settings import SHODAN_API_KEY

class ShodanPlugin(ReconPlugin):
    name = "shodan"
    dependencies = []

    async def run(self, target: str, scan_data: dict, session: aiohttp.ClientSession):
        if not SHODAN_API_KEY:
            return {"error": "No Shodan API key"}
        url = f"https://api.shodan.io/shodan/host/{target}?key={SHODAN_API_KEY}"
        async with session.get(url) as resp:
            if resp.status == 200:
                return await resp.json()
            return {"error": f"Shodan API returned {resp.status}"}