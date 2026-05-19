"""Template: Headless model/data loader.

Replace the per-stage methods with the real ones from your project. The
critical contract is:

  * No Tkinter / no GUI calls.
  * Every progress update goes through ``self._set(...)`` which writes into
    a dict shared with the web layer (``STARTUP_STATE`` in web_endpoints.py).
  * Public attributes (``llm``, ``embedder``, ``reranker``, …) match what
    the web module's ``init_models()`` expects, so the web routes do not
    need any changes.
"""

from __future__ import annotations

import os
import sys
import urllib.request
from pathlib import Path


class HeadlessLoader:
    def __init__(self, progress_state: dict):
        self.progress = progress_state

        # Example user-writable directories. Adjust per-project.
        appdata = Path(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")))
        self.user_data_dir = appdata / "YourAppName"
        self.user_data_dir.mkdir(exist_ok=True)
        self.models_dir = self.user_data_dir / "models"
        self.models_dir.mkdir(exist_ok=True)

        # Attributes consumed by the web module's init_models()
        self.llm = None
        self.embedder = None
        self.reranker = None
        self.chroma_client = None
        self.collection = None

    # ---- progress helpers -------------------------------------------------
    def _set(self, **kwargs):
        self.progress.update(kwargs)

    def _stage(self, idx: int, total: int, label: str):
        self._set(
            stage_index=idx,
            stage_total=total,
            stage_label=label,
            percent=(idx / total) * 100 if total else 0,
            status=label,
        )

    # ---- download with progress ------------------------------------------
    def _download(self, url: str, dest_path: Path, description: str):
        self._set(title="Downloading", status=description,
                  download_bytes=0, download_total=0)
        with urllib.request.urlopen(url, timeout=30) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            self._set(download_total=total)
            downloaded = 0
            with open(dest_path, "wb") as f:
                while True:
                    chunk = resp.read(1024 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    self._set(
                        download_bytes=downloaded,
                        percent=(downloaded / total) * 100 if total else 0,
                    )

    # ---- one method per startup stage (copy from your GUI class) ---------
    def init_llm(self):
        self._set(status="Loading language model...")
        # ... your real code ...

    def init_embeddings(self):
        self._set(status="Loading embeddings...")
        # ... your real code ...

    def init_reranker(self):
        self._set(status="Loading reranker...")
        # ... your real code ...

    def init_vector_db(self):
        self._set(status="Opening vector database...")
        # ... your real code ...

    # ---- orchestration ----------------------------------------------------
    def load_all(self):
        try:
            stages = [
                ("Loading language model...", self.init_llm),
                ("Loading embeddings...", self.init_embeddings),
                ("Loading reranker...", self.init_reranker),
                ("Opening vector database...", self.init_vector_db),
            ]
            total = len(stages)
            self._set(ready=False, error=None,
                      stage_total=total, title="Starting...", percent=0)
            for i, (label, fn) in enumerate(stages):
                self._stage(i, total, label)
                fn()
                self._stage(i + 1, total, label + " ✓")
            self._set(ready=True, status="Ready", percent=100,
                      title="Application is ready")
        except Exception as e:
            import traceback
            traceback.print_exc()
            self._set(ready=False, error=str(e),
                      status=f"Failed: {e}", title="Startup Failed")
