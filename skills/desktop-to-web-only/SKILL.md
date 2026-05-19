---
name: desktop-to-web-only
description: Convert a Python Tkinter desktop application into a web-only application that ships with a Bottle/Flask web server. Removes the desktop window entirely, keeps installation/loading progress visible in the browser, adds a "Stop App" control to the web UI, and registers the app for auto-start at user login. Also covers extending free-trial license durations. Use this skill whenever a user says things like "remove the desktop GUI", "make it web only", "show a startup progress page in the browser", "let me stop the app from the browser", "auto-launch on boot", or "extend free trial to N days/months/years" for a hybrid Tk + web Python application.
applyTo:
  - "**/*.py"
---

# Skill: Desktop GUI → Web-only Conversion

This skill packages the exact recipe used to convert the **Doqurix** project
from a hybrid Tkinter-desktop + Bottle-web app into a **web-only** application,
while preserving:

1. **Progress bars during model/data loading** (now rendered in the browser).
2. **A user-controlled shutdown** ("Stop App" button → `/api/shutdown`).
3. **Auto-start on user login** (Windows registry Run key; macOS `launchctl`
   plist; Linux `~/.config/autostart/*.desktop`).
4. **License/trial logic** (here: extend the free trial from 30 days to
   365 days — generalizable to any duration).

## When to use

Use this skill when:

- A Python desktop app uses Tkinter (or PyQt/PySide) **and** already ships a
  web UI alongside it, and the user wants to drop the desktop window.
- The user wants browser-based progress reporting during a slow startup
  (model download, ML model loading, DB warm-up, etc.).
- The user wants to "stop the app from the browser" (graceful shutdown
  endpoint) and/or auto-start on login.
- The user wants to change a trial-period duration in a `LicenseManager`-style
  class.

## When NOT to use

- The app has **no web server** yet — adding a web stack from scratch is a
  larger architectural change; do not auto-apply this skill.
- The app is a pure CLI tool (no GUI to remove).
- The web UI and desktop UI share deeply coupled state that can't be broken
  cleanly — flag this to the user and ask before proceeding.

## High-level transformation

```
Before:                         After:
  main.py                         main.py
    └── tk.Tk().mainloop()          └── HeadlessLoader → bottle_app.app.run()
    └── instantiates models in      └── instantiates same models headlessly
         the GUI class              └── auto-start registration
  bottle_app.py (optional)        bottle_app.py
    └── init_models(desktop_app)    └── init_models(loader)  # same shape
                                    └── /api/startup-progress
                                    └── /api/shutdown
                                    └── Stop App button injected into HTML
```

The trick that makes the migration cheap is that the web module already
accepted a `desktop_app`-shaped object (anything with `.llm`, `.embedder`,
…). We replace that object with a Tk-free **headless loader** that exposes
the same attributes. No web-route code has to change.

## Step-by-step instructions

Follow these steps in order. Each step has a matching template file in
[`templates/`](templates/).

### 1. Extend the trial duration (if requested)

In the `LicenseManager` (or equivalent) class, change the constant that
defines the free-trial window:

```python
# Before
_TRIAL_DAYS = 30
# After – 1 year free trial
_TRIAL_DAYS = 365
```

Search for any hard-coded `30` near license/trial code (e.g. UI warning
thresholds) and decide whether they should follow the new duration.

### 2. Add a headless model/data loader

Copy [`templates/headless_loader.py`](templates/headless_loader.py) into the
project (or inline the class into `main.py`). The class:

- Has the **same public attributes** that the web module's `init_models`
  expects (`llm`, `embedder`, `reranker`, `chroma_client`, `collection`,
  agent-specific collections, `agents`, …).
- Reports progress into a shared `dict` (`STARTUP_STATE`) — no Tk callbacks.
- Implements each `init_*` stage by **copying logic** from the corresponding
  method on the desktop GUI class, stripping all `self.root.after(...)` and
  `self.progress_window.*` calls and replacing them with `self._set(...)`.

### 3. Add startup-progress + shutdown endpoints to the web app

Copy [`templates/web_endpoints.py`](templates/web_endpoints.py) into the web
module. It defines:

- `STARTUP_STATE` — the dict the loader writes into.
- `LOADING_HTML` — a self-contained page that polls `/api/startup-progress`
  every ~700 ms and reloads `/` once `ready` is true.
- `@app.route('/')` — returns `LOADING_HTML` until ready, then the real UI.
- `@app.route('/api/startup-progress')` — JSON dump of `STARTUP_STATE`.
- `@app.route('/api/shutdown')` — calls `os._exit(0)` after a short delay
  (Bottle's default WSGI server has no graceful shutdown hook).

If the existing index route already exists, **replace it** rather than
adding a second one.

### 4. Inject a "Stop App" button into the existing UI HTML

To avoid surgically editing an enormous HTML string constant, use the
**string-replace-`</body>`** trick from
[`templates/stop_button_snippet.html`](templates/stop_button_snippet.html):

```python
_INDEX_WITH_STOP_BUTTON = INDEX_HTML.replace("</body>", _STOP_BUTTON_SNIPPET, 1)
```

The snippet adds a floating button bottom-right that calls
`POST /api/shutdown` after a `confirm()` prompt and then shows a full-screen
"Doqurix has been stopped" overlay.

### 5. Register the app for auto-start

Copy [`templates/autostart.py`](templates/autostart.py). The implementation:

- **Windows**: writes `HKCU\Software\Microsoft\Windows\CurrentVersion\Run\<AppName>`
  pointing at `sys.executable` (frozen) or `python main.py` (dev).
- **macOS**: writes a `LaunchAgent` `.plist` under
  `~/Library/LaunchAgents/<bundle>.plist` and runs `launchctl load`.
- **Linux**: writes a `~/.config/autostart/<app>.desktop` file.

Call it once near the top of the web launcher. Re-running it on every launch
keeps the path in sync if the user moves the binary.

### 6. Replace the desktop entry point

Replace the `if __name__ == "__main__":` block (and any `check_license_and_run`
helper that creates a Tk root) with the **web launcher** pattern from
[`templates/web_launcher.py`](templates/web_launcher.py):

```python
def run_web_app():
    _ensure_license_or_exit()    # headless: env-var fallback for activation
    register_autostart()         # best-effort, ignore failures
    import bottle_app
    loader = HeadlessLoader(bottle_app.STARTUP_STATE)
    threading.Thread(target=lambda: (loader.load_all(),
                                     bottle_app.init_models(loader)),
                     daemon=True).start()
    threading.Thread(target=lambda: (time.sleep(1.5),
                                     webbrowser.open("http://localhost:8502")),
                     daemon=True).start()
    bottle_app.app.run(host="localhost", port=8502, quiet=True, debug=False)
```

Important rules:

- **Do NOT** call any Tk dialogs from the new entry point. License failures
  must print an instruction and `sys.exit(1)`. Provide an env-var (e.g.
  `DOQURIX_LICENSE_KEY`) as a headless activation path.
- **Do NOT** remove the existing `DocumentQAApp` / GUI class — leave it
  unused. PyInstaller specs typically still reference `main.py`, and other
  code may import names from it. Removing is high-risk for low reward.
- Keep model-loading logic on a background thread so the web server can
  bind the port and serve the `LOADING_HTML` page immediately.

### 7. Verify

- Launch the app and confirm a browser tab opens to
  `http://localhost:8502` showing the loading page first, then the main UI.
- Click "Stop App" — the server process should exit within ~1s.
- Reboot (or sign out/in) — the app should auto-launch.
- On Windows, verify the Run key:
  ```powershell
  Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' Doqurix
  ```

## Common pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| Browser hangs on loading page forever | Loader thread crashed; `error` is set but the JS ignored it | Make sure `LOADING_HTML` surfaces `s.error` (template already does) |
| `/api/shutdown` returns but process keeps running | Some web servers ignore `sys.exit` inside a request thread | Use `os._exit(0)` from a daemon thread (template does this) |
| Auto-start fires but window does not open | `webbrowser.open` ran before Bottle bound the port | Sleep ~1.5 s before opening the browser, **or** open from JS after the loading page renders |
| First-run trial keeps re-starting from 0 | Trial file stored in a per-process temp dir | Store it under `%LOCALAPPDATA%` (Windows) / `~/.config` (Linux) / `~/Library/Application Support` (macOS) — keyed by a stable machine ID |
| PyInstaller build is missing `bottle_app` after refactor | Spec didn't list `bottle_app.py` in `datas` | Ensure `('bottle_app.py', '.')` is in the spec `datas` list |

## Files in this skill

- [SKILL.md](SKILL.md) — this document
- [templates/headless_loader.py](templates/headless_loader.py) — drop-in loader
- [templates/web_endpoints.py](templates/web_endpoints.py) — progress + shutdown endpoints
- [templates/stop_button_snippet.html](templates/stop_button_snippet.html) — UI injection
- [templates/autostart.py](templates/autostart.py) — cross-platform auto-start
- [templates/web_launcher.py](templates/web_launcher.py) — new `__main__` entry
