# ============================================================================
# Document QA Application - Automated Build Script
# ============================================================================
# This script automates the entire build and installer creation process
# ============================================================================

param(
    [switch]$SkipVenv = $false,
    [switch]$SkipBuild = $false,
    [switch]$SkipInstaller = $false,
    [switch]$CleanBuild = $false
)

$ErrorActionPreference = "Stop"

# Colors for output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Step($message) {
    Write-ColorOutput Green "`n========================================`n$message`n========================================"
}

function Write-Info($message) {
    Write-ColorOutput Cyan "ℹ️  $message"
}

function Write-Success($message) {
    Write-ColorOutput Green "✓ $message"
}

function Write-Error-Custom($message) {
    Write-ColorOutput Red "❌ $message"
}

# ============================================================================
# Step 1: Check Prerequisites
# ============================================================================
Write-Step "Step 1: Checking Prerequisites"

# Check Python
Write-Info "Checking Python installation..."
try {
    $pythonVersion = python --version 2>&1
    Write-Success "Found: $pythonVersion"
    
    # Check if Python version is 3.9 or higher
    $versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)"
    if ($versionMatch) {
        $major = [int]$Matches[1]
        $minor = [int]$Matches[2]
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 9)) {
            Write-Error-Custom "Python 3.9 or higher is required. Found: $pythonVersion"
            exit 1
        }
    }
}
catch {
    Write-Error-Custom "Python is not installed or not in PATH!"
    Write-Info "Please install Python 3.9+ from https://www.python.org/downloads/"
    exit 1
}

# Check Inno Setup
Write-Info "Checking Inno Setup installation..."
$innoSetupPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $innoSetupPath)) {
    Write-Error-Custom "Inno Setup 6 not found at: $innoSetupPath"
    Write-Info "Please install Inno Setup 6 from https://jrsoftware.org/isdl.php"
    exit 1
}
Write-Success "Found Inno Setup 6"

# Check required files and directories
Write-Info "Checking required files and directories..."
$requiredItems = @{
    "main.py" = "Main application file";
    "bottle_app.py" = "Web interface file";
    "DocumentQA.spec" = "PyInstaller spec file";
    "installer_script.iss" = "Inno Setup script";
    "LICENSE.txt" = "License file";
    "README.txt" = "Readme file";
    "tax_knowledge" = "Tax knowledge base directory"
}

$allRequiredPresent = $true
foreach ($item in $requiredItems.Keys) {
    if (Test-Path $item) {
        if ($item -eq "tax_knowledge") {
            $taxFiles = Get-ChildItem -Path "tax_knowledge\*.txt" -ErrorAction SilentlyContinue
            if ($taxFiles.Count -ge 5) {
                Write-Success "Found $($requiredItems[$item]) - $($taxFiles.Count) files"
            }
            else {
                Write-Error-Custom "Missing tax files - Only $($taxFiles.Count) found (need 5)"
                $allRequiredPresent = $false
            }
        }
        else {
            Write-Success "Found $($requiredItems[$item])"
        }
    }
    else {
        Write-Error-Custom "Missing: $item"
        $allRequiredPresent = $false
    }
}

if (-not $allRequiredPresent) {
    Write-Error-Custom "Some required files are missing!"
    exit 1
}

# ============================================================================
# Step 2: Clean Previous Build (Optional)
# ============================================================================
if ($CleanBuild) {
    Write-Step "Step 2: Cleaning Previous Build"
    
    $foldersToClean = @("build", "dist", "installer_output")
    foreach ($folder in $foldersToClean) {
        if (Test-Path $folder) {
            Write-Info "Removing $folder..."
            Remove-Item -Path $folder -Recurse -Force
            Write-Success "Removed $folder"
        }
    }
}

