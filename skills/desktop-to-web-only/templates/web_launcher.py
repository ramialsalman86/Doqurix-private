"""Template: web-only entry point.

Replaces the old Tk ``check_license_and_run()`` / ``mainloop()`` pattern.
Adapt the imports for your project.
"""

from __future__ import annotations

import os
import sys
import threading
import time
import webbrowser
from pathlib import Path


def _ensure_license_or_exit():
    """Headless license gate.

    First run silently starts the trial via ``LicenseManager.start_trial``.
    If the trial is expired or tampered with, the user can pre-activate via
    a ``YOURAPP_LICENSE_KEY`` env var (useful for enterprise rollouts).
    Otherwise we print instructions and exit — there is NO Tk dialog here.
    """
    from your_module import LicenseManager  # adjust import

    lm = LicenseManager()
    can_run, *_ = lm.get_status()
    if can_run:
        return

    env_key = os.environ.get("YOURAPP_LICENSE_KEY")
    if env_key:
        ok, msg = lm.validate_license_key(env_key)
        print(f"[license] {msg}")
        if ok and lm.get_status()[0]:
            return

    print("Trial expired / license missing. Set YOURAPP_LICENSE_KEY and relaunch.")
    sys.exit(1)


def run_web_app(port: int = 8502):
    _ensure_license_or_exit()

    from autostart import register_autostart  # ../templates/autostart.py
    register_autostart(app_name="YourApp")

    # Lazy import: the web module must define ``app`` (Bottle instance),
    # ``STARTUP_STATE`` (dict) and ``init_models(loader)``.
    app_dir = Path(__file__).parent
    if str(app_dir) not in sys.path:
        sys.path.insert(0, str(app_dir))
    import web_app as web

    from headless_loader import HeadlessLoader
    loader = HeadlessLoader(web.STARTUP_STATE)

    def _bootstrap():
        loader.load_all()
        if loader.progress.get("ready"):
            try:
                web.init_models(loader)
            except Exception as e:
                import traceback; traceback.print_exc()
                web.STARTUP_STATE.update(
                    ready=False, error=f"init_models failed: {e}")
    threading.Thread(target=_bootstrap, daemon=True).start()

    def _open_browser():
        time.sleep(1.5)
        try:
            webbrowser.open(f"http://localhost:{port}")
        except Exception:
            pass
    threading.Thread(target=_open_browser, daemon=True).start()

    print(f"Web app running at http://localhost:{port}")
    web.app.run(host="localhost", port=port, quiet=True, debug=False)


if __name__ == "__main__":
    run_web_app()
