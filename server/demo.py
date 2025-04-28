import datetime
import os
import json
import asyncio
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack

from starlette.applications import Starlette
from starlette.responses import FileResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.types import Receive, Scope, Send

ROOT = os.path.dirname(__file__)
STATIC_ROOT = os.environ.get("STATIC_ROOT", os.path.join(ROOT, "client"))
STATIC_URL = "/"
LOGS_PATH = os.path.join(STATIC_ROOT, "logs")
QVIS_URL = "https://qvis.quictools.info/"

templates = Jinja2Templates(directory=os.path.join(ROOT, "templates"))

class TempVideoTrack(MediaStreamTrack):
    kind = "video"
    async def recv(self):
        await asyncio.sleep(1/30)
        return None

async def homepage(request):
    """
    Simple homepage.
    """
    return FileResponse(os.path.join(STATIC_ROOT, "index.html"))

async def wt(scope: Scope, receive: Receive, send: Send) -> None:
    """
    WebTransport echo endpoint.
    """
    # accept connection
    print("starting wt connection")
    message = await receive()
    assert message["type"] == "webtransport.connect"
    await send({"type": "webtransport.accept"})
    print("wt connected")
    buffer = b""
    pc = RTCPeerConnection()
    while True:
        message = await receive()
        if message["type"] == "webtransport.stream.receive":
            buffer += message["data"]
            try:
                obj = json.loads(buffer.decode())
                # print("received:", obj)

                if obj.get("type") == "sdp-offer":
                    print("received sdp offer ")
                    # print(obj["sdp"])
                    await pc.setRemoteDescription(RTCSessionDescription(sdp=obj["sdp"], type="offer"))
                    pc.addTrack(TempVideoTrack())

                    answer = await pc.createAnswer()
                    await pc.setLocalDescription(answer)

                    answer_message = {
                        "type": "sdp-answer",
                        "sdp": pc.localDescription.sdp
                    }

                    await send({
                        "data": json.dumps(answer_message).encode(),
                        "stream": message["stream"],
                        "type": "webtransport.stream.send",
                    })
                    print("replied with sdp answer")

                buffer = b""

            except json.JSONDecodeError:
                pass


starlette = Starlette(
    routes=[
        Route("/", homepage),
        Mount(STATIC_URL, StaticFiles(directory=STATIC_ROOT, html=True)),
    ]
)


async def app(scope: Scope, receive: Receive, send: Send) -> None:
    if scope["type"] == "webtransport" and scope["path"] == "/wt":
        await wt(scope, receive, send)
    else:
        await starlette(scope, receive, send)
