import asyncio
import subprocess
import json
import xmltodict
from config.settings import RUSTSCAN_TIMEOUT, NMAP_TIMEOUT

async def rustscan_ports(target: str) -> list[int]:
    cmd = f"rustscan -a {target} -u 5000 -b 1500 -t 2000 --ulimit 5000 --no-config -g -o json"
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=RUSTSCAN_TIMEOUT
    )
    stdout, _ = await proc.communicate()
    try:
        data = json.loads(stdout)
        ports = []
        for host in data.get("hosts", []):
            for port in host.get("ports", []):
                if port.get("state") == "open":
                    ports.append(port["port"])
        return sorted(set(ports))
    except:
        return []

async def nmap_scan(target: str, ports: list[int]) -> dict:
    if not ports:
        return {}
    port_str = ",".join(str(p) for p in ports)
    cmd = f"nmap -sV -sC -p{port_str} -oX - {target}"
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=NMAP_TIMEOUT
    )
    stdout, _ = await proc.communicate()
    data = xmltodict.parse(stdout)
    # parse into simple dict: port -> {service, product, version, cpe}
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