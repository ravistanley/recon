from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ReconPlugin(ABC):
    name: str
    dependencies: List[str] = []

    @abstractmethod
    async def run(self, target: str, scan_data: Dict[str, Any], session) -> Dict[str, Any]:
        pass