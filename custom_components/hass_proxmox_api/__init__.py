from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import logging

from .const import DOMAIN, CONF_HOST, CONF_IP, CONF_TOKEN_ID, CONF_TOKEN_SECRET, CONF_VERIFY_SSL
from .coordinator import ProxmoxNodeCoordinator, ProxmoxQemuCoordinator, ProxmoxLXCCoordinator
from .proxmox_client import ProxmoxApiClient

PLATFORMS = ["sensor"]
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setup Proxmox integration from a config entry."""

    host_ip = entry.data.get(CONF_IP) or entry.data.get(CONF_HOST)
    token_id = entry.data.get(CONF_TOKEN_ID)
    token_secret = entry.data.get(CONF_TOKEN_SECRET)
    verify_ssl = entry.data.get(CONF_VERIFY_SSL, True)

    if not host_ip:
        _LOGGER.error("No host or IP defined in config entry %s", entry.entry_id)
        return False

    api_client = ProxmoxApiClient(host_ip, token_id, token_secret, verify_ssl)

    nodes = entry.data.get("nodes", [])
    display_name = entry.data.get(CONF_HOST)

    if not nodes:
        try:
            nodes = await api_client.get_nodes()
            _LOGGER.debug("Fetched nodes from Proxmox API at %s: %s", host_ip, nodes)
        except Exception as e:
            _LOGGER.error("Failed to fetch nodes from Proxmox API at %s: %s", host_ip, e)
            nodes = []

    if not nodes:
        _LOGGER.warning("No Proxmox nodes found. Sensors will not be created.")

    # Node coordinator
    node_coordinator = ProxmoxNodeCoordinator(
        hass,
        api_client=api_client,
        nodes=nodes,
        display_name=display_name,
    )
    await node_coordinator.async_config_entry_first_refresh()

    # QEMU coordinator
    qemu_coordinator = ProxmoxQemuCoordinator(
        hass,
        api_client=api_client,
        nodes=nodes,
    )
    await qemu_coordinator.async_config_entry_first_refresh()

    # Efter att du skapat QEMU-coordinatorn
    lxc_coordinator = ProxmoxLXCCoordinator(
        hass,
        api_client=api_client,
        nodes=nodes,
    )
    await lxc_coordinator.async_config_entry_first_refresh()

    # Spara coordinators i hass.data
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "node": node_coordinator,
        "qemu": qemu_coordinator,
        "lxc": lxc_coordinator, 
    }


    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True
