"""Sensor platform for Vool integration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfPower,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import VoolCoordinator


@dataclass(frozen=True, kw_only=True)
class VoolSensorEntityDescription(SensorEntityDescription):
    """Describes a VOOL sensor entity."""

    value_fn: Callable[[dict[str, Any]], Any] | None = None
    convert_kw: bool = False


# Sensor definitions matching the reference integration's power units
SENSOR_DESCRIPTIONS: tuple[VoolSensorEntityDescription, ...] = (
    VoolSensorEntityDescription(
        key="active_power",
        translation_key="active_power",
        name="Active Power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("active_power"),
        convert_kw=False,  # Already in kW from API
    ),
    VoolSensorEntityDescription(
        key="current_l1",
        translation_key="current_l1",
        name="Current L1",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("current_l1"),
    ),
    VoolSensorEntityDescription(
        key="current_l2",
        translation_key="current_l2",
        name="Current L2",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("current_l2"),
    ),
    VoolSensorEntityDescription(
        key="current_l3",
        translation_key="current_l3",
        name="Current L3",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("current_l3"),
    ),
    VoolSensorEntityDescription(
        key="voltage_l1",
        translation_key="voltage_l1",
        name="Voltage L1",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("voltage_l1"),
    ),
    VoolSensorEntityDescription(
        key="voltage_l2",
        translation_key="voltage_l2",
        name="Voltage L2",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("voltage_l2"),
    ),
    VoolSensorEntityDescription(
        key="voltage_l3",
        translation_key="voltage_l3",
        name="Voltage L3",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("voltage_l3"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Vool sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for device_type in ['lmc', 'wallbox']:
        for description in SENSOR_DESCRIPTIONS:
            entities.append(VoolSensor(coordinator, device_type, description))

    async_add_entities(entities)


class VoolSensor(CoordinatorEntity, SensorEntity):
    """Representation of a VOOL Sensor."""

    entity_description: VoolSensorEntityDescription

    def __init__(
        self,
        coordinator: VoolCoordinator,
        device_type: str,
        description: VoolSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._device_type = device_type
        self.entity_description = description
        
        # Safely get the device ID, falling back to the one from config if not found in data
        device_id = self._get_device_id(coordinator, device_type)
        self._attr_unique_id = f"{device_id}_{description.key}"
        self._attr_name = f"VOOL {device_type.upper()} {description.name}"

    def _get_device_id(self, coordinator: VoolCoordinator, device_type: str) -> str:
        """Safely get the device ID."""
        try:
            return coordinator.data[device_type]['deviceStatus']['deviceId']
        except (KeyError, TypeError):
            # Fallback to the device ID from the config entry
            return getattr(coordinator, f"{device_type}_api").device_id

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if self.coordinator.data:
            try:
                connectors = self.coordinator.data[self._device_type]['deviceStatus']['connectors']
                if connectors and self.entity_description.value_fn:
                    value = self.entity_description.value_fn(connectors[0])
                    return value
            except (KeyError, TypeError, IndexError):
                pass
        return None

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this VOOL device."""
        device_id = self._get_device_id(self.coordinator, self._device_type)
        return DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=f"VOOL {self._device_type.upper()}",
            manufacturer="VOOL",
            model="Charger" if self._device_type == "wallbox" else "LMC",
            sw_version=self.coordinator.data[self._device_type].get("firmwareVersion") if self.coordinator.data else None,
        )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success