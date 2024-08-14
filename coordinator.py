"""DataUpdateCoordinator for Vool integration."""
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryAuthFailed

from .const import DOMAIN, CONF_SCAN_INTERVAL
from .vool_api import VoolAPI, InvalidAuth

_LOGGER = logging.getLogger(__name__)

class VoolCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Vool data."""

    def __init__(self, hass: HomeAssistant, entry):
        """Initialize."""
        self.api = VoolAPI(entry.data["email"], entry.data["password"], entry.data["device_id"])
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=entry.data[CONF_SCAN_INTERVAL]),
        )

    async def _async_update_data(self):
        """Fetch data from Vool."""
        try:
            return await self.api.get_device_status()
        except InvalidAuth as err:
            raise ConfigEntryAuthFailed from err
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err