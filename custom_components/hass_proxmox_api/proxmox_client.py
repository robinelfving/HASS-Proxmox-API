import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)

class ProxmoxApiClient:
    def __init__(self, host: str, token_id: str, token_secret: str, verify_ssl: bool = True):
        self.host = host
        self.token_id = token_id
        self.token_secret = token_secret
        self.verify_ssl = verify_ssl
        self.base_url = f"https://{self.host}:8006/api2/json"
        self._session: aiohttp.ClientSession | None = None

    async def get_nodes(self):
        url = f"{self.base_url}/nodes"
        data = await self._get(url)
        return [node["node"] for node in data.get("data", [])]

    async def get_node_status(self, node_name: str):
        url = f"{self.base_url}/nodes/{node_name}/status"
        data = await self._get(url)
        if "data" not in data:
            return None
        node = data["data"]
        return {
            "cpu": node.get("cpu", 0),
            "memory": {
                "used": node.get("memory", {}).get("used"),
                "total": node.get("memory", {}).get("total"),
        },
            "uptime": node.get("uptime", 0),
            "pveversion": node.get("pveversion"),
        }

#List VMs
    async def get_qemu_list(self, node_name: str):
        url = f"{self.base_url}/nodes/{node_name}/qemu"
        data = await self._get(url)

        if "data" not in data:
            return []

        return [
            {
                "vmid": vm.get("vmid"),
                "name": vm.get("name"),
                "status": vm.get("status"),
            }
            for vm in data["data"]
        ]

#VM Status
    async def get_qemu_status(self, node_name: str, vmid: int):
        url = f"{self.base_url}/nodes/{node_name}/qemu/{vmid}/status/current"
        data = await self._get(url)

        if "data" not in data:
            return None

        vm = data["data"]

        return {
            "name": vm.get("name"),
            "status": vm.get("status"),
            "cpu": vm.get("cpu", 0),
            "cpus": vm.get("cpus"),
            "memory": {
                "used": vm.get("mem"),
                "total": vm.get("maxmem"),
            },
            "uptime": vm.get("uptime", 0),
        }

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=10)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def _get(self, url: str):
        headers = {"Authorization": f"PVEAPIToken={self.token_id}={self.token_secret}"}
        session = await self._get_session()
        async with session.get(url, headers=headers, ssl=self.verify_ssl) as resp:
            if resp.status != 200:
                text = await resp.text()
                _LOGGER.error("Proxmox API returned %s: %s", resp.status, text)
                raise Exception(f"Invalid response from Proxmox API: {resp.status}")
            return await resp.json()