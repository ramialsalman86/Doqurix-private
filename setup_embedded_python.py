"""
Setup Embedded Python with Streamlit for Doqurix Web Version

This script downloads Python embeddable package and installs Streamlit
for use with the installed application.
"""

import os
import sys
import urllib.request
import zipfile
import subprocess
from pathlib import Path

# Configuration
PYTHON_VERSION = "3.12.3"
PYTHON_EMBED_URL = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-embed-amd64.zip"
EMBED_DIR = Path(__file__).parent / "python_embed"
GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"


def download_file(url, dest):
    """Download a file with progress"""
    print(f"Downloading {url}...")
    urllib.request.urlretrieve(url, dest)
    print(f"  -> Saved to {dest}")


def setup_embedded_python():
    """Download and setup embedded Python"""
    
    # Create embed directory
    EMBED_DIR.mkdir(exist_ok=True)
    
    # Download Python embeddable
    zip_path = EMBED_DIR / "python_embed.zip"
    if not zip_path.exists():
        download_file(PYTHON_EMBED_URL, zip_path)
    
    # Extract
    print("Extracting Python embeddable package...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(EMBED_DIR)
    
    # Remove the zip to save space
    zip_path.unlink()
    
    # Configure ._pth file to enable pip
    # Find the ._pth file (e.g., python312._pth)
    pth_files = list(EMBED_DIR.glob("python*._pth"))
    if pth_files:
        pth_file = pth_files[0]
        print(f"Configuring {pth_file.name} to enable pip...")
        
        # Read and modify - uncomment 'import site'
        content = pth_file.read_text()
        content = content.replace("#import site", "import site")
        pth_file.write_text(content)
    
    # Download get-pip.py
    get_pip_path = EMBED_DIR / "get-pip.py"
    if not get_pip_path.exists():
        download_file(GET_PIP_URL, get_pip_path)
    
    # Install pip
    python_exe = EMBED_DIR / "python.exe"
    print("Installing pip...")
    subprocess.run([str(python_exe), str(get_pip_path)], check=True, cwd=str(EMBED_DIR))
    
    # Install Streamlit and minimal dependencies
    print("Installing Streamlit (this may take a few minutes)...")
    subprocess.run([
        str(python_exe), "-m", "pip", "install", 
        "--no-warn-script-location",
        "streamlit",
        "watchdog",  # For better file watching
    ], check=True, cwd=str(EMBED_DIR))
    
    # Clean up pip cache to reduce size
    pip_cache = EMBED_DIR / "pip"
    if pip_cache.exists():
        import shutil
        shutil.rmtree(pip_cache, ignore_errors=True)
    
    # Remove get-pip.py
    get_pip_path.unlink(missing_ok=True)
    
    print("\n✓ Embedded Python with Streamlit is ready!")
    print(f"  Location: {EMBED_DIR}")
    
    # Calculate size
    total_size = sum(f.stat().st_size for f in EMBED_DIR.rglob("*") if f.is_file())
    print(f"  Total size: {total_size / (1024*1024):.1f} MB")


if __name__ == "__main__":
    setup_embedded_python()
