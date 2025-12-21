# Document QA Application - Build & Installation Guide

## 📋 Overview

This guide explains how to build a Windows installer (.exe) for the Document QA application. The installer includes all Python dependencies and creates a professional wizard-based installation experience.

## 🔧 Prerequisites

Before building the installer, ensure you have:

1. **Python 3.9 or higher (64-bit)**
   - Download from: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"

2. **Inno Setup 6**
   - Download from: https://jrsoftware.org/isdl.php
   - Install to default location: `C:\Program Files (x86)\Inno Setup 6\`

3. **Windows 10 or later (64-bit)**
   - Required for building and running the application

4. **Minimum 10GB free disk space**
   - For build artifacts, dependencies, and AI models

## 🚀 Quick Start - Automated Build

The easiest way to build the installer is using the automated build script:

### Option 1: Full Automated Build (Recommended)

```powershell
# Navigate to project directory
cd "c:\Users\R00171\OneDrive - Uniper SE\Desktop\QA_AI_DOCUMENT"

# Run the automated build script
.\build_installer.ps1
```

This will:
1. ✅ Check all prerequisites (Python, Inno Setup)
2. ✅ Create/activate virtual environment
3. ✅ Install all dependencies
4. ✅ Build executable with PyInstaller
5. ✅ Create installer with Inno Setup

### Option 2: Clean Build

```powershell
# Clean previous builds and rebuild everything
.\build_installer.ps1 -CleanBuild
```

### Option 3: Partial Build

```powershell
# Skip virtual environment setup (use existing)
.\build_installer.ps1 -SkipVenv

# Skip PyInstaller build (use existing dist folder)
.\build_installer.ps1 -SkipBuild

