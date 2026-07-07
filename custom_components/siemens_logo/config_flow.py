"""Config flow for Siemens Logo PLC Modbus integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
)

from .const import (
    CONF_NAME,
    CONF_NUM_INPUTS,
    CONF_NUM_OUTPUTS,
    DEFAULT_NUM_INPUTS,
    DEFAULT_NUM_OUTPUTS,
    DEFAULT_PORT,
    DOMAIN,
    MAX_INPUTS,
    MAX_OUTPUTS,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): TextSelector(),
        vol.Required(CONF_HOST): TextSelector(),
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): NumberSelector(
            NumberSelectorConfig(min=1, max=65535, step=1, mode=NumberSelectorMode.BOX)
        ),
        vol.Optional(CONF_NUM_INPUTS, default=DEFAULT_NUM_INPUTS): NumberSelector(
            NumberSelectorConfig(min=0, max=MAX_INPUTS, step=1, mode=NumberSelectorMode.BOX)
        ),
        vol.Optional(CONF_NUM_OUTPUTS, default=DEFAULT_NUM_OUTPUTS): NumberSelector(
            NumberSelectorConfig(min=0, max=MAX_OUTPUTS, step=1, mode=NumberSelectorMode.BOX)
        ),
    }
)


async def _test_connection(hass: HomeAssistant, host: str, port: int) -> str | None:
    """Try to connect to the Logo PLC. Returns None on success or an error key."""
    from pymodbus.client import AsyncModbusTcpClient
    from pymodbus.exceptions import ConnectionException, ModbusIOException

    client = AsyncModbusTcpClient(host=host, port=port, timeout=5)
    try:
        connected = await client.connect()
        if not connected:
            return "cannot_connect"

        # Small delay to let the connection stabilise
        import asyncio
        await asyncio.sleep(0.5)

        if not client.connected:
            return "cannot_connect"

        # Try reading the first discrete input to verify communication
        try:
            result = await client.read_discrete_inputs(address=0, count=1)
            if not result.isError():
                return None
        except (ConnectionException, ModbusIOException):
            pass

        # Fallback: try reading an output coil instead
        try:
            result = await client.read_coils(address=8192, count=1)
            if not result.isError():
                return None
        except (ConnectionException, ModbusIOException):
            pass

        return "cannot_communicate"

    except (ConnectionRefusedError, ConnectionException, OSError):
        return "cannot_connect"
    except Exception as exc:
        _LOGGER.exception(
            "Unexpected error testing connection to %s:%s: %s",
            host, port, exc,
        )
        return "unknown"
    finally:
        client.close()


class SiemensLogoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for Siemens Logo PLC."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step — connection details and I/O count."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host: str = user_input[CONF_HOST].strip()
            port: int = int(user_input[CONF_PORT])
            name: str = user_input[CONF_NAME].strip()
            num_inputs: int = int(user_input[CONF_NUM_INPUTS])
            num_outputs: int = int(user_input[CONF_NUM_OUTPUTS])

            await self.async_set_unique_id(f"{host}_{port}")
            self._abort_if_unique_id_configured()

            error = await _test_connection(self.hass, host, port)
            if error:
                errors["base"] = error
            else:
                return self.async_create_entry(
                    title=name,
                    data={
                        CONF_NAME: name,
                        CONF_HOST: host,
                        CONF_PORT: port,
                        CONF_NUM_INPUTS: num_inputs,
                        CONF_NUM_OUTPUTS: num_outputs,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
