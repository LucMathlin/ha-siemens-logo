"""Binary sensor platform for Siemens Logo PLC — discrete inputs."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_NAME, CONF_NUM_INPUTS, DOMAIN
from .coordinator import LogoModbusCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Logo PLC binary sensors (discrete inputs) from a config entry."""
    coordinator: LogoModbusCoordinator = hass.data[DOMAIN][entry.entry_id]
    plc_name: str = entry.data[CONF_NAME]
    host: str = entry.data[CONF_HOST]
    port: int = entry.data[CONF_PORT]
    num_inputs: int = entry.data[CONF_NUM_INPUTS]

    entities: list[LogoInputSensor] = []

    for i in range(1, num_inputs + 1):
        entities.append(
            LogoInputSensor(
                coordinator=coordinator,
                entry_id=entry.entry_id,
                plc_name=plc_name,
                host=host,
                port=port,
                input_number=i,
            )
        )

    async_add_entities(entities)


class LogoInputSensor(CoordinatorEntity, BinarySensorEntity):
    """Represents a discrete input (I1-I24) on the Siemens Logo PLC."""

    def __init__(
        self,
        coordinator: LogoModbusCoordinator,
        entry_id: str,
        plc_name: str,
        host: str,
        port: int,
        input_number: int,
    ) -> None:
        super().__init__(coordinator)

        self._input_number = input_number
        self._key = f"input_{input_number}"

        self._attr_name = f"{plc_name} Input I{input_number}"
        self._attr_unique_id = f"{entry_id}_input_{input_number}"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{host}_{port}")},
            name=plc_name,
            manufacturer="Siemens",
            model="Logo 8 (Modbus TCP)",
        )

    @property
    def is_on(self) -> bool | None:
        """Return True if the input is active (high)."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._key)

    @property
    def available(self) -> bool:
        """Mark unavailable if the coordinator failed."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
            and self._key in self.coordinator.data
        )
