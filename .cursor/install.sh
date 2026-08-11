#!/usr/bin/env bash
# Idempotent Cloud Agent bootstrap for the GFA Admin Panel (School Management System).
# Prepares the Python virtual environment and installs pinned dependencies.
set -euo pipefail

cd "$(dirname "$0")/.."

# Tkinter (customtkinter/tkcalendar) is a system-level dependency that pip cannot
# provide. It is baked into the environment snapshot, but re-install defensively so
# the script also works on a plain base image. Skip silently when sudo/apt is absent.
if command -v apt-get >/dev/null 2>&1 && command -v sudo >/dev/null 2>&1; then
  if ! python3 -c "import tkinter" >/dev/null 2>&1; then
    sudo apt-get update -qq
    sudo apt-get install -y -qq python3-tk python3-venv
  fi
fi

# Create the virtual environment if it does not already exist.
if [ ! -x "venv/bin/python" ]; then
  python3 -m venv venv
fi

venv/bin/python -m pip install --upgrade pip
venv/bin/pip install -r req.txt

echo "Install complete. Activate with: source venv/bin/activate"
