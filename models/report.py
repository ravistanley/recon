from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Any
from models.service import ServiceIdentity
from models.cve import CVERecord

class ReportData(BaseModel):
    target: str
    timestamp: datetime
    services: List[ServiceIdentity]
    cves: List[CVERecord]
    plugin_outputs: Dict[str, Any]
    loot_dir: str