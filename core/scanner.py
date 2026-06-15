import asyncio
import subprocess
import re
import xmltodict
from config.settings import RUSTSCAN_TIMEOUT, NMAP_TIMEOUT

async def run_cmd_with_timeout(cmd: str, timeout: int):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return stdout.decode(), stderr.decode()
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        raise TimeoutError(f"Command timed out after {timeout}s: {cmd}")

def extract_ports_from_rustscan(stdout: str) -> list[int]:
    ports = set()
    for match in re.findall(r"Open\s+\d+\.\d+\.\d+\.\d+:(\d+)", stdout):
        ports.add(int(match))
    for match in re.findall(r"^(\d+)$", stdout, re.MULTILINE):
        ports.add(int(match))
    return sorted(ports)

async def rustscan_ports(target: str) -> list[int]:
    cmd = f"rustscan -a {target} -b 1500 -t 2000 --ulimit 5000 --no-config"
    try:
        stdout, _ = await run_cmd_with_timeout(cmd, RUSTSCAN_TIMEOUT)
        ports = extract_ports_from_rustscan(stdout)
        return ports
    except Exception as e:
        print(f"[!] rustscan error: {e}")
        return []

async def nmap_scan(target: str, ports: list[int]) -> dict:
    if not ports:
        return {}
    port_str = ",".join(str(p) for p in ports)
    cmd = f"nmap -sV -sC -p{port_str} -oX - {target}"
    try:
        stdout, _ = await run_cmd_with_timeout(cmd, NMAP_TIMEOUT)
        data = xmltodict.parse(stdout)
        result = {}
        hosts = data.get("nmaprun", {}).get("host", [])
        if not isinstance(hosts, list):
            hosts = [hosts]
        for host in hosts:
            ports_node = host.get("ports", {}).get("port", [])
            if not isinstance(ports_node, list):
                ports_node = [ports_node]
            for p in ports_node:
                port_id = int(p.get("@portid"))
                service = p.get("service", {})
                result[port_id] = {
                    "name": service.get("@name", ""),
                    "product": service.get("@product", ""),
                    "version": service.get("@version", ""),
                    "cpe": service.get("@cpe", ""),
                }
        return result
    except Exception as e:
        print(f"[!] nmap scan error: {e}")
        return {}