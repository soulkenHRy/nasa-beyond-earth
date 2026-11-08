"""A tiny headless-Chrome driver (Chrome DevTools Protocol), used to check that the animations really play.

    async with Browser() as b:
        await b.open("file:///.../animations/F01_empty_lanes.html")
        print(await b.js("document.title"))
        await b.screenshot("/tmp/x.png")

Needs google-chrome on the PATH and the `websockets` package (already in .venv).
"""
from __future__ import annotations

import asyncio
import base64
import json
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.request

import websockets


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Browser:
    def __init__(self, width: int = 1400, height: int = 1000):
        self.width, self.height = width, height
        self.port = _free_port()
        self.profile = tempfile.mkdtemp(prefix="chrome-check-")
        self.proc = None
        self.ws = None
        self._id = 0
        self.console: list[str] = []

    async def __aenter__(self):
        exe = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
        self.proc = subprocess.Popen(
            [exe, "--headless=new", f"--remote-debugging-port={self.port}", f"--user-data-dir={self.profile}",
             f"--window-size={self.width},{self.height}", "--no-first-run", "--no-default-browser-check",
             "--hide-scrollbars", "--mute-audio", "--use-angle=swiftshader", "--enable-unsafe-swiftshader",
             "--allow-file-access-from-files", "about:blank"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        url = f"http://127.0.0.1:{self.port}/json/list"
        for _ in range(100):
            try:
                pages = [t for t in json.loads(urllib.request.urlopen(url, timeout=1).read()) if t["type"] == "page"]
                if pages:
                    break
            except OSError:
                pass
            time.sleep(0.1)
        else:
            raise RuntimeError("Chrome did not start")
        self.ws = await websockets.connect(pages[0]["webSocketDebuggerUrl"], max_size=None)
        await self.send("Page.enable")
        await self.send("Runtime.enable")
        await self.send("Emulation.setDeviceMetricsOverride", width=self.width, height=self.height,
                        deviceScaleFactor=1, mobile=False)
        return self

    async def __aexit__(self, *exc):
        try:
            if self.ws:
                await self.ws.close()
        finally:
            if self.proc:
                self.proc.terminate()
                try:
                    self.proc.wait(5)
                except subprocess.TimeoutExpired:
                    self.proc.kill()
            shutil.rmtree(self.profile, ignore_errors=True)

    async def send(self, method: str, **params):
        self._id += 1
        my_id = self._id
        await self.ws.send(json.dumps({"id": my_id, "method": method, "params": params}))
        while True:
            msg = json.loads(await self.ws.recv())
            if msg.get("method") == "Runtime.consoleAPICalled":
                self.console.append(" ".join(str(a.get("value", a.get("description", ""))) for a in msg["params"]["args"]))
            elif msg.get("method") == "Runtime.exceptionThrown":
                self.console.append("EXCEPTION " + msg["params"]["exceptionDetails"].get("text", "") + " " +
                                    str(msg["params"]["exceptionDetails"].get("exception", {}).get("description", "")))
            if msg.get("id") == my_id:
                if "error" in msg:
                    raise RuntimeError(f"{method}: {msg['error']}")
                return msg.get("result", {})

    async def js(self, expression: str, timeout: float = 60):
        """Run JavaScript in the page; promises are awaited; the result comes back as plain JSON."""
        r = await asyncio.wait_for(self.send("Runtime.evaluate", expression=expression, awaitPromise=True,
                                             returnByValue=True), timeout)
        if "exceptionDetails" in r:
            raise RuntimeError(r["exceptionDetails"].get("exception", {}).get("description", str(r["exceptionDetails"])))
        return r.get("result", {}).get("value")

    async def open(self, url: str, ready: str = "document.readyState === 'complete'", timeout: float = 60):
        await self.send("Page.navigate", url=url)
        t0 = time.time()
        while time.time() - t0 < timeout:
            await asyncio.sleep(0.2)
            try:
                if await self.js(f"Boolean({ready})"):
                    return
            except RuntimeError:
                pass
        raise TimeoutError(f"page not ready: {url}")

    async def wait_for(self, condition: str, timeout: float = 60, every: float = 0.25):
        t0 = time.time()
        while time.time() - t0 < timeout:
            if await self.js(f"Boolean({condition})"):
                return True
            await asyncio.sleep(every)
        return False

    async def screenshot(self, path: str, full_page: bool = False, clip: dict | None = None):
        params = {"format": "png", "captureBeyondViewport": full_page}
        if clip:
            params["clip"] = {**clip, "scale": 1}
        r = await self.send("Page.captureScreenshot", **params)
        with open(path, "wb") as fh:
            fh.write(base64.b64decode(r["data"]))
        return path

    async def click(self, x: float, y: float):
        for kind in ("mousePressed", "mouseReleased"):
            await self.send("Input.dispatchMouseEvent", type=kind, x=x, y=y, button="left", clickCount=1)
