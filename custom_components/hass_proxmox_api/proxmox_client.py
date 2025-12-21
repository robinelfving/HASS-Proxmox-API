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
            "mem": node.get("mem", 0),
            "maxmem": node.get("maxmem", 1),
            "uptime": node.get("uptime", 0),
        }

    async def _get(self, url: str):
        headers = {"Authorization": f"PVEAPIToken={self.token_id}={self.token_secret}"}
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers, ssl=self.verify_ssl) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    _LOGGER.error("Proxmox API returned %s: %s", resp.status, text)
                    raise Exception(f"Invalid response from Proxmox API: {resp.status}")
                return await resp.json()
