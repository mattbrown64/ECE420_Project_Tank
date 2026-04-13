#!/bin/bash
set -e

# Change to the project directory.
cd "$(dirname "$0")"

# Activate virtual environment if it exists.
if [ -f "venv/bin/activate" ]; then
    # shellcheck source=/dev/null
    source "venv/bin/activate"
fi

# Launch the main Python program.
exec python3 main.py
