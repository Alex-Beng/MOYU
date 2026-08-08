"""Web 终端 —— 实时展示 scrcpy 截屏 + 控制器状态"""
import asyncio
import json
import logging
import time

import cv2
from aiohttp import web

logger = logging.getLogger(__name__)

_PAGE = """\
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>MOYU 实时画面</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { background:#000; font-family:monospace; }
#status {
  position:fixed; top:12px; left:12px; z-index:10;
  background:rgba(0,0,0,0.85); color:#0f0; padding:10px 16px;
  border-radius:6px; font-size:14px; line-height:1.6;
  min-width:220px; pointer-events:none;
}
#status .row { display:flex; }
#status .label { color:#888; width:60px; flex-shrink:0; }
#status .value { color:#0f0; }
.ctrl-toggle {
  margin-top:6px; padding:3px 12px; border-radius:4px;
  font-size:13px; cursor:pointer; text-align:center;
  pointer-events:auto; user-select:none;
}
.ctrl-toggle.on  { background:#0f0; color:#000; }
.ctrl-toggle.off { background:#555; color:#aaa; }
#panel {
  display:none; margin-top:6px; pointer-events:auto;
  border-top:1px solid #444; padding-top:6px;
}
.ctrl-row { display:flex; align-items:center; gap:6px; margin-bottom:4px; }
.ctrl-row select {
  flex:1; background:#333; color:#0f0; border:1px solid #555;
  border-radius:3px; padding:3px 6px; font-size:13px; font-family:monospace;
}
.ctrl-row button {
  background:#0a0; color:#000; border:none; border-radius:3px;
  padding:4px 10px; font-size:13px; cursor:pointer; font-family:monospace;
}
.ctrl-row button:hover { background:#0f0; }
#stream { width:100%; height:100vh; object-fit:contain; cursor:crosshair; }
#click-feedback {
  position:fixed; z-index:20; pointer-events:none;
  width:20px; height:20px; border:2px solid #f00; border-radius:50%;
  transform:translate(-50%,-50%); display:none;
}
#click-feedback::after {
  content:''; position:absolute; top:50%; left:50%;
  width:2px; height:20px; background:#f00;
  transform:translate(-50%,-50%) rotate(45deg);
}
</style>
</head>
<body>
<div id="status">
  <div class="row"><span class="label">mode</span><span class="value" id="v-mode">-</span></div>
  <div class="row"><span class="label">state</span><span class="value" id="v-state">-</span></div>
  <div class="row"><span class="label">moves</span><span class="value" id="v-moves">-</span></div>
  <div class="row"><span class="label">uptime</span><span class="value" id="v-uptime">-</span></div>
  <div class="row"><span class="label">solve</span><span class="value" id="v-solve">-</span></div>
  <div class="ctrl-toggle on" id="pause-toggle">⏸ 暂停</div>
  <div class="ctrl-toggle on" id="panel-toggle">🔧 控制面板</div>
  <div id="panel">
    <div class="ctrl-row">
      <select id="recipe-select"></select>
      <button id="recipe-switch">切换</button>
    </div>
    <div class="ctrl-row">
      <select id="state-select">
        <option>init</option><option>scramble</option><option>solve</option>
        <option>re_rank</option><option>re_holder</option><option>re_team</option><option>re_week</option>
      </select>
      <button id="state-set">跳转</button>
    </div>
  </div>
  <div class="ctrl-toggle on" id="click-toggle">点击关闭</div>
</div>
<div id="click-feedback"></div>
<img id="stream" src="/stream">
<script>
const img = document.getElementById('stream');
const fb = document.getElementById('click-feedback');
const toggle = document.getElementById('click-toggle');
const panelToggle = document.getElementById('panel-toggle');
const panel = document.getElementById('panel');
const pauseToggle = document.getElementById('pause-toggle');
let clickEnabled = true;

panelToggle.addEventListener('click', function() {
  const show = panel.style.display !== 'block';
  panel.style.display = show ? 'block' : 'none';
  this.className = show ? 'ctrl-toggle on' : 'ctrl-toggle off';
});

toggle.addEventListener('click', function() {
  clickEnabled = !clickEnabled;
  this.className = clickEnabled ? 'ctrl-toggle on' : 'ctrl-toggle off';
  this.textContent = clickEnabled ? '点击关闭' : '点击开启';
  img.style.cursor = clickEnabled ? 'crosshair' : 'default';
});

pauseToggle.addEventListener('click', async function() {
  const paused = this.dataset.paused === 'true';
  try {
    const r = await fetch('/api/pause', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body:JSON.stringify({paused: !paused})
    });
    const d = await r.json();
    this.dataset.paused = d.paused;
    this.className = d.paused ? 'ctrl-toggle off' : 'ctrl-toggle on';
    this.textContent = d.paused ? '▶ 继续' : '⏸ 暂停';
  } catch(e) {}
});

img.addEventListener('click', async function(e) {
  if (!clickEnabled) return;
  const rect = this.getBoundingClientRect();
  const nw = this.naturalWidth, nh = this.naturalHeight;
  if (!nw || !nh) return;
  const scale = Math.min(rect.width / nw, rect.height / nh);
  const dispW = nw * scale, dispH = nh * scale;
  const offX = (rect.width - dispW) / 2, offY = (rect.height - dispH) / 2;
  const imgX = Math.round((e.clientX - rect.left - offX) / scale);
  const imgY = Math.round((e.clientY - rect.top - offY) / scale);

  fb.style.left = e.clientX + 'px';
  fb.style.top = e.clientY + 'px';
  fb.style.display = 'block';
  setTimeout(() => fb.style.display = 'none', 600);

  try {
    await fetch('/api/click', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body:JSON.stringify({x:imgX, y:imgY})
    });
  } catch(e) {}
});

async function loadRecipes() {
  try {
    const r = await fetch('/api/recipes');
    const list = await r.json();
    const sel = document.getElementById('recipe-select');
    list.forEach(f => { const o = document.createElement('option'); o.value = f; o.textContent = f; sel.appendChild(o); });
  } catch(e) {}
}
loadRecipes();

document.getElementById('recipe-switch').addEventListener('click', async function() {
  const path = document.getElementById('recipe-select').value;
  const state = document.getElementById('state-select').value;
  if (!path) return;
  try {
    await fetch('/api/recipe', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({path, state}) });
  } catch(e) {}
});

document.getElementById('state-set').addEventListener('click', async function() {
  const state = document.getElementById('state-select').value;
  if (!state) return;
  try {
    await fetch('/api/state', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({state}) });
  } catch(e) {}
});

async function poll() {
  try {
    const r = await fetch('/api/status');
    const d = await r.json();
    document.getElementById('v-mode').textContent = d.mode;
    document.getElementById('v-state').textContent = d.state;
    document.getElementById('v-moves').textContent = d.current_moves || '-';
    const t = Math.round(d.uptime);
    const pad = n => String(n).padStart(2,'0');
    document.getElementById('v-uptime').textContent = pad(Math.floor(t/3600)) + ':' + pad(Math.floor((t%3600)/60)) + ':' + pad(t%60);
    const s = d.solve_count, m = d.max_solves;
    document.getElementById('v-solve').textContent = m > 0 ? s + '/' + m : s;
    pauseToggle.dataset.paused = d.paused;
    pauseToggle.className = d.paused ? 'ctrl-toggle off' : 'ctrl-toggle on';
    pauseToggle.textContent = d.paused ? '▶ 继续' : '⏸ 暂停';
  } catch(e) {}
}
setInterval(poll, 500); poll();
</script>
</body>
</html>
"""


class WebFrameServer:
    """aiohttp 服务器，提供 MJPEG 流 + 控制器状态。"""

    def __init__(self, controller, host: str = "0.0.0.0", port: int = 8080):
        self.controller = controller
        self.host = host
        self.port = port

    @property
    def scrcpy(self):
        return self.controller.scrcpy

    async def start(self):
        app = web.Application()
        app.router.add_get("/", self._handle_index)
        app.router.add_get("/stream", self._handle_stream)
        app.router.add_get("/frame", self._handle_frame)
        app.router.add_get("/api/status", self._handle_status)
        app.router.add_post("/api/click", self._handle_click)
        app.router.add_get("/api/recipes", self._handle_list_recipes)
        app.router.add_post("/api/recipe", self._handle_switch_recipe)
        app.router.add_post("/api/state", self._handle_set_state)
        app.router.add_post("/api/pause", self._handle_pause)
        runner = web.AppRunner(app, access_log=None)
        await runner.setup()
        await web.TCPSite(runner, self.host, self.port).start()
        logger.info("Web 终端 http://%s:%d", self.host, self.port)

    async def _handle_index(self, request):
        return web.Response(text=_PAGE, content_type="text/html")

    async def _handle_frame(self, request):
        frame = self.scrcpy.last_frame
        if frame is None:
            return web.Response(status=204)
        _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        return web.Response(body=buf.tobytes(), content_type="image/jpeg")

    async def _handle_stream(self, request):
        resp = web.StreamResponse()
        resp.headers["Content-Type"] = "multipart/x-mixed-replace; boundary=frame"
        await resp.prepare(request)
        try:
            while True:
                frame = self.scrcpy.last_frame
                if frame is not None:
                    _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                    await resp.write(
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n"
                    )
                await asyncio.sleep(0.1)
        except (ConnectionResetError, ConnectionAbortedError):
            logger.debug("Web 客户端断开连接")

    async def _handle_status(self, request):
        cl = self.controller.cube_loop
        current = cl.current_moves
        if isinstance(current, list):
            moves_str = " ".join(s.get("move", "") for s in current if isinstance(s, dict))
            if not moves_str.strip():
                parts = []
                for s in current:
                    if not isinstance(s, dict) or "face" not in s:
                        continue
                    face_char = "URFDLB"[s["face"]]
                    if s["dir"] == 0:
                        dir_char = ""
                    elif s["dir"] == 1:
                        dir_char = "'"
                    else:
                        dir_char = "2"
                    parts.append(f"{face_char}{dir_char}")
                moves_str = " ".join(parts)
        elif isinstance(current, str):
            moves_str = current
        else:
            moves_str = None
        return web.Response(
            content_type="application/json",
            text=json.dumps({
                "mode": self.controller.mode,
                "state": self.controller.state,
                "current_moves": moves_str,
                "queue_pending": cl.move_queue.qsize(),
                "uptime": time.monotonic() - self.controller._start_time,
                "solve_count": self.controller._solve_count,
                "max_solves": self.controller._max_solves,
                "paused": self.controller._paused,
            }),
        )

    async def _handle_click(self, request):
        data = await request.json()
        x, y = data["x"], data["y"]
        logger.info("Web 远程点击 (%d, %d)", x, y)
        self.controller.scrcpy.tap(x, y)
        return web.Response(text="ok")

    async def _handle_list_recipes(self, request):
        from recipe.loader import RECIPES_DIR
        files = sorted(f.name for f in RECIPES_DIR.iterdir() if f.suffix == ".json")
        return web.json_response(files)

    async def _handle_switch_recipe(self, request):
        data = await request.json()
        path = data.get("path")
        state = data.get("state")
        if not path:
            return web.json_response({"error": "missing path"}, status=400)
        logger.info("Web 切换 recipe: %s", path)
        await self.controller.switch_recipe(path, state)
        return web.json_response({"ok": True})

    async def _handle_set_state(self, request):
        data = await request.json()
        state = data.get("state")
        if not state:
            return web.json_response({"error": "missing state"}, status=400)
        logger.info("Web 跳转状态: %s", state)
        self.controller.set_state(state)
        return web.json_response({"ok": True})

    async def _handle_pause(self, request):
        data = await request.json()
        paused = data.get("paused")
        if paused is None:
            paused = not self.controller.is_paused
        if paused:
            self.controller.pause()
        else:
            self.controller.resume()
        logger.info("Web 暂停状态: %s", paused)
        return web.json_response({"paused": paused})
