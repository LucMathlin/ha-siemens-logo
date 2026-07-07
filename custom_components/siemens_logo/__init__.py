"""Siemens Logo PLC Modbus TCP integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant

from .const import (
    CONF_NAME,
    CONF_NUM_INPUTS,
    CONF_NUM_OUTPUTS,
    DOMAIN,
)
from .coordinator import LogoModbusCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.BINARY_SENSOR, Platform.SWITCH]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Siemens Logo PLC from a config entry."""
    host: str = entry.data[CONF_HOST]
    port: int = entry.data[CONF_PORT]
    num_inputs: int = entry.data[CONF_NUM_INPUTS]
    num_outputs: int = entry.data[CONF_NUM_OUTPUTS]

    coordinator = LogoModbusCoordinator(
        hass=hass,
        host=host,
        port=port,
        num_inputs=num_inputs,
        num_outputs=num_outputs,
        update_interval=timedelta(seconds=1),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
