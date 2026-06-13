from pydantic import BaseModel

class CVERecord(BaseModel):
    id: str
    cvss_score: float
    severity: str
    description: str
    exploit_available: bool = False