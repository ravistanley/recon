from models.service import ServiceIdentity, ServiceCategory

def classify_service(port: int, nmap_info: dict, banner: str | None, ssl_detected: bool = False) -> ServiceIdentity:
    product = nmap_info.get("product", "").lower()
    name = nmap_info.get("name", "").lower()

    category = ServiceCategory.UNKNOWN
    if port in [80, 8080, 8000, 8888] or "http" in name:
        category = ServiceCategory.HTTPS if ssl_detected else ServiceCategory.HTTP
    elif port == 22 or "ssh" in name:
        category = ServiceCategory.SSH
    elif port == 21 or "ftp" in name:
        category = ServiceCategory.FTP
    elif port in [139, 445] or "smb" in name:
        category = ServiceCategory.SMB
    elif port == 25 or "smtp" in name:
        category = ServiceCategory.SMTP
    elif port == 3306 or "mysql" in name:
        category = ServiceCategory.MYSQL
    elif port == 5432 or "postgres" in name:
        category = ServiceCategory.POSTGRES
    elif port == 3389 or "rdp" in name:
        category = ServiceCategory.RDP

    return ServiceIdentity(
        port=port,
        category=category,
        product=nmap_info.get("product", ""),
        version=nmap_info.get("version", ""),
        cpe=nmap_info.get("cpe"),
        is_ssl=ssl_detected,
        banner=banner,
    )