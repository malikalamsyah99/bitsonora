#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP="$ROOT/dist/Bitsonora.app"
STAGING="$ROOT/build/dmg"
DMG="$ROOT/dist/Bitsonora-macOS.dmg"

if [[ ! -d "$APP" ]]; then
    echo "ERROR: Bitsonora.app not found at:"
    echo "$APP"
    echo "Build the app first using PyInstaller."
    exit 1
fi

mkdir -p "$ROOT/dist"
rm -rf "$STAGING"
mkdir -p "$STAGING"

echo "Copying Bitsonora.app..."
ditto "$APP" "$STAGING/Bitsonora.app"

echo "Creating Applications shortcut..."
ln -s /Applications "$STAGING/Applications"

echo "Creating DMG..."
rm -f "$DMG"
hdiutil create \
    -volname "Bitsonora" \
    -srcfolder "$STAGING" \
    -ov \
    -format UDZO \
    "$DMG"

echo "Verifying DMG..."
hdiutil verify "$DMG"

echo
echo "DMG created successfully:"
echo "$DMG"
ls -lh "$DMG"

echo
echo "SHA-256:"
shasum -a 256 "$DMG"