# ============================================================================
# Step 3: Setup Virtual Environment
# ============================================================================
if (-not $SkipVenv) {
    Write-Step "Step 3: Setting Up Virtual Environment"
    
    if (-not (Test-Path "venv")) {
        Write-Info "Creating virtual environment..."
        python -m venv venv
        Write-Success "Virtual environment created"
    }
    else {
        Write-Info "Virtual environment already exists"
    }
    
    Write-Info "Activating virtual environment..."
    & ".\venv\Scripts\Activate.ps1"
    Write-Success "Virtual environment activated"
    
    Write-Info "Upgrading pip..."
    python -m pip install --upgrade pip
    
    Write-Info "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
    Write-Success "Dependencies installed"
}
else {
    Write-Info "Skipping virtual environment setup (using existing environment)"
}

# ============================================================================
# Step 4: Build Executable with PyInstaller
# ============================================================================
if (-not $SkipBuild) {
    Write-Step "Step 4: Building Executable with PyInstaller"
    
    Write-Info "Running PyInstaller..."
    pyinstaller DocumentQA.spec --clean --noconfirm
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "PyInstaller build failed!"
        exit 1
    }
    
    # Verify the executable was created
    $exePath = "dist\DocumentQA\DocumentQA.exe"
    if (Test-Path $exePath) {
        $exeSize = (Get-Item $exePath).Length / 1MB
        Write-Success "Executable created successfully: $exePath ($([math]::Round($exeSize, 2)) MB)"
        
        # Fix: Manually copy llama_cpp/lib folder which PyInstaller often misses
        Write-Info "Applying fix for llama_cpp DLLs..."
        $llamaSource = "venv\Lib\site-packages\llama_cpp"
        $llamaDest = "dist\DocumentQA\_internal\llama_cpp"
        
        if (Test-Path $llamaSource) {
            # Create destination if needed
            if (-not (Test-Path $llamaDest)) { New-Item -ItemType Directory -Path $llamaDest -Force | Out-Null }
            
            # Copy all files recursively
            Copy-Item -Path "$llamaSource\*" -Destination $llamaDest -Recurse -Force
            Write-Success "Copied llama_cpp library files"
        }
        else {
            Write-Error-Custom "Could not find llama_cpp in venv!"
        }
    }
    else {
        Write-Error-Custom "Executable not found at: $exePath"
        exit 1
    }
}
else {
    Write-Info "Skipping PyInstaller build (using existing build)"
}

# ============================================================================
# Step 5: Create Installer with Inno Setup
# ============================================================================
if (-not $SkipInstaller) {
    Write-Step "Step 5: Creating Installer with Inno Setup"
    
    Write-Info "Compiling installer script..."
    & $innoSetupPath "installer_script.iss"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Inno Setup compilation failed!"
        exit 1
    }
    
    # Find the created installer
    $installerPattern = "installer_output\DocumentQA_Setup_*.exe"
    $installer = Get-ChildItem -Path $installerPattern -ErrorAction SilentlyContinue | Select-Object -First 1
    
    if ($installer) {
        $installerSize = $installer.Length / 1MB
        Write-Success "Installer created successfully!"
        Write-Info "Location: $($installer.FullName)"
        Write-Info "Size: $([math]::Round($installerSize, 2)) MB"
    }
    else {
        Write-Error-Custom "Installer not found in installer_output folder"
        exit 1
    }
}
else {
    Write-Info "Skipping installer creation"
}

# ============================================================================
# Summary
# ============================================================================
Write-Step "Build Complete! 🎉"

Write-Success "All steps completed successfully!"
Write-Info ""
Write-Info "Next steps:"
Write-Info "1. Test the installer: installer_output\DocumentQA_Setup_v1.0.0.exe"
Write-Info "2. Install on a clean Windows machine to verify"
Write-Info "3. Distribute the installer to users"
Write-Info ""
Write-Info "Build artifacts:"
Write-Info "  - Executable: dist\DocumentQA\DocumentQA.exe"
Write-Info "  - Installer: installer_output\DocumentQA_Setup_v1.0.0.exe"
