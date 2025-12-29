from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta
import logging

_LOGGER = logging.getLogger(__name__)

DEFAULT_UPDATE_INTERVAL = timedelta(seconds=30)

class ProxmoxNodeCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api_client, nodes, display_name=None):
        self.api_client = api_client
        self.display_name = display_name
        self.nodes_config = [{"node": node, "display_name": display_name or node} for node in nodes]

        super().__init__(
            hass,
            _LOGGER,
            name="Proxmox Nodes",
            update_interval=DEFAULT_UPDATE_INTERVAL,
        )

    async def _async_update_data(self):
        try:
            new_data = []
            for node in self.nodes_config:
                node_name = node["node"]  # använd exakt namn
                display_name = node["display_name"]
                try:
                    node_status = await self.api_client.get_node_status(node_name)
                    _LOGGER.debug("Node status for %s: %s", node_name, node_status)
                    if node_status:
                        node_status["node"] = node_name
                        new_data.append(node_status)
                except Exception as err:
                    _LOGGER.error("Failed to fetch data for node %s: %s", node_name, err)
                    # fortsätt med övriga noder även om en nod misslyckas
                    continue
            return new_data
        except Exception as err:
            raise UpdateFailed(f"Failed to fetch data from Proxmox API: {err}") from err

class ProxmoxQemuCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api_client, nodes):
        self.api_client = api_client
        self.nodes = nodes

        super().__init__(
            hass,
            _LOGGER,
            name="Proxmox QEMU",
            update_interval=DEFAULT_UPDATE_INTERVAL,
        )

    async def _async_update_data(self):
        data = []

        for node in self.nodes:
            qemus = await self.api_client.get_qemu_list(node)
            for vm in qemus:
                vmid = vm["vmid"]
                status = await self.api_client.get_qemu_status(node, vmid)
                if status:
                    status["node"] = node
                    status["vmid"] = vmid
                    data.append(status)

        return data
    
class ProxmoxLXCCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api_client, nodes):
        self.api_client = api_client
        self.nodes = nodes

        super().__init__(
            hass,
            _LOGGER,
            name="Proxmox LXC",
            update_interval=DEFAULT_UPDATE_INTERVAL,
        )

    async def _async_update_data(self):
        data = []

        for node in self.nodes:
            lxcs = await self.api_client.get_lxc_list(node)
            for lxc in lxcs:
                vmid = lxc["vmid"]
                status = await self.api_client.get_lxc_status(node, vmid)
                if status:
                    status["node"] = node
                    status["vmid"] = vmid
                    data.append(status)

        return data