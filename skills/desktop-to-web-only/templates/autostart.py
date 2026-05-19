"""Template: cross-platform auto-start on user login.

Call ``register_autostart(app_name="YourApp")`` once during startup. All
failures are caught and logged — auto-start is a "nice to have", never a
blocker for launching the app.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


def _command_for_self() -> str:
    """Build the command line that re-launches the current program."""
    if getattr(sys, "frozen", False):
        # PyInstaller / cx_Freeze packaged binary
        return f'"{sys.executable}"'
    main_script = Path(sys.argv[0]).resolve()
    return f'"{sys.executable}" "{main_script}"'


def _register_windows(app_name: str) -> None:
    import winreg  # type: ignore
    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0, winreg.KEY_SET_VALUE,
    )
    try:
        winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, _command_for_self())
    finally:
        winreg.CloseKey(key)


def _register_macos(app_name: str) -> None:
    bundle = f"com.{app_name.lower()}.autostart"
    plist_dir = Path.home() / "Library" / "LaunchAgents"
    plist_dir.mkdir(parents=True, exist_ok=True)
    plist_path = plist_dir / f"{bundle}.plist"

    if getattr(sys, "frozen", False):
        program_args = [sys.executable]
    else:
        program_args = [sys.executable, str(Path(sys.argv[0]).resolve())]
    args_xml = "\n".join(f"        <string>{a}</string>" for a in program_args)
    plist_path.write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
    <key>Label</key><string>{bundle}</string>
    <key>ProgramArguments</key><array>
{args_xml}
    </array>
    <key>RunAtLoad</key><true/>
</dict></plist>
""")
    if shutil.which("launchctl"):
        os.system(f'launchctl unload "{plist_path}" 2>/dev/null')
        os.system(f'launchctl load "{plist_path}" 2>/dev/null')


def _register_linux(app_name: str) -> None:
    autostart_dir = Path.home() / ".config" / "autostart"
    autostart_dir.mkdir(parents=True, exist_ok=True)
    desktop_path = autostart_dir / f"{app_name.lower()}.desktop"
    if getattr(sys, "frozen", False):
        exec_cmd = sys.executable
    else:
        exec_cmd = f"{sys.executable} {Path(sys.argv[0]).resolve()}"
    desktop_path.write_text(
        "[Desktop Entry]\n"
        "Type=Application\n"
        f"Name={app_name}\n"
        f"Exec={exec_cmd}\n"
        "X-GNOME-Autostart-enabled=true\n"
    )


def register_autostart(app_name: str = "MyApp") -> None:
    """Best-effort registration. Silently ignores all failures."""
    try:
        if sys.platform == "win32":
            _register_windows(app_name)
        elif sys.platform == "darwin":
            _register_macos(app_name)
        elif sys.platform.startswith("linux"):
            _register_linux(app_name)
    except Exception as e:  # pragma: no cover - best effort
        print(f"[autostart] could not register {app_name}: {e}")
