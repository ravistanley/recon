import aiohttp
from storage.cache import get_cache, set_cache
from models.cve import CVERecord
from config.settings import NVD_API_KEY

async def lookup_cves_for_service(cpe: str, session: aiohttp.ClientSession) -> list[CVERecord]:
    cached = await get_cache("cve", cpe)
    if cached is not None:
        return [CVERecord(**c) for c in cached]

    url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    params = {"cpeName": cpe, "resultsPerPage": 20}
    if NVD_API_KEY:
        params["apiKey"] = NVD_API_KEY
    async with session.get(url, params=params) as resp:
        if resp.status != 200:
            return []
        data = await resp.json()

    cves = []
    for vuln in data.get("vulnerabilities", []):
        cve = vuln.get("cve", {})
        metrics = cve.get("metrics", {})
        cvssv3 = metrics.get("cvssMetricV31", [{}])[0].get("cvssData", {})
        cves.append(CVERecord(
            id=cve.get("id", ""),
            cvss_score=cvssv3.get("baseScore", 0.0),
            severity=cvssv3.get("baseSeverity", "UNKNOWN"),
            description=cve.get("descriptions", [{}])[0].get("value", "")[:200],
        ))
    await set_cache("cve", cpe, [c.dict() for c in cves])
    return cves