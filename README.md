# Siemens Logo PLC (Modbus TCP)

[![Validate](https://github.com/LucMathlin/ha-siemens-logo/actions/workflows/validate.yml/badge.svg)](https://github.com/LucMathlin/ha-siemens-logo/actions/workflows/validate.yml)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

A Home Assistant custom integration for Siemens LOGO! PLCs via Modbus TCP.

## Supported Devices

- Siemens LOGO! 8 series (0BA8)
- Siemens LOGO! 8.3 (0BA8.3)
- Other LOGO! models with Modbus TCP support

## Features

- Read digital inputs and outputs as binary sensors
- Control digital outputs via switch entities
- Read analogue inputs/outputs as sensors
- Configurable Modbus register mapping
- Configurable via the Home Assistant UI (config flow)

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots menu → **Custom repositories**
3. Add `https://github.com/LucMathlin/ha-siemens-logo` with category **Integration**
4. Search for "Siemens Logo" and install
5. Restart Home Assistant

### Manual

1. Copy `custom_components/siemens_logo/` to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for "Siemens Logo"
3. Enter the Modbus TCP host and port of your LOGO! PLC
4. Configure the registers/coils you want to expose

## Requirements

- Modbus TCP connectivity to the LOGO! PLC
- Modbus server enabled on the LOGO! device
- `pymodbus>=3.11.2` (installed automatically)
