from homeassistant import config_entries
import voluptuous as vol
import aiohttp
from .const import DOMAIN, CONF_HOST, CONF_IP, CONF_TOKEN_ID, CONF_TOKEN_SECRET, CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL

class ProxmoxConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input:
            try:
                await self._test_connection(user_input)
                return self.async_create_entry(title=user_input[CONF_HOST], data=user_input)
            except Exception:
                errors["base"] = "cannot_connect"

        schema = vol.Schema({
            vol.Required(CONF_HOST): str,
            vol.Optional(CONF_IP): str,
            vol.Required(CONF_TOKEN_ID): str,
            vol.Required(CONF_TOKEN_SECRET): str,
            vol.Optional(CONF_VERIFY_SSL, default=DEFAULT_VERIFY_SSL): bool,
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def _test_connection(self, data):
        ip_or_host = data.get(CONF_IP) or data[CONF_HOST]
        token_id = data[CONF_TOKEN_ID]
        token_secret = data[CONF_TOKEN_SECRET]
        verify_ssl = data.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL)

        headers = {"Authorization": f"PVEAPIToken={token_id}={token_secret}"}
        url = f"https://{ip_or_host}:8006/api2/json/nodes"

        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers, ssl=verify_ssl) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise Exception(f"Invalid response: {resp.status} {text}")
