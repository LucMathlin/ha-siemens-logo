"""Constants for the Siemens Logo PLC Modbus integration."""

DOMAIN = "siemens_logo"

CONF_NAME = "name"
CONF_NUM_INPUTS = "num_inputs"
CONF_NUM_OUTPUTS = "num_outputs"

DEFAULT_PORT = 502
DEFAULT_NUM_INPUTS = 24
DEFAULT_NUM_OUTPUTS = 20

# Modbus address mapping for Siemens Logo 8
# From the Logo manual:
#   I  (Discrete Inputs):  DI address 1-24       (Read only, bit)
#   Q  (Outputs):          Coil address 8193-8212 (Read/Write, bit)
#   M  (Flags/Markers):    Coil address 8257-8320 (Read/Write, bit)
#   AI (Analog Inputs):    Input Register 1-8     (Read only, word)
#   AQ (Analog Outputs):   Holding Register 513-520 (Read/Write, word)

# Digital Inputs (I1-I24) — Discrete Input addresses 1-24 (0-indexed: 0-23)
# Read via Modbus function code 2 (Read Discrete Inputs)
INPUT_START_ADDRESS = 0  # 0-indexed (address 1 in 1-indexed)

# Digital Outputs (Q1-Q20) — Coil addresses 8193-8212 (0-indexed: 8192-8211)
# Read via Modbus function code 1 to get actual output state
OUTPUT_START_ADDRESS = 8192  # 0-indexed (address 8193 in 1-indexed)

# M Flags (Markers) — Coil addresses 8257-8320 (0-indexed: 8256-8319)
# Write via Modbus function code 5 to control outputs indirectly.
# The Logo program should wire M1->Q1, M2->Q2, etc.
MARKER_START_ADDRESS = 8256  # 0-indexed (address 8257 in 1-indexed)

MAX_INPUTS = 24
MAX_OUTPUTS = 20
