#!/usr/bin/env bash
# ============================================================================
# Doqurix - macOS Build Script
#
# Builds a standalone .app bundle and a .dmg installer.
# Run this on a Mac (Intel or Apple Silicon) from EITHER:
#     bash macos/build_macos.sh
# or:
#     cd macos && bash build_macos.sh
#
# Requirements:
#   - macOS 10.15+ (Catalina or newer)
#   - Python 3.10 or 3.11 (recommended: brew install python@3.11)
#   - Xcode Command Line Tools: xcode-select --install
# ============================================================================

set -euo pipefail

# Always run from the project root (parent of this script's directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

APP_NAME="Doqurix"
VERSION="1.0.0"
DMG_NAME="${APP_NAME}_Setup_v${VERSION}"
APP_PATH="dist/${APP_NAME}.app"
DMG_DIR="dmg_temp"
DMG_OUTPUT="installer_output/${DMG_NAME}.dmg"

echo "========================================"
echo "  Doqurix macOS Build"
echo "  Project root: $PROJECT_ROOT"
echo "  Architecture: $(uname -m)"
echo "========================================"

# ---------------------------------------------------------------------------
# 1. Python check
# ---------------------------------------------------------------------------
if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: Python 3 is not installed."
    echo "Install with: brew install python@3.11"
    exit 1
fi
echo "Using: $(python3 --version)"

if [[ ! -f "main.py" ]]; then
    echo "ERROR: main.py not found in $PROJECT_ROOT"
    exit 1
fi

# ---------------------------------------------------------------------------
# 2. Virtual environment
# ---------------------------------------------------------------------------
echo ""
echo "[1/6] Setting up virtual environment..."
if [[ ! -d "venv" ]]; then
    python3 -m venv venv
    echo "  - Created venv"
else
    echo "  - venv already exists"
fi
# shellcheck disable=SC1091
source venv/bin/activate

# ---------------------------------------------------------------------------
# 3. Dependencies
# ---------------------------------------------------------------------------
echo ""
echo "[2/6] Installing dependencies..."
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt
pip install pyinstaller
echo "  - Dependencies installed"

# ---------------------------------------------------------------------------
# 4. Icon conversion (.ico -> .icns)
# ---------------------------------------------------------------------------
echo ""
echo "[3/6] Preparing app icon..."
if [[ -f "app_icon.icns" ]]; then
    echo "  - app_icon.icns already present"
elif [[ -f "app_icon.ico" ]] && command -v sips >/dev/null 2>&1; then
    ICONSET="app_icon.iconset"
    rm -rf "$ICONSET"
    mkdir -p "$ICONSET"
    sips -z 16 16     app_icon.ico --out "$ICONSET/icon_16x16.png"     >/dev/null 2>&1 || true
    sips -z 32 32     app_icon.ico --out "$ICONSET/icon_16x16@2x.png"  >/dev/null 2>&1 || true
    sips -z 32 32     app_icon.ico --out "$ICONSET/icon_32x32.png"     >/dev/null 2>&1 || true
    sips -z 64 64     app_icon.ico --out "$ICONSET/icon_32x32@2x.png"  >/dev/null 2>&1 || true
    sips -z 128 128   app_icon.ico --out "$ICONSET/icon_128x128.png"   >/dev/null 2>&1 || true
    sips -z 256 256   app_icon.ico --out "$ICONSET/icon_128x128@2x.png">/dev/null 2>&1 || true
    sips -z 256 256   app_icon.ico --out "$ICONSET/icon_256x256.png"   >/dev/null 2>&1 || true
    sips -z 512 512   app_icon.ico --out "$ICONSET/icon_256x256@2x.png">/dev/null 2>&1 || true
    sips -z 512 512   app_icon.ico --out "$ICONSET/icon_512x512.png"   >/dev/null 2>&1 || true
    sips -z 1024 1024 app_icon.ico --out "$ICONSET/icon_512x512@2x.png">/dev/null 2>&1 || true
    iconutil -c icns "$ICONSET" -o app_icon.icns 2>/dev/null \
        && echo "  - Created app_icon.icns" \
        || echo "  - WARNING: Could not create .icns (using default icon)"
    rm -rf "$ICONSET"
else
    echo "  - WARNING: No icon source found; using PyInstaller default"
fi

# ---------------------------------------------------------------------------
# 5. PyInstaller build
# ---------------------------------------------------------------------------
echo ""
echo "[4/6] Building app bundle with PyInstaller..."
rm -rf build/Doqurix dist/Doqurix dist/Doqurix.app
pyinstaller --noconfirm --clean macos/Doqurix_macOS.spec
if [[ ! -d "$APP_PATH" ]]; then
    echo "ERROR: PyInstaller did not produce $APP_PATH"
    exit 1
fi
echo "  - Built $APP_PATH"

# Make executable bit explicit (sometimes lost)
chmod +x "$APP_PATH/Contents/MacOS/${APP_NAME}" 2>/dev/null || true

# ---------------------------------------------------------------------------
# 6. DMG installer
# ---------------------------------------------------------------------------
echo ""
echo "[5/6] Creating DMG installer..."
mkdir -p installer_output
rm -f "$DMG_OUTPUT"
rm -rf "$DMG_DIR"
mkdir -p "$DMG_DIR"
cp -R "$APP_PATH" "$DMG_DIR/"
ln -s /Applications "$DMG_DIR/Applications"

if command -v create-dmg >/dev/null 2>&1; then
    create-dmg \
        --volname "$APP_NAME" \
        ${ICON_ARG:-} \
        --window-pos 200 120 \
        --window-size 600 400 \
        --icon-size 100 \
        --icon "${APP_NAME}.app" 150 185 \
        --app-drop-link 450 185 \
        --hide-extension "${APP_NAME}.app" \
        "$DMG_OUTPUT" \
        "$DMG_DIR" \
        || hdiutil create -volname "$APP_NAME" -srcfolder "$DMG_DIR" -ov -format UDZO "$DMG_OUTPUT"
else
    hdiutil create -volname "$APP_NAME" -srcfolder "$DMG_DIR" -ov -format UDZO "$DMG_OUTPUT"
fi
rm -rf "$DMG_DIR"
echo "  - Created $DMG_OUTPUT"

# ---------------------------------------------------------------------------
# 7. Optional: ad-hoc codesign so Gatekeeper doesn't kill the app on first run
#    (Real distribution still requires a Developer ID + notarization.)
# ---------------------------------------------------------------------------
echo ""
echo "[6/6] Ad-hoc signing app bundle..."
codesign --force --deep --sign - "$APP_PATH" >/dev/null 2>&1 \
    && echo "  - Ad-hoc signed" \
    || echo "  - WARNING: codesign failed (app will still run, may show Gatekeeper warning)"

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
echo ""
echo "========================================"
echo "  BUILD SUCCESSFUL"
echo "========================================"
echo "App:       $APP_PATH"
echo "Installer: $DMG_OUTPUT"
[[ -d "$APP_PATH" ]] && echo "App size:  $(du -sh "$APP_PATH" | cut -f1)"
[[ -f "$DMG_OUTPUT" ]] && echo "DMG size:  $(du -sh "$DMG_OUTPUT" | cut -f1)"
echo ""
echo "Test:   open \"$APP_PATH\""
echo "Notes:"
echo "  - First launch downloads the LLM (~1GB) into the user data folder."
echo "  - On first run users may need to right-click the app and choose Open"
echo "    (Gatekeeper bypass for unsigned apps)."
echo ""
