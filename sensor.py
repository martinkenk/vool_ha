"""Sensor platform for Vool integration."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import (
    POWER_WATT,
    ELECTRIC_CURRENT_AMPERE,
    ELECTRIC_POTENTIAL_VOLT,
)
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import VoolCoordinator

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Vool sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        VoolPowerSensor(coordinator, "active_power", "Active Power", POWER_WATT, True),
        VoolPowerSensor(coordinator, "current_l1", "Current L1", ELECTRIC_CURRENT_AMPERE),
        VoolPowerSensor(coordinator, "current_l2", "Current L2", ELECTRIC_CURRENT_AMPERE),
        VoolPowerSensor(coordinator, "current_l3", "Current L3", ELECTRIC_CURRENT_AMPERE),
        VoolPowerSensor(coordinator, "voltage_l1", "Voltage L1", ELECTRIC_POTENTIAL_VOLT),
        VoolPowerSensor(coordinator, "voltage_l2", "Voltage L2", ELECTRIC_POTENTIAL_VOLT),
        VoolPowerSensor(coordinator, "voltage_l3", "Voltage L3", ELECTRIC_POTENTIAL_VOLT),
    ]

    async_add_entities(entities)

class VoolPowerSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Vool Power Sensor."""

    def __init__(self, coordinator: VoolCoordinator, key: str, name: str, unit: str, convert_to_watts: bool = False):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._key = key
        self._name = name
        self._unit = unit
        self._convert_to_watts = convert_to_watts
        self._attr_unique_id = f"{coordinator.api.device_id}_{key}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"Vool {self._name}"

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.coordinator.data:
            connectors = self.coordinator.data.get('deviceStatus', {}).get('connectors', [])
            if connectors:
                value = connectors[0].get(self._key)
                if value is not None and self._convert_to_watts:
                    return value * 1000  # Convert kW to W
                return value
        return None

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    @property
    def device_info(self):
        """Return device information about this Vool device."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.api.device_id)},
            name="Vool Power Monitor",
            manufacturer="Vool",
            model="Power Monitor",
            sw_version=self.coordinator.data.get("firmwareVersion") if self.coordinator.data else None,
        )