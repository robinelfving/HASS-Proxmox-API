from datetime import timedelta

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_TOKEN_ID,
    CONF_TOKEN_SECRET,
    CONF_VERIFY_SSL,
)


class ProxmoxCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.hass = hass
        self.entry = entry

        self.host = entry.data[CONF_HOST]
        self.token_id = entry.data[CONF_TOKEN_ID]
        self.token_secret = entry.data[CONF_TOKEN_SECRET]
        self.verify_ssl = entry.data[CONF_VERIFY_SSL]

        self.headers = {
            "Authorization": f"PVEAPIToken={self.token_id}={self.token_secret}"
        }

        self.session = async_get_clientsession(hass)

        super().__init__(
            hass,
            logger=None,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )

    async def _async_update_data(self):
        url = f"https://{self.host}:8006/api2/json/nodes"

        try:
            async with self.session.get(
                url,
                headers=self.headers,
                ssl=self.verify_ssl,
                timeout=10,
            ) as response:
                if response.status != 200:
                    raise UpdateFailed(
                        f"Invalid response from Proxmox: {response.status}"
                    )

                payload = await response.json()
                return payload["data"]

        except Exception as err:
            raise UpdateFailed(f"Proxmox API error: {err}") from err
