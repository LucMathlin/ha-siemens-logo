"""Switch platform for Siemens Logo PLC — digital outputs (coils)."""
from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_NAME, CONF_NUM_OUTPUTS, DOMAIN, MARKER_START_ADDRESS, OUTPUT_START_ADDRESS
from .coordinator import LogoModbusCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Logo PLC switches (digital outputs) from a config entry."""
    coordinator: LogoModbusCoordinator = hass.data[DOMAIN][entry.entry_id]
    plc_name: str = entry.data[CONF_NAME]
    host: str = entry.data[CONF_HOST]
    port: int = entry.data[CONF_PORT]
    num_outputs: int = entry.data[CONF_NUM_OUTPUTS]

    entities: list[LogoOutputSwitch] = []

    for i in range(1, num_outputs + 1):
        entities.append(
            LogoOutputSwitch(
                coordinator=coordinator,
                entry_id=entry.entry_id,
                plc_name=plc_name,
                host=host,
                port=port,
                output_number=i,
            )
        )

    async_add_entities(entities)


class LogoOutputSwitch(CoordinatorEntity, SwitchEntity):
    """Represents a digital output (Q1-Q20) on the Siemens Logo PLC.

    Outputs are controlled by writing to M flag coils at addresses 8257+
    (0-indexed: 8256+). The Logo program should wire M1->Q1, M2->Q2, etc.
    The actual output state is read back from Q coil addresses 8193-8212
    during each coordinator poll cycle.
    """

    def __init__(
        self,
        coordinator: LogoModbusCoordinator,
        entry_id: str,
        plc_name: str,
        host: str,
        port: int,
        output_number: int,
    ) -> None:
        super().__init__(coordinator)

        self._output_number = output_number
        self._key = f"output_{output_number}"
        # Write to M flag, read state from Q coil
        self._marker_address = MARKER_START_ADDRESS + (output_number - 1)

        self._attr_name = f"{plc_name} Output Q{output_number}"
        self._attr_unique_id = f"{entry_id}_output_{output_number}"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{host}_{port}")},
            name=plc_name,
            manufacturer="Siemens",
            model="Logo 8 (Modbus TCP)",
        )

    @property
    def is_on(self) -> bool | None:
        """Return True if the output coil is energised."""
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

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the output on by writing True to the M flag coil."""
        success = await self.coordinator.async_write_coil(
            address=self._marker_address, value=True
        )
        if success:
            # Optimistically update local state
            self.coordinator.data[self._key] = True
            self.async_write_ha_state()
            # Request a refresh to confirm the actual Q output state
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the output off by writing False to the M flag coil."""
        success = await self.coordinator.async_write_coil(
            address=self._marker_address, value=False
        )
        if success:
            # Optimistically update local state
            self.coordinator.data[self._key] = False
            self.async_write_ha_state()
            # Request a refresh to confirm the actual Q output state
            await self.coordinator.async_request_refresh()
