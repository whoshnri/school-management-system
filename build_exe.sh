#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

BUILD_WINDOWS=false
for arg in "$@"; do
  if [[ "$arg" == "--windows" || "$arg" == "-w" ]]; then
    BUILD_WINDOWS=true
  fi
done

if [ "$BUILD_WINDOWS" = true ]; then
  echo "Building GFA Admin Panel Windows executable using Wine..."
  echo
  
  # Check if Wine is available
  if ! command -v wine &> /dev/null && [ ! -f /usr/bin/wine ]; then
    echo "Error: Wine is not installed or not found in PATH."
    exit 1
  fi
  
  WINE_CMD="wine"
  if [ -f /usr/bin/wine ]; then
    WINE_CMD="/usr/bin/wine"
  fi
  
  # Run pyinstaller in wine
  $WINE_CMD python -m PyInstaller main.spec --distpath dist/android --noconfirm
  
  if [[ -f dist/android/GFA-Admin-Panel.exe ]]; then
    echo
    echo "Success: dist/android/GFA-Admin-Panel.exe"
  else
    echo "Windows build failed."
    exit 1
  fi
else
  echo "Building GFA Admin Panel Linux executable..."
  echo
  echo "Note: PyInstaller builds for the current OS only."
  echo "To build the Windows executable on Linux using Wine, run: ./build_exe.sh --windows"
  echo
  
  if [[ ! -d venv ]]; then
    python -m venv venv
  fi
  
  # shellcheck disable=SC1091
  source venv/bin/activate
  python -m pip install --upgrade pip
  pip install -r req.txt pyinstaller
  
  pyinstaller main.spec --distpath dist/android --noconfirm
  
  if [[ -f dist/android/GFA-Admin-Panel ]]; then
    echo
    echo "Success: dist/android/GFA-Admin-Panel"
  else
    echo "Linux build failed."
    exit 1
  fi
fi
