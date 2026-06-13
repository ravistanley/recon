from abc import ABC, abstractmethod
from models.report import ReportData

class Renderer(ABC):
    @abstractmethod
    async def render(self, report: ReportData) -> str | bytes:
        pass