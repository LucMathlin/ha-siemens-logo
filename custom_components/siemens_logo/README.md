# Siemens Logo 8 PLC — Home Assistant Custom Integration

Connects to a Siemens Logo 8 PLC via Modbus TCP, exposing discrete inputs as
binary sensors and digital outputs as controllable switches.

## Features

- **Discrete Inputs (I1–I24)** — read-only binary sensors showing the state of
  each physical input on the Logo and any expansion modules.
- **Digital Outputs (Q1–Q20)** — switches that let you turn outputs on/off
  directly from Home Assistant via Modbus coil writes.
- **Configurable I/O count** — set the number of inputs and outputs during setup
  to match your actual hardware (base unit + DM modules).
- **Fast polling** — 1-second update interval for responsive state tracking.

## Modbus Address Mapping

| Address Type | Range   | Modbus Address        | Direction | Usage |
|---|---|---|---|---|
| I (Inputs)   | 1–24    | Discrete Input 1–24   | Read      | Binary sensors |
| Q (Outputs)  | 1–20    | Coil 8193–8212        | Read      | Read actual output state |
| M (Markers)  | 1–20    | Coil 8257–8276        | Write     | Control outputs via markers |

Outputs are controlled indirectly: HA writes to M flag coils (8257+) using
Modbus function code 5, and the Logo program wires M1→Q1, M2→Q2, etc.

## Prerequisites

- Siemens Logo 8 with Modbus TCP server enabled
- Logo must be reachable on the network from your Home Assistant host
- Enable the Modbus server in Logo!Soft Comfort under
  **Network → Connections → Modbus Connections**

## Installation

### HACS (recommended)
1. Add this repo as a custom repository in HACS (type: Integration).
2. Install **Siemens Logo PLC (Modbus TCP)**.
3. Restart Home Assistant.

### Manual
1. Copy the `siemens_logo` folder into your `config/custom_components/` directory.
2. Restart Home Assistant.

## Setup

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **Siemens Logo PLC**.
3. Fill in the form:

   | Field | Example | Notes |
   |---|---|---|
   | PLC Name | `Logo-1` | Used as a prefix for all entity names |
   | IP Address | `192.168.1.100` | Logo's IP on your network |
   | Modbus TCP Port | `502` | Default is 502 |
   | Number of Inputs | `8` | How many DI your Logo + modules have |
   | Number of Outputs | `4` | How many Q your Logo + modules have |

4. Click **Submit**. The integration tests the connection before saving.

## Entity Naming

- Inputs: `<PLC Name> Input I1`, `<PLC Name> Input I2`, etc.
- Outputs: `<PLC Name> Output Q1`, `<PLC Name> Output Q2`, etc.

## Controlling Outputs

Outputs appear as standard Home Assistant switches. You can:
- Toggle them from the UI
- Use them in automations (`switch.turn_on` / `switch.turn_off`)
- Include them in scripts and scenes

**Important:** This integration writes to M flag coils (markers), not directly
to Q outputs. You need a simple Logo program that passes markers through to
outputs:

```
M1 → Q1
M2 → Q2
M3 → Q3
...
```

In Logo!Soft Comfort, this is just a direct connection from each Network Input
(M flag) block to the corresponding output. The actual Q output state is read
back to confirm the switch state in HA.

## Polling Interval

All inputs and outputs are polled every **1 second**.

## Requirements

- Home Assistant 2023.6 or newer
- `pymodbus >= 3.11.2` (installed automatically)
- Siemens Logo 8 with firmware supporting Modbus TCP server
