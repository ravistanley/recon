import pytest
from models.service import ServiceCategory
from core.service_classifier import classify_service

class TestServiceClassifier:
    def test_http_port_80(self):
        nmap_info = {"name": "http", "product": "Apache", "version": "2.4.49", "cpe": "cpe:/a:apache:http_server:2.4.49"}
        service = classify_service(80, nmap_info, banner=None, ssl_detected=False)
        assert service.port == 80
        assert service.category == ServiceCategory.HTTP
        assert service.product == "Apache"
        assert service.version == "2.4.49"
        assert service.cpe == "cpe:/a:apache:http_server:2.4.49"
        assert service.is_ssl is False

    def test_https_port_443(self):
        nmap_info = {"name": "https", "product": "nginx", "version": "1.18.0", "cpe": ""}
        service = classify_service(443, nmap_info, banner=None, ssl_detected=True)
        assert service.category == ServiceCategory.HTTPS
        assert service.is_ssl is True

    def test_ssh_port_22(self):
        nmap_info = {"name": "ssh", "product": "OpenSSH", "version": "8.2p1", "cpe": "cpe:/a:openbsd:openssh:8.2p1"}
        service = classify_service(22, nmap_info, banner="SSH-2.0-OpenSSH_8.2p1", ssl_detected=False)
        assert service.category == ServiceCategory.SSH
        assert service.banner == "SSH-2.0-OpenSSH_8.2p1"

    def test_smb_port_445(self):
        nmap_info = {"name": "microsoft-ds", "product": "Samba", "version": "4.13", "cpe": ""}
        service = classify_service(445, nmap_info, banner=None)
        assert service.category == ServiceCategory.SMB

    def test_unknown_port(self):
        nmap_info = {"name": "unknown", "product": "", "version": "", "cpe": ""}
        service = classify_service(12345, nmap_info, banner=None)
        assert service.category == ServiceCategory.UNKNOWN