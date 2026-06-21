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
  background:rgba(0,0,0,0.75); color:#0f0; padding:10px 16px;
  border-radius:6px; font-size:14px; line-height:1.6;
  min-width:200px; pointer-events:none;
}
#status .row { display:flex; }
#status .label { color:#888; width:60px; flex-shrink:0; }
#status .value { color:#0f0; }
#click-toggle {
  margin-top:8px; padding:4px 12px; border-radius:4px;
  font-size:13px; cursor:pointer; text-align:center;
  pointer-events:auto; user-select:none;
}
#click-toggle.on  { background:#0f0; color:#000; }
#click-toggle.off { background:#555; color:#aaa; }
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
  <div id="click-toggle" class="on">点击关闭</div>
</div>
<div id="click-feedback"></div>
<img id="stream" src="/stream">
<script>
const img = document.getElementById('stream');
const fb = document.getElementById('click-feedback');
const toggle = document.getElementById('click-toggle');
let clickEnabled = true;

toggle.addEventListener('click', function() {
  clickEnabled = !clickEnabled;
  this.className = clickEnabled ? 'on' : 'off';
  this.textContent = clickEnabled ? '点击关闭' : '点击开启';
  img.style.cursor = clickEnabled ? 'crosshair' : 'default';
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
        runner = web.AppRunner(app)
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
            }),
        )

    async def _handle_click(self, request):
        data = await request.json()
        x, y = data["x"], data["y"]
        logger.info("Web 远程点击 (%d, %d)", x, y)
        self.controller.scrcpy.tap(x, y)
        return web.Response(text="ok")
