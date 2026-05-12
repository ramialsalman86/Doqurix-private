# -*- mode: python ; coding: utf-8 -*-
# ============================================================================
# Doqurix macOS Build Specification (FULL PARITY WITH WINDOWS BUILD)
#
# Run from the PROJECT ROOT on macOS:
#     pyinstaller --noconfirm macos/Doqurix_macOS.spec
#
# Or use the helper script:
#     bash macos/build_macos.sh
# ============================================================================

import os
import sys
import platform
from pathlib import Path
from PyInstaller.utils.hooks import collect_all, collect_submodules, collect_data_files

# ----------------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------------
# PyInstaller resolves relative paths in a .spec file relative to the spec's
# own directory (NOT the cwd). Since this spec lives in macos/, we anchor
# everything to the project root (one level up).
SPEC_DIR = Path(os.path.dirname(os.path.abspath(SPEC)))  # type: ignore[name-defined]  # SPEC is injected by PyInstaller
PROJECT_ROOT = SPEC_DIR.parent

def p(rel: str) -> str:
    """Resolve a path relative to the project root, as an absolute string."""
    return str((PROJECT_ROOT / rel).resolve())

# Detect the active Python's site-packages for venv-relative file lookups.
# On macOS, the path is venv/lib/pythonX.Y/site-packages
PY_VER = f"python{sys.version_info.major}.{sys.version_info.minor}"
venv_path = PROJECT_ROOT / 'venv' / 'lib' / PY_VER / 'site-packages'

# ----------------------------------------------------------------------------
# Data files (knowledge bases, modules, license, web app)
# Models are NOT bundled - they are downloaded on first run (~1GB).
# Source paths must be absolute so PyInstaller doesn't look inside macos/.
# ----------------------------------------------------------------------------
datas = [
    (p('data'),                  'data'),
    (p('tax_knowledge'),         'tax_knowledge'),
    (p('buerokratai_knowledge'), 'buerokratai_knowledge'),
    (p('ecommerce_agent.py'),    '.'),
    (p('buerokratai_agent.py'),  '.'),
    (p('bottle_app.py'),         '.'),
    (p('LICENSE.txt'),           '.'),
    (p('README.txt'),            '.'),
]

binaries = []

# ----------------------------------------------------------------------------
# Collect submodules + data files for heavy ML packages
# ----------------------------------------------------------------------------
chromadb_imports = collect_submodules('chromadb')
sentence_transformers_imports = collect_submodules('sentence_transformers')
llama_cpp_imports = collect_submodules('llama_cpp')
transformers_imports = collect_submodules('transformers')

chromadb_datas, chromadb_binaries, _ = collect_all('chromadb')
datas += chromadb_datas
binaries += chromadb_binaries

# fake_useragent ships a JSON browser DB
try:
    datas += collect_data_files('fake_useragent')
except Exception as e:
    print(f"Warning: Could not collect fake_useragent data: {e}")

# ----------------------------------------------------------------------------
# Bundle llama_cpp native libraries (.dylib / .so on macOS)
# ----------------------------------------------------------------------------
llama_cpp_path = venv_path / 'llama_cpp'
if llama_cpp_path.exists():
    lib_path = llama_cpp_path / 'lib'
    if lib_path.exists():
        for pattern in ('*.dylib', '*.so', '*.metal'):
            for lib in lib_path.glob(pattern):
                binaries.append((str(lib), 'llama_cpp/lib'))

# ----------------------------------------------------------------------------
# Hidden imports (mirror of Windows spec, macOS-safe)
# ----------------------------------------------------------------------------
hiddenimports = [
    # Web framework
    'bottle',

    # Hybrid search
    'rank_bm25',

    # Document handling
    'PyPDF2',
    'pypdf',
    'docx',
    'openpyxl',
    'pandas',

    # Agents
    'ecommerce_agent',
    'buerokratai_agent',
    'bs4',
    'beautifulsoup4',
    'requests',
    'lxml',
    'lxml.html',
    'lxml.etree',
    'html5lib',
    'fake_useragent',
    'diskcache',
    'aiohttp',

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
    'transformers.models.bert',
    'transformers.pipelines',
    'transformers.tokenization_utils',
    'transformers.tokenization_utils_base',
    'transformers.tokenization_utils_fast',

    # ChromaDB
    'chromadb',
    'chromadb.api',
    'chromadb.api.client',
    'chromadb.api.segment',
    'chromadb.api.types',
    'chromadb.config',
    'chromadb.db',
    'chromadb.db.base',
    'chromadb.db.impl',
    'chromadb.db.impl.sqlite',
    'chromadb.db.impl.sqlite_pool',
    'chromadb.db.migrations',
    'chromadb.db.system',
    'chromadb.errors',
    'chromadb.execution',
    'chromadb.execution.expression',
    'chromadb.execution.expression.operator',
    'chromadb.execution.expression.plan',
    'chromadb.ingest',
    'chromadb.migrations',
    'chromadb.quota',
    'chromadb.rate_limit',
    'chromadb.segment',
    'chromadb.segment.distributed',
    'chromadb.segment.impl',
    'chromadb.segment.impl.manager',
    'chromadb.segment.impl.manager.local',
    'chromadb.serde',
    'chromadb.telemetry',
    'chromadb.telemetry.opentelemetry',
    'chromadb.telemetry.product',
    'chromadb.telemetry.product.events',
    'chromadb.telemetry.product.posthog',
    'chromadb.types',
    'chromadb.utils',
    'chromadb.utils.batch_utils',
    'chromadb.utils.embedding_functions',
    'chromadb.utils.embedding_functions.onnx_mini_lm_l6_v2',
    'chromadb.utils.embedding_functions.sentence_transformer_embedding_function',

    # Torch
    'torch',
    'torch.nn',
    'torch.nn.functional',
    'torch.utils',
    'torch.utils.data',

    # HuggingFace Hub
    'huggingface_hub',
    'huggingface_hub.file_download',
    'huggingface_hub.hf_api',
    'huggingface_hub.utils',

    # Numerics
    'numpy',
    'scipy',
    'scipy.spatial',
    'scipy.spatial.distance',
    'sklearn',
    'sklearn.metrics',
    'sklearn.metrics.pairwise',

    # Tokenizers
    'tiktoken',
    'tiktoken_ext',
    'tiktoken_ext.openai_public',
    'tokenizers',
    'safetensors',

    # Misc deps
    'pkg_resources',
    'tqdm',
    'filelock',
    'regex',
    'urllib3',
    'certifi',
    'charset_normalizer',
    'idna',
    'packaging',
    'yaml',
    'posthog',
    'monotonic',
    'backoff',
    'mmh3',
    'onnxruntime',
    'sqlite3',
    'pydantic',
    'pydantic.deprecated',
    'pydantic.deprecated.decorator',
    'opentelemetry',
    'opentelemetry.sdk',
    'opentelemetry.sdk.trace',

    # Pillow
    'PIL',
    'PIL.Image',
    'PIL._imaging',

    # Tkinter (system Python.framework Tk on macOS)
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'tkinter.scrolledtext',

    # Stdlib used dynamically
    'urllib.parse',
    'hashlib',
    'json',
]

# Combine static + dynamically collected hidden imports, dedup
all_hiddenimports = list(set(
    hiddenimports
    + chromadb_imports
    + sentence_transformers_imports
    + llama_cpp_imports
    + transformers_imports
))

# ----------------------------------------------------------------------------
# Excludes (slim the bundle)
# ----------------------------------------------------------------------------
excludes = [
    'matplotlib',
    'cv2',
    'opencv',
    'IPython',
    'jupyter',
    'notebook',
    'pytest',
    'sphinx',
    'tensorflow',
    'keras',
    'jax',
    'flax',
]

# ----------------------------------------------------------------------------
# Icon (use .icns if present, otherwise PyInstaller default)
# ----------------------------------------------------------------------------
_icns = PROJECT_ROOT / 'app_icon.icns'
icon_file = str(_icns) if _icns.exists() else None

# ----------------------------------------------------------------------------
# Analysis / PYZ / EXE / COLLECT / BUNDLE
# ----------------------------------------------------------------------------
a = Analysis(
    [p('main.py')],
    pathex=[str(PROJECT_ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=all_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
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
    upx=False,           # UPX is unreliable on macOS Mach-O binaries
    console=False,       # Windowed (.app) GUI
    disable_windowed_traceback=False,
    argv_emulation=True, # Needed on macOS for file-open events
    target_arch=None,    # Builds for the host arch (arm64 or x86_64)
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='Doqurix',
)

app = BUNDLE(
    coll,
    name='Doqurix.app',
    icon=icon_file,
    bundle_identifier='com.aisolutions.doqurix',
    info_plist={
        'CFBundleName': 'Doqurix',
        'CFBundleDisplayName': 'Doqurix',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleExecutable': 'Doqurix',
        'CFBundleIdentifier': 'com.aisolutions.doqurix',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': 'DQRX',
        'LSMinimumSystemVersion': '10.15',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'LSApplicationCategoryType': 'public.app-category.productivity',
        'NSHumanReadableCopyright': 'Copyright © 2025 AI Solutions',
        # Privacy strings (only required if app actually triggers these prompts)
        'NSAppleEventsUsageDescription': 'Doqurix may interact with other apps for document import.',
    },
)
