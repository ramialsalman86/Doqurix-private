"""Template: startup-progress and shutdown endpoints for a Bottle app.

Drop into the module that defines your ``app = Bottle()`` instance.
Adjust the ``return INDEX_HTML`` line to whatever your real "ready" page is.
"""

from __future__ import annotations

import json
import os
import threading
import time

from bottle import Bottle, response

app: Bottle  # type: ignore  # provided by your real module

# ---- Shared startup-state dict ------------------------------------------
STARTUP_STATE = {
    "ready": False,
    "error": None,
    "title": "Starting application",
    "status": "Booting...",
    "stage_index": 0,
    "stage_total": 0,
    "stage_label": "",
    "percent": 0,
    "download_bytes": 0,
    "download_total": 0,
}

# ---- Loading HTML polled by browser until ready -------------------------
LOADING_HTML = """<!DOCTYPE html><html><head><meta charset="UTF-8">
<title>Starting...</title>
<style>
 body{margin:0;font-family:'Segoe UI',sans-serif;background:#0f0f0f;color:#ececf1;
      display:flex;align-items:center;justify-content:center;height:100vh}
 .card{background:#1a1a1a;padding:36px 44px;border-radius:14px;width:460px;max-width:92vw;
       box-shadow:0 10px 40px rgba(0,0,0,.5)}
 h1{margin:0 0 6px;font-size:22px}
 .status{color:#b4b4b4;margin-bottom:18px;font-size:14px}
 .bar{background:#2a2a2a;border-radius:8px;overflow:hidden;height:14px}
 .fill{background:linear-gradient(135deg,#10a37f 0%,#1bc9a0 100%);
       height:100%;width:0%;transition:width .3s ease}
 .meta{margin-top:10px;font-size:12px;color:#6e6e80;display:flex;justify-content:space-between}
 .err{color:#ff6b6b;margin-top:14px;font-size:13px}
</style></head><body>
<div class="card">
  <h1 id="title">Starting...</h1>
  <div class="status" id="status">Booting...</div>
  <div class="bar"><div class="fill" id="fill"></div></div>
  <div class="meta"><span id="stage"></span><span id="pct">0%</span></div>
  <div class="err" id="err"></div>
</div>
<script>
function mb(b){return (b/1048576).toFixed(1)+' MB';}
async function poll(){
 try{
  const r=await fetch('/api/startup-progress');const s=await r.json();
  title.textContent=s.title||'Starting...';status.textContent=s.status||'';
  fill.style.width=(s.percent||0)+'%';pct.textContent=Math.round(s.percent||0)+'%';
  let st=s.stage_total?('Step '+s.stage_index+'/'+s.stage_total):'';
  if(s.download_total)st=mb(s.download_bytes)+' / '+mb(s.download_total);
  stage.textContent=st;
  if(s.error){err.textContent='Error: '+s.error;return;}
  if(s.ready){location.href='/';return;}
 }catch(e){}
 setTimeout(poll,700);
}poll();
</script></body></html>"""


# ---- Routes -------------------------------------------------------------
@app.route('/')
def index():
    if not STARTUP_STATE.get("ready"):
        response.content_type = 'text/html; charset=utf-8'
        return LOADING_HTML
    return INDEX_HTML  # type: ignore[name-defined]  # your real UI


@app.route('/api/startup-progress')
def startup_progress():
    response.content_type = 'application/json'
    return json.dumps(STARTUP_STATE)


@app.route('/api/shutdown', method=['POST', 'GET'])
def shutdown():
    response.content_type = 'application/json'

    def _exit_soon():
        time.sleep(0.4)
        os._exit(0)  # WSGI ref server has no clean shutdown hook

    threading.Thread(target=_exit_soon, daemon=True).start()
    return json.dumps({'success': True, 'message': 'Shutting down...'})