# Skip installer creation (only build executable)
.\build_installer.ps1 -SkipInstaller
```

## 📝 Manual Build Process

If you prefer to build manually, follow these steps:

### Step 1: Setup Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Build Executable with PyInstaller

```powershell
# Build the executable
pyinstaller DocumentQA.spec --clean --noconfirm
```

This creates:
- `build/` - Temporary build files
- `dist/DocumentQA/` - Standalone application folder
- `dist/DocumentQA/DocumentQA.exe` - Main executable

### Step 3: Create Installer with Inno Setup

```powershell
# Compile installer (using Inno Setup command line)
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer_script.iss
```

This creates:
- `installer_output/DocumentQA_Setup_v1.0.0.exe` - Final installer

## 📦 What Gets Included

### Application Files
- ✅ Main executable (`DocumentQA.exe`)
- ✅ All Python runtime dependencies
- ✅ AI/ML libraries (llama-cpp, sentence-transformers, etc.)
- ✅ GUI libraries (tkinter)
- ✅ Documentation (README.txt, LICENSE.txt)

### User Data Directories (Created on Installation)
- `%APPDATA%\Document QA Assistant\data\` - Vector database storage
- `%APPDATA%\Document QA Assistant\models\` - AI models cache

### Installation Options
- ✅ Desktop shortcut (optional, checked by default)
- ✅ Start Menu shortcuts
- ✅ Quick Launch icon (optional, Windows 7 only)

## 🎯 Installer Features

### System Requirements Check
- Verifies Windows 10 or later (64-bit)
- Checks for 64-bit architecture
- Displays clear error messages if requirements not met

### Installation Wizard
- Professional modern UI
- License agreement (MIT License)
- Pre-installation information
- Custom installation directory
- Component selection
- Progress tracking
- Post-installation launch option

### Uninstallation
- Clean uninstall option
- Asks user whether to keep or remove user data
- Removes all installed files and shortcuts

## 🔍 Verification

### Test the Executable (Before Creating Installer)

```powershell
# Run the built executable directly
.\dist\DocumentQA\DocumentQA.exe
```

Verify:
- ✅ Application launches without errors
- ✅ GUI displays correctly
- ✅ Can upload PDF documents
- ✅ Can ask questions
- ✅ AI models download on first run

### Test the Installer

1. **Install on a clean machine** (or VM)
2. **Run the installer**: `installer_output\DocumentQA_Setup_v1.0.0.exe`
3. **Follow the wizard** and complete installation
4. **Launch the application** from desktop or Start Menu
5. **Test core functionality**:
   - Upload a PDF document
   - Ask a question
   - Verify AI models download
   - Check answer quality

## 📊 Build Output

After successful build, you'll have:

```
QA_AI_DOCUMENT/
├── build/                          # Temporary build files (can be deleted)
├── dist/
│   └── DocumentQA/                 # Standalone application
│       ├── DocumentQA.exe          # Main executable (~50-100 MB)
│       ├── _internal/              # Dependencies
│       ├── data/                   # Empty data folder
│       ├── models/                 # Empty models folder
│       ├── README.txt
│       └── LICENSE.txt
├── installer_output/
│   └── DocumentQA_Setup_v1.0.0.exe # Final installer (~150-200 MB)
├── venv/                           # Virtual environment (can be deleted)
├── main.py                         # Source code
├── requirements.txt                # Dependencies
├── DocumentQA.spec                 # PyInstaller config
├── installer_script.iss            # Inno Setup config
└── build_installer.ps1             # Automated build script
```

## 🐛 Troubleshooting

### PyInstaller Errors

**Error: Module not found**
```powershell
# Solution: Add missing module to DocumentQA.spec hiddenimports
# Then rebuild
pyinstaller DocumentQA.spec --clean --noconfirm
```

**Error: UPX not available**
```powershell
# Solution: Disable UPX in DocumentQA.spec
# Change: upx=True → upx=False
```

### Inno Setup Errors

**Error: Cannot find source file**
```powershell
# Solution: Ensure PyInstaller build completed successfully
# Check that dist/DocumentQA/ folder exists
```

**Error: Inno Setup not found**
```powershell
# Solution: Install Inno Setup 6 from:
# https://jrsoftware.org/isdl.php
```

### Runtime Errors

**Application doesn't start**
- Check Windows Event Viewer for errors
- Try running from command line to see error messages:
  ```powershell
  .\dist\DocumentQA\DocumentQA.exe
  ```

**Missing DLL errors**
- Ensure you're building on Windows 10+ 64-bit
- Reinstall Visual C++ Redistributable

## 📈 Optimization Tips

### Reduce Installer Size

1. **Exclude unnecessary packages** in `DocumentQA.spec`:
   ```python
   excludes=['matplotlib', 'pandas', 'PIL', 'cv2']
   ```

2. **Use better compression** in `installer_script.iss`:
   ```pascal
   Compression=lzma2/ultra64
   ```

### Faster Build Times

1. **Skip clean build** when testing:
   ```powershell
   pyinstaller DocumentQA.spec --noconfirm
   ```

2. **Use existing virtual environment**:
   ```powershell
   .\build_installer.ps1 -SkipVenv
   ```

## 📝 Customization

### Change Application Version

Edit `installer_script.iss`:
```pascal
#define MyAppVersion "1.0.0"  → "1.1.0"
```

### Change Application Icon

Replace `app_icon.ico` with your custom icon (256x256 recommended)

### Modify Installation Directory

Edit `installer_script.iss`:
```pascal
DefaultDirName={autopf}\{#MyAppName}  → Your custom path
```

## 🎉 Distribution

Once built, distribute:
- **Installer**: `installer_output\DocumentQA_Setup_v1.0.0.exe`
- **Size**: ~150-200 MB (compressed)
- **Includes**: Everything needed to run (no Python installation required)

### User Installation Steps

1. Download `DocumentQA_Setup_v1.0.0.exe`
2. Run the installer (requires admin rights)
3. Follow the installation wizard
4. Launch from desktop or Start Menu
5. On first run, AI models will download (~1GB, one-time)

## 📞 Support

For issues or questions:
- Check troubleshooting section above
- Review build logs in console output
- Verify all prerequisites are installed correctly

---

**Built with ❤️ using PyInstaller and Inno Setup**
