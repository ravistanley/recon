from enum import Enum
from pydantic import BaseModel

class ServiceCategory(str, Enum):
    HTTP = "http"
    HTTPS = "https"
    SSH = "ssh"
    FTP = "ftp"
    SMB = "smb"
    SMTP = "smtp"
    MYSQL = "mysql"
    POSTGRES = "postgres"
    RDP = "rdp"
    UNKNOWN = "unknown"

class ServiceIdentity(BaseModel):
    port: int
    category: ServiceCategory
    product: str
    version: str
    cpe: str | None = None
    is_ssl: bool = False
    banner: str | None = None