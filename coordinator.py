"""DataUpdateCoordinator for Vool integration."""
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryAuthFailed

from .const import DOMAIN, CONF_SCAN_INTERVAL, CONF_LMC_DEVICE_ID, CONF_WALLBOX_DEVICE_ID
from .vool_api import VoolAPI, InvalidAuth

_LOGGER = logging.getLogger(__name__)

class VoolCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Vool data."""

    def __init__(self, hass: HomeAssistant, entry):
        """Initialize."""
        self.lmc_api = VoolAPI(entry.data["email"], entry.data["password"], entry.data[CONF_LMC_DEVICE_ID])
        self.wallbox_api = VoolAPI(entry.data["email"], entry.data["password"], entry.data[CONF_WALLBOX_DEVICE_ID])
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=entry.data[CONF_SCAN_INTERVAL]),
        )

    async def _async_update_data(self):
        """Fetch data from Vool."""
        try:
            lmc_data = await self.lmc_api.get_device_status()
            wallbox_data = await self.wallbox_api.get_device_status()
            
            # Ensure the device ID is included in the data structure
            if lmc_data and 'deviceStatus' in lmc_data:
                lmc_data['deviceStatus']['deviceId'] = self.lmc_api.device_id
            if wallbox_data and 'deviceStatus' in wallbox_data:
                wallbox_data['deviceStatus']['deviceId'] = self.wallbox_api.device_id
            
            return {
                "lmc": lmc_data,
                "wallbox": wallbox_data
            }
        except InvalidAuth as err:
            raise ConfigEntryAuthFailed from err
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    async def async_refresh(self):
        """Refresh data from Vool."""
        await self.async_request_refresh()