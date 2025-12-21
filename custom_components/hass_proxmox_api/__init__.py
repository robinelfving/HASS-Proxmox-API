from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import logging

from .const import DOMAIN, CONF_HOST, CONF_IP, CONF_TOKEN_ID, CONF_TOKEN_SECRET, CONF_VERIFY_SSL
from .coordinator import ProxmoxDataCoordinator
from .proxmox_client import ProxmoxApiClient

PLATFORMS = ["sensor"]
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setup Proxmox integration from a config entry."""
    # Använd IP om det finns, annars host
    host_ip = entry.data.get(CONF_IP) or entry.data.get(CONF_HOST)
    token_id = entry.data.get(CONF_TOKEN_ID)
    token_secret = entry.data.get(CONF_TOKEN_SECRET)
    verify_ssl = entry.data.get(CONF_VERIFY_SSL, True)

    if not host_ip:
        _LOGGER.error("No host or IP defined in config entry %s", entry.entry_id)
        return False

    api_client = ProxmoxApiClient(host_ip, token_id, token_secret, verify_ssl)

    # Hämta noder från config entry, eller från API om tomt
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

    # Skapa koordinator med nodlistan
    coordinator = ProxmoxDataCoordinator(hass, api_client=api_client, nodes=nodes, display_name=display_name)
    await coordinator.async_config_entry_first_refresh()

    # Spara koordinatorn för sensorerna
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Starta sensorer/platformar
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True
