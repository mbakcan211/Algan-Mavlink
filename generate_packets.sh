#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# --- Configuration ---
DIALECT_NAME="algan_uav"
XML_DIR="message_definitions/v1.0"
OUT_DIR=".."
PROTOCOL="2.0"

# --- Setup ---
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "   Algan UAV MAVLink Generator"
echo "=========================================="

# Check if pymavlink is installed
if ! python3 -c "import pymavlink" &> /dev/null; then
    echo "[ERROR] pymavlink not found. Please run: pip install pymavlink lxml"
    exit 1
fi

# Determine the correct generator command
# We check if 'mavgen.py' is in the system path. If not, we try to find it manually.
if command -v mavgen.py &> /dev/null; then
    MAVGEN_CMD="mavgen.py"
else
    # Fallback: sometimes it's just 'mavgen' (no .py) or we use the module approach as a last resort
    if command -v mavgen &> /dev/null; then
        MAVGEN_CMD="mavgen"
    else
        MAVGEN_CMD="python3 -m pymavlink.tools.mavgen"
    fi
fi
echo "[INFO] Using generator command: $MAVGEN_CMD"

# Create output directories
mkdir -p "$OUT_DIR/mavlink_python_library_v2"
mkdir -p "$OUT_DIR/mavlink_c_library_v2"

# --- 1. Generate Python Bindings ---
echo "[INFO] Generating Python bindings..."
$MAVGEN_CMD \
    --lang=Python \
    --wire-protocol=$PROTOCOL \
    --output="$OUT_DIR/mavlink_python_library_v2/${DIALECT_NAME}.py" \
    "$XML_DIR/${DIALECT_NAME}.xml"

# --- 2. Generate C Headers (for PX4/Embedded) ---
echo "[INFO] Generating C headers..."
$MAVGEN_CMD \
    --lang=C \
    --wire-protocol=$PROTOCOL \
    --output="$OUT_DIR/mavlink_c_library_v2" \
    "$XML_DIR/${DIALECT_NAME}.xml"

echo "=========================================="
echo "[SUCCESS] Generation Complete!"
echo "Python file: $OUT_DIR/mavlink_python_library_v2/${DIALECT_NAME}.py"
echo "C Headers:   $OUT_DIR/mavlink_c_library_v2/"
echo "=========================================="