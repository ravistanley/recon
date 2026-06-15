from models.service import ServiceIdentity, ServiceCategory

def classify_service(port: int, nmap_info: dict, banner: str | None, ssl_detected: bool = False) -> ServiceIdentity:
    product = nmap_info.get("product", "").lower()
    name = nmap_info.get("name", "").lower()

    is_http_banner = banner and ("HTTP/" in banner or "html" in banner.lower() or "Content-Type" in banner)
    if is_http_banner:
        category = ServiceCategory.HTTPS if ssl_detected else ServiceCategory.HTTP
    elif port in [80, 443, 8080, 8443, 3000, 5000, 8000, 8008, 8888, 9000]:
        category = ServiceCategory.HTTPS if (ssl_detected or port == 443) else ServiceCategory.HTTP
    elif port == 22 or "ssh" in name:
        category = ServiceCategory.SSH
    elif port == 21 or "ftp" in name:
        category = ServiceCategory.FTP
    elif port in [139, 445] or "smb" in name:
        category = ServiceCategory.SMB
    elif port == 25 or "smtp" in name:
        category = ServiceCategory.SMTP
    else:
        category = ServiceCategory.UNKNOWN

    if "http" in name or "nginx" in product or "apache" in product or "next" in product:
        category = ServiceCategory.HTTPS if ssl_detected else ServiceCategory.HTTP

    return ServiceIdentity(
        port=port,
        category=category,
        product=nmap_info.get("product", ""),
        version=nmap_info.get("version", ""),
        cpe=nmap_info.get("cpe", ""),
        is_ssl=ssl_detected,
        banner=banner,
    )