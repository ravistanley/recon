import asyncio
from config.wordlist_registry import WordlistRegistry
from models.service import ServiceCategory

registry = WordlistRegistry()

async def detect_task_type(host: str, port: int, ssl: bool, service_category: ServiceCategory) -> str:
    # For now simple mapping; could be extended with HTTP probe
    if service_category in (ServiceCategory.HTTP, ServiceCategory.HTTPS):
        # Could check for API patterns, but default to dir
        return "dir"
    return "dir"

async def get_wordlist_for_task(task_type: str) -> str | None:
    return registry.get_best(task_type)