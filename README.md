#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# --- Configuration ---
DIALECT_NAME="algan_uav"
XML_DIR="../definitions"
OUT_DIR="../generated_build"
# Ensure we use MAVLink v2.0
PROTOCOL="2.0"

# --- Setup ---
# Get the absolute path of the script directory to ensure relative paths work
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "   Algan UAV MAVLink Generator"
echo "=========================================="

# Check if pymavlink is installed
if ! python3 -c "import pymavlink" &> /dev/null; then
    echo "[ERROR] pymavlink not found. Installing..."
    pip install pymavlink
fi

# Create output directories if they don't exist
mkdir -p "$OUT_DIR/python"
mkdir -p "$OUT_DIR/c_library"

# --- 1. Generate Python Bindings ---
echo "[INFO] Generating Python bindings..."
python3 -m pymavlink.tools.mavgen \
    --lang=Python \
    --wire-protocol=$PROTOCOL \
    --output="$OUT_DIR/python/${DIALECT_NAME}.py" \
    "$XML_DIR/${DIALECT_NAME}.xml"

# --- 2. Generate C Headers (for PX4/Embedded) ---
echo "[INFO] Generating C headers..."
python3 -m pymavlink.tools.mavgen \
    --lang=C \
    --wire-protocol=$PROTOCOL \
    --output="$OUT_DIR/c_library" \
    "$XML_DIR/${DIALECT_NAME}.xml"

echo "=========================================="
echo "[SUCCESS] Generation Complete!"
echo "Python file: $OUT_DIR/python/${DIALECT_NAME}.py"
echo "C Headers:   $OUT_DIR/c_library/${DIALECT_NAME}"
echo "=========================================="