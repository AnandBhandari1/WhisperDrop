#!/bin/bash

# WhisperDrop - Speak. Drop. Done.

echo "Starting WhisperDrop..."
echo "Press F8 anywhere to start/stop recording"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed."
    echo "Install it: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check if xdotool is installed
if ! command -v xdotool &> /dev/null; then
    echo "Error: xdotool is not installed."
    echo "Install it: sudo apt install xdotool"
    exit 1
fi

uv run python app.py
