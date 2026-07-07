"""Modbus polling coordinator for Siemens Logo PLC."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, INPUT_START_ADDRESS, OUTPUT_START_ADDRESS

_LOGGER = logging.getLogger(__name__)


class LogoModbusCoordinator(DataUpdateCoordinator):
    """
    Polls discrete inputs and output coils from a Siemens Logo PLC over Modbus TCP.

    Opens a fresh TCP connection for each poll cycle to avoid stale connections
    and transaction ID collisions.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: int,
        num_inputs: int,
        num_outputs: int,
        update_interval: timedelta,
    ) -> None:
        self.host = host
        self.port = port
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs
        self._lock = asyncio.Lock()

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{host}_{port}",
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> dict[str, bool]:
        """Fetch all discrete inputs and output coil states."""
        from pymodbus.client import AsyncModbusTcpClient

        async with self._lock:
            client = AsyncModbusTcpClient(
                host=self.host,
                port=self.port,
                timeout=5,
            )
            try:
                connected = await client.connect()
                if not connected:
                    raise UpdateFailed(
                        f"Cannot connect to Siemens Logo at {self.host}:{self.port}"
                    )

                results: dict[str, bool] = {}

                # Read discrete inputs (function code 2)
                if self.num_inputs > 0:
                    response = await client.read_discrete_inputs(
                        address=INPUT_START_ADDRESS,
                        count=self.num_inputs,
                    )
                    if hasattr(response, "bits") and response.bits is not None:
                        for i in range(self.num_inputs):
                            results[f"input_{i + 1}"] = bool(response.bits[i])
                    else:
                        _LOGGER.warning(
                            "Error reading discrete inputs from %s: %s",
                            self.host, response,
                        )
                        for i in range(self.num_inputs):
                            results[f"input_{i + 1}"] = False

                # Read output coils (function code 1)
                if self.num_outputs > 0:
                    response = await client.read_coils(
                        address=OUTPUT_START_ADDRESS,
                        count=self.num_outputs,
                    )
                    if hasattr(response, "bits") and response.bits is not None:
                        for i in range(self.num_outputs):
                            results[f"output_{i + 1}"] = bool(response.bits[i])
                    else:
                        _LOGGER.warning(
                            "Error reading output coils from %s: %s",
                            self.host, response,
                        )
                        for i in range(self.num_outputs):
                            results[f"output_{i + 1}"] = False

                return results

            except UpdateFailed:
                raise
            except Exception as exc:
                raise UpdateFailed(
                    f"Error polling Siemens Logo at {self.host}:{self.port}: {exc}"
                ) from exc
            finally:
                client.close()

    async def async_write_coil(self, address: int, value: bool) -> bool:
        """Write a single coil (output) on the Logo PLC.

        Uses Modbus function code 5 (Write Single Coil).
        Returns True on success, False on failure.
        """
        from pymodbus.client import AsyncModbusTcpClient

        async with self._lock:
            client = AsyncModbusTcpClient(
                host=self.host,
                port=self.port,
                timeout=5,
            )
            try:
                connected = await client.connect()
                if not connected:
                    _LOGGER.error(
                        "Cannot connect to Siemens Logo at %s:%s to write coil",
                        self.host, self.port,
                    )
                    return False

                response = await client.write_coil(
                    address=address,
                    value=value,
                )

                if response.isError():
                    _LOGGER.error(
                        "Error writing coil at address %s on %s: %s",
                        address, self.host, response,
                    )
                    return False

                return True

            except Exception as exc:
                _LOGGER.error(
                    "Exception writing coil at address %s on %s: %s",
                    address, self.host, exc,
                )
                return False
            finally:
                client.close()
