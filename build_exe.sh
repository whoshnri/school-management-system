#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

echo "Building GFA Admin Panel executable..."
echo
echo "Note: PyInstaller builds for the current OS only."
echo "Run build_exe.bat on Windows to produce GFA-Admin-Panel.exe"
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
elif [[ -f dist/android/GFA-Admin-Panel.exe ]]; then
  echo
  echo "Success: dist/android/GFA-Admin-Panel.exe"
else
  echo "Build failed."
  exit 1
fi

