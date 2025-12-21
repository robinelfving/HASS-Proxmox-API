from homeassistant import config_entries
import voluptuous as vol

from .const import (
    DOMAIN,
    CONF_HOST,
    CONF_TOKEN_ID,
    CONF_TOKEN_SECRET,
    CONF_VERIFY_SSL,
    DEFAULT_VERIFY_SSL,
)


class ProxmoxConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_HOST],
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_TOKEN_ID): str,
                vol.Required(CONF_TOKEN_SECRET): str,
                vol.Optional(CONF_VERIFY_SSL, default=DEFAULT_VERIFY_SSL): bool,
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema)
