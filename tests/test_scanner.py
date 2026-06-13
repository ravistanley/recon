import pytest
from unittest.mock import patch, AsyncMock
from core.scanner import rustscan_ports, nmap_scan

@pytest.mark.asyncio
class TestScanner:
    @patch("core.scanner.asyncio.create_subprocess_shell")
    async def test_rustscan_ports_success(self, mock_subprocess):
        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (
            b'{"hosts":[{"ports":[{"port":22,"state":"open"},{"port":80,"state":"open"}]}]}',
            b"",
        )
        mock_subprocess.return_value = mock_proc

        ports = await rustscan_ports("192.168.1.1")
        assert ports == [22, 80]

    @patch("core.scanner.asyncio.create_subprocess_shell")
    async def test_rustscan_ports_empty(self, mock_subprocess):
        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"{}", b"")
        mock_subprocess.return_value = mock_proc

        ports = await rustscan_ports("192.168.1.1")
        assert ports == []

    @patch("core.scanner.asyncio.create_subprocess_shell")
    async def test_nmap_scan_single_port(self, mock_subprocess):
        xml_output = b"""<?xml version="1.0"?>
        <nmaprun>
            <host>
                <ports>
                    <port portid="22">
                        <service name="ssh" product="OpenSSH" version="8.2p1" cpe="cpe:/a:openbsd:openssh:8.2p1"/>
                    </port>
                </ports>
            </host>
        </nmaprun>"""
        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (xml_output, b"")
        mock_subprocess.return_value = mock_proc

        result = await nmap_scan("192.168.1.1", [22])
        assert result[22]["name"] == "ssh"
        assert result[22]["product"] == "OpenSSH"
        assert result[22]["version"] == "8.2p1"
        assert result[22]["cpe"] == "cpe:/a:openbsd:openssh:8.2p1"

    @patch("core.scanner.asyncio.create_subprocess_shell")
    async def test_nmap_scan_no_ports(self, mock_subprocess):
        result = await nmap_scan("192.168.1.1", [])
        assert result == {}
        mock_subprocess.assert_not_called()