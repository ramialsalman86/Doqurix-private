# Doqurix - macOS Build

This folder contains everything needed to build a fully working macOS version
of Doqurix: a standalone `.app` bundle and a `.dmg` installer.

The macOS build has **full feature parity** with the Windows build:
- Document Q&A (PDF / DOCX / TXT)
- Tax knowledge agent (`tax_knowledge/`)
- BürokratAI immigration agent (`buerokratai_knowledge/`)
- E-commerce price agent (`ecommerce_agent.py`)
- Bottle web UI (`bottle_app.py`)
- Local LLM via `llama-cpp-python`
- ChromaDB vector store + sentence-transformers + BM25 hybrid search

## Files

| File | Purpose |
|------|---------|
| `Doqurix_macOS.spec` | PyInstaller spec for the `.app` bundle |
| `build_macos.sh`     | One-shot build script (venv → PyInstaller → DMG) |
| `README.md`          | This file |

## Requirements

- macOS 10.15 (Catalina) or newer — Intel **or** Apple Silicon
- Python 3.10 or 3.11
  ```bash
  brew install python@3.11
  ```
- Xcode Command Line Tools
  ```bash
  xcode-select --install
  ```
- *(Optional, prettier DMG)* `brew install create-dmg`

## Build

From the **project root** (the folder containing `main.py`):

```bash
chmod +x macos/build_macos.sh
bash macos/build_macos.sh
```

The script will:

1. Create / reuse `venv/`
2. Install `requirements.txt` + PyInstaller
3. Convert `app_icon.ico` → `app_icon.icns` (via `sips` + `iconutil`)
4. Build `dist/Doqurix.app` from `macos/Doqurix_macOS.spec`
5. Package `installer_output/Doqurix_Setup_v1.0.0.dmg`
6. Ad-hoc codesign the bundle (so Gatekeeper allows first launch)

## Run / Test

```bash
open dist/Doqurix.app
```

On first launch, the LLM model (~1 GB) is downloaded automatically into the
user's data directory. No model is bundled in the installer to keep its size
reasonable.

## Distribute

Drag `installer_output/Doqurix_Setup_v1.0.0.dmg` to end users. They:

1. Open the DMG
2. Drag **Doqurix** to **Applications**
3. First launch: right-click → **Open** (one-time Gatekeeper bypass for
   unsigned apps)

For real public distribution, sign with a paid Apple Developer ID and
notarize:

```bash
codesign --force --deep --options runtime \
  --sign "Developer ID Application: Your Name (TEAMID)" \
  dist/Doqurix.app

xcrun notarytool submit installer_output/Doqurix_Setup_v1.0.0.dmg \
  --apple-id you@example.com --team-id TEAMID --password app-specific-pwd \
  --wait

xcrun stapler staple installer_output/Doqurix_Setup_v1.0.0.dmg
```

## Architecture notes

- The spec auto-detects the host architecture. Build on an **Apple Silicon
  Mac** to get an arm64 `.app`; build on an **Intel Mac** for x86_64.
- To produce a universal2 binary you need universal Python + universal wheels
  for `torch`, `llama-cpp-python`, `onnxruntime`, etc. That is generally not
  worth the trouble — ship two DMGs instead, or a single arm64 DMG (Intel
  Macs can run it under Rosetta 2 if dependencies are x86_64).

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `llama_cpp` fails to load | Ensure `pip install llama-cpp-python` succeeded; on Apple Silicon you may want `CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python --no-binary llama-cpp-python` |
| App quarantined / "damaged" | `xattr -cr dist/Doqurix.app` then re-run |
| Tk icon ugly / app crashes on launch | Use Python from python.org or Homebrew (system Python lacks proper Tk) |
| `ModuleNotFoundError: chromadb.xxx` at runtime | Re-run the build; spec collects all chromadb submodules dynamically |
