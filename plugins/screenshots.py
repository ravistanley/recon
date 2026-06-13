from playwright.async_api import async_playwright
from plugins.base import ReconPlugin

class ScreenshotPlugin(ReconPlugin):
    name = "screenshots"
    dependencies = ["service_classifier"]

    async def run(self, target: str, scan_data: dict, session):
        loot = scan_data.get("loot")
        if not loot:
            return {"error": "No loot object"}
        services = scan_data.get("classified_services", [])
        web_services = [s for s in services if s.category in ("http", "https")]
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            taken = 0
            for svc in web_services:
                proto = "https" if svc.is_ssl else "http"
                url = f"{proto}://{target}:{svc.port}"
                try:
                    page = await browser.new_page()
                    await page.goto(url, timeout=10000)
                    await page.screenshot(path=loot.screenshots / f"port_{svc.port}.png")
                    await page.close()
                    taken += 1
                except:
                    pass
            await browser.close()
        return {"screenshots_taken": taken}