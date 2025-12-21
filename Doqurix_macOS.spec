# -*- mode: python ; coding: utf-8 -*-
# Doqurix macOS Build Specification
# Run on macOS: pyinstaller --noconfirm Doqurix_macOS.spec

import os
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_all, collect_submodules, collect_data_files

# Get the venv site-packages path
venv_path = Path('venv/lib/python3.11/site-packages')  # Adjust Python version as needed

# Collect all necessary data files
# NOTE: Models are NOT bundled - they will be downloaded on first run
datas = [
    ('data', 'data'),
    ('LICENSE.txt', '.'),
    ('README.txt', '.'),
]

# Binary files
binaries = []

# Collect ALL submodules for critical packages
chromadb_imports = collect_submodules('chromadb')
sentence_transformers_imports = collect_submodules('sentence_transformers')
llama_cpp_imports = collect_submodules('llama_cpp')
transformers_imports = collect_submodules('transformers')

# Collect data files for packages that need them
chromadb_datas, chromadb_binaries, _ = collect_all('chromadb')
datas += chromadb_datas
binaries += chromadb_binaries

# Hidden imports
hiddenimports = [
    # Llama CPP
    'llama_cpp',
    'llama_cpp._internals',
    'llama_cpp._logger',
    'llama_cpp._utils',
    'llama_cpp.llama',
    'llama_cpp.llama_cache',
    'llama_cpp.llama_chat_format',
    'llama_cpp.llama_cpp',
    'llama_cpp.llama_grammar',
    'llama_cpp.llama_speculative',
    'llama_cpp.llama_tokenizer',
    'llama_cpp.llama_types',
    'llama_cpp.llava_cpp',
    
    # Sentence Transformers
    'sentence_transformers',
    'sentence_transformers.SentenceTransformer',
    'sentence_transformers.cross_encoder',
    'sentence_transformers.cross_encoder.CrossEncoder',
    'sentence_transformers.evaluation',
    'sentence_transformers.losses',
    'sentence_transformers.models',
    'sentence_transformers.models.CLIPModel',
    'sentence_transformers.models.Dense',
    'sentence_transformers.models.Normalize',
    'sentence_transformers.models.Pooling',
    'sentence_transformers.models.Transformer',
    'sentence_transformers.util',
    'sentence_transformers.quantization',
    'sentence_transformers.similarity_functions',
    
    # Transformers
    'transformers',
    'transformers.models',
    'transformers.models.auto',
    'transformers.pipelines',
    'transformers.tokenization_utils',
    'transformers.tokenization_utils_base',
    'transformers.tokenization_utils_fast',
    
    # ChromaDB
    'chromadb',
    'chromadb.api',
    'chromadb.api.segment',
    'chromadb.config',
    'chromadb.db',
    'chromadb.db.base',
    'chromadb.db.impl',
    'chromadb.db.impl.sqlite',
    'chromadb.migrations',
    'chromadb.segment',
    'chromadb.segment.distributed',
    'chromadb.segment.impl',
    'chromadb.segment.impl.manager',
    'chromadb.segment.impl.manager.local',
    'chromadb.telemetry',
    'chromadb.telemetry.product.posthog',
    'chromadb.utils',
    'chromadb.utils.batch_utils',
    
    # Other dependencies
    'tiktoken_ext.openai_public',
    'tiktoken_ext',
    'pydantic.deprecated.decorator',
    'huggingface_hub',
    'huggingface_hub.hf_api',
    'huggingface_hub.file_download',
    'safetensors',
    'tqdm',
    'numpy',
    'torch',
    'PIL',
    'PIL.Image',
    'pypdf',
    'PyPDF2',
    'docx',
    'openpyxl',
    'pandas',
    'sklearn',
    'sklearn.metrics',
    'sklearn.metrics.pairwise',
    
    # Tkinter
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'tkinter.scrolledtext',
]

# Add collected submodules
hiddenimports += chromadb_imports
hiddenimports += sentence_transformers_imports
hiddenimports += llama_cpp_imports
hiddenimports += transformers_imports

# Remove duplicates
hiddenimports = list(set(hiddenimports))

# Exclude unnecessary packages to reduce size
excludes = [
    'matplotlib',
    'notebook',
    'jupyter',
    'ipython',
    'pytest',
    'sphinx',
    'cv2',
    'opencv',
    'tensorflow',
    'keras',
    'jax',
    'flax',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Doqurix',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=True,  # macOS specific
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Doqurix',
)

# macOS .app bundle
app = BUNDLE(
    coll,
    name='Doqurix.app',
    icon='app_icon.icns',  # Need to create .icns from .ico
    bundle_identifier='com.aisolutions.doqurix',
    info_plist={
        'CFBundleName': 'Doqurix',
        'CFBundleDisplayName': 'Doqurix',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleExecutable': 'Doqurix',
        'CFBundleIconFile': 'app_icon.icns',
        'CFBundleIdentifier': 'com.aisolutions.doqurix',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': 'DQRX',
        'LSMinimumSystemVersion': '10.15',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'LSApplicationCategoryType': 'public.app-category.productivity',
        'NSHumanReadableCopyright': 'Copyright © 2025 AI Solutions',
    },
)
