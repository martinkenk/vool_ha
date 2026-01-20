"""Config flow for Vool integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, CONF_SCAN_INTERVAL, CONF_LMC_DEVICE_ID, CONF_WALLBOX_DEVICE_ID
from .vool_api import VoolAPI

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_LMC_DEVICE_ID): str,
        vol.Required(CONF_WALLBOX_DEVICE_ID): str,
        vol.Optional(CONF_SCAN_INTERVAL, default=300): int,
    }
)

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    lmc_api = VoolAPI(data[CONF_EMAIL], data[CONF_PASSWORD], data[CONF_LMC_DEVICE_ID])
    wallbox_api = VoolAPI(data[CONF_EMAIL], data[CONF_PASSWORD], data[CONF_WALLBOX_DEVICE_ID])

    if not await lmc_api.authenticate() or not await wallbox_api.authenticate():
        raise InvalidAuth

    return {"title": f"Vool LMC {data[CONF_LMC_DEVICE_ID]} and Wallbox {data[CONF_WALLBOX_DEVICE_ID]}"}

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Vool."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""