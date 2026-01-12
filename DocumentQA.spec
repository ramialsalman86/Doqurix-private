# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_all, collect_submodules, collect_data_files

# Get the venv site-packages path
venv_path = Path('venv/Lib/site-packages')

# Collect all necessary data files
# NOTE: Models are NOT bundled - they will be downloaded on first run to reduce installer size
datas = [
    # Include data directory structure (but NOT models - too large ~1GB)
    ('data', 'data'),
    # Include tax knowledge base (essential for tax agent)
    ('tax_knowledge', 'tax_knowledge'),
    # Include BürokratAI knowledge base (essential for immigration agent)
    ('buerokratai_knowledge', 'buerokratai_knowledge'),
    # Include e-commerce agent module
    ('ecommerce_agent.py', '.'),
    # Include BürokratAI agent module
    ('buerokratai_agent.py', '.'),
    # Include license and readme
    ('LICENSE.txt', '.'),
    ('README.txt', '.'),
    # Include lightweight Bottle web app
    ('bottle_app.py', '.'),
]

# Binary files that need to be included
binaries = []

# Collect ALL submodules for critical packages to prevent missing module errors
chromadb_imports = collect_submodules('chromadb')
sentence_transformers_imports = collect_submodules('sentence_transformers')
llama_cpp_imports = collect_submodules('llama_cpp')
transformers_imports = collect_submodules('transformers')

# Collect data files for packages that need them
chromadb_datas, chromadb_binaries, _ = collect_all('chromadb')
datas += chromadb_datas
binaries += chromadb_binaries

# Collect fake_useragent data files (browsers.jsonl)
try:
    fake_ua_datas = collect_data_files('fake_useragent')
    datas += fake_ua_datas
    print(f"Collected fake_useragent data files: {fake_ua_datas}")
except Exception as e:
    print(f"Warning: Could not collect fake_useragent data: {e}")

# Check for llama_cpp DLLs
llama_cpp_path = venv_path / 'llama_cpp'
if llama_cpp_path.exists():
    lib_path = llama_cpp_path / 'lib'
    if lib_path.exists():
        for dll in lib_path.glob('*.dll'):
            binaries.append((str(dll), 'llama_cpp/lib'))

# Hidden imports that PyInstaller might miss
hiddenimports = [
    # Bottle web framework
    'bottle',
    
    # BM25 for hybrid search
    'rank_bm25',
    
    # PDF handling
    'PyPDF2',
    
    # E-commerce agent dependencies
    'ecommerce_agent',
    'bs4',
    'beautifulsoup4',
    'requests',
    'lxml',
    'html5lib',
    'fake_useragent',
    'diskcache',
    
    # BürokratAI agent
    'buerokratai_agent',
    
    # Llama CPP - ALL submodules
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
    
    # Sentence Transformers - ALL submodules
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
    
    # ChromaDB - ALL submodules
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
    
    # Others
    'PyPDF2',
    'rank_bm25',
    'numpy',
    'scipy',
    'scipy.spatial',
    'scipy.spatial.distance',
    'sklearn',
    'sklearn.metrics',
    'sklearn.metrics.pairwise',
    'tiktoken',
    'tiktoken_ext',
    'tiktoken_ext.openai_public',
    'tokenizers',
    
    # Additional hidden imports for compatibility
    'pkg_resources',
    'tqdm',
    'filelock',
    'regex',
    'requests',
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
    'grpc',
    'google',
    'google.protobuf',
    
    # PIL/Pillow - required by sentence_transformers
    'PIL',
    'PIL.Image',
    'PIL._imaging',
    
    # Web scraping & E-commerce
    'aiohttp',
    'lxml',
    'lxml.html',
    'lxml.etree',
    'html5lib',
    'selenium',
    'selenium.webdriver',
    'urllib.parse',
    'hashlib',
    'json',
]

# Combine all hidden imports (static + dynamic)
all_hiddenimports = hiddenimports + chromadb_imports + sentence_transformers_imports + llama_cpp_imports + transformers_imports

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=all_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'cv2',
        'IPython',
        'jupyter',
        'notebook',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

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
    console=False,  # No console window - windowed mode for GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico',  # Application icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Doqurix',
)
