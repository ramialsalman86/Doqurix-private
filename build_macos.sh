#!/bin/bash
# ============================================
# Doqurix macOS Build Script
# Run this on a Mac to build the application
# ============================================

set -e  # Exit on error

echo "========================================"
echo "  Doqurix macOS Build Script"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo "Please install Python 3.10+ from python.org or via Homebrew:"
    echo "  brew install python@3.11"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "Using: $PYTHON_VERSION"

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "ERROR: main.py not found!"
    echo "Please run this script from the Doqurix project directory."
    exit 1
fi

# Step 1: Create virtual environment if it doesn't exist
echo ""
echo "[1/6] Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "  ✓ Created virtual environment"
else
    echo "  ✓ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Step 2: Install dependencies
echo ""
echo "[2/6] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller
echo "  ✓ Dependencies installed"

# Step 3: Convert icon to macOS format (.icns)
echo ""
echo "[3/6] Converting icon..."
if [ -f "app_icon.ico" ]; then
    # Create iconset directory
    mkdir -p app_icon.iconset
    
    # Check if we have imagemagick or can use sips
    if command -v sips &> /dev/null; then
        # Use sips (built into macOS) to convert
        sips -z 16 16     app_icon.ico --out app_icon.iconset/icon_16x16.png 2>/dev/null || true
        sips -z 32 32     app_icon.ico --out app_icon.iconset/icon_16x16@2x.png 2>/dev/null || true
        sips -z 32 32     app_icon.ico --out app_icon.iconset/icon_32x32.png 2>/dev/null || true
        sips -z 64 64     app_icon.ico --out app_icon.iconset/icon_32x32@2x.png 2>/dev/null || true
        sips -z 128 128   app_icon.ico --out app_icon.iconset/icon_128x128.png 2>/dev/null || true
        sips -z 256 256   app_icon.ico --out app_icon.iconset/icon_128x128@2x.png 2>/dev/null || true
        sips -z 256 256   app_icon.ico --out app_icon.iconset/icon_256x256.png 2>/dev/null || true
        sips -z 512 512   app_icon.ico --out app_icon.iconset/icon_256x256@2x.png 2>/dev/null || true
        sips -z 512 512   app_icon.ico --out app_icon.iconset/icon_512x512.png 2>/dev/null || true
        sips -z 1024 1024 app_icon.ico --out app_icon.iconset/icon_512x512@2x.png 2>/dev/null || true
        
        # Convert iconset to icns
        iconutil -c icns app_icon.iconset -o app_icon.icns 2>/dev/null || {
            echo "  ⚠ Could not create .icns file, will use default icon"
        }
        
        rm -rf app_icon.iconset
        echo "  ✓ Icon converted"
    else
        echo "  ⚠ sips not available, will use default icon"
    fi
else
    echo "  ⚠ app_icon.ico not found, will use default icon"
fi

# Step 4: Build with PyInstaller
echo ""
echo "[4/6] Building application with PyInstaller..."
pyinstaller --noconfirm Doqurix_macOS.spec
echo "  ✓ Application built"

# Step 5: Create DMG installer
echo ""
echo "[5/6] Creating DMG installer..."

APP_NAME="Doqurix"
DMG_NAME="Doqurix_Setup_v1.0.0"
APP_PATH="dist/${APP_NAME}.app"
DMG_DIR="dmg_temp"
DMG_OUTPUT="installer_output/${DMG_NAME}.dmg"

# Create output directory
mkdir -p installer_output

# Remove any existing DMG
rm -f "$DMG_OUTPUT"

# Create temp directory for DMG contents
rm -rf "$DMG_DIR"
mkdir -p "$DMG_DIR"

# Copy app to DMG directory
cp -R "$APP_PATH" "$DMG_DIR/"

# Create symlink to Applications folder
ln -s /Applications "$DMG_DIR/Applications"

# Create DMG
if command -v create-dmg &> /dev/null; then
    # Use create-dmg if available (brew install create-dmg)
    create-dmg \
        --volname "$APP_NAME" \
        --volicon "app_icon.icns" \
        --window-pos 200 120 \
        --window-size 600 400 \
        --icon-size 100 \
        --icon "$APP_NAME.app" 150 185 \
        --app-drop-link 450 185 \
        --hide-extension "$APP_NAME.app" \
        "$DMG_OUTPUT" \
        "$DMG_DIR" || {
            # Fallback to hdiutil if create-dmg fails
            hdiutil create -volname "$APP_NAME" -srcfolder "$DMG_DIR" -ov -format UDZO "$DMG_OUTPUT"
        }
else
    # Use built-in hdiutil
    hdiutil create -volname "$APP_NAME" -srcfolder "$DMG_DIR" -ov -format UDZO "$DMG_OUTPUT"
fi

# Cleanup
rm -rf "$DMG_DIR"

echo "  ✓ DMG installer created"

# Step 6: Show results
echo ""
echo "[6/6] Build complete!"
echo ""
echo "========================================"
echo "  BUILD SUCCESSFUL!"
echo "========================================"
echo ""
echo "Application:  dist/${APP_NAME}.app"
echo "Installer:    installer_output/${DMG_NAME}.dmg"
echo ""

# Get file sizes
if [ -d "$APP_PATH" ]; then
    APP_SIZE=$(du -sh "$APP_PATH" | cut -f1)
    echo "App size:     $APP_SIZE"
fi

if [ -f "$DMG_OUTPUT" ]; then
    DMG_SIZE=$(du -sh "$DMG_OUTPUT" | cut -f1)
    echo "DMG size:     $DMG_SIZE"
fi

echo ""
echo "NOTES:"
echo "  - The AI model will download on first run (~1GB)"
echo "  - Users may need to right-click > Open the first time"
echo "  - For distribution, consider signing and notarizing the app"
echo ""
echo "To test the app:"
echo "  open dist/${APP_NAME}.app"
echo ""
