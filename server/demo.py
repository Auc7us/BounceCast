import os
import json
import asyncio
import numpy as np
from av import VideoFrame
import fractions
import threading
import queue
from ballsim import BallSimulator

from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack, RTCRtpSender

from starlette.applications import Starlette
from starlette.responses import FileResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.types import Receive, Scope, Send

ROOT = os.path.dirname(__file__)
STATIC_ROOT = os.environ.get("STATIC_ROOT", os.path.join(ROOT, "client"))
STATIC_URL = "/"
# LOGS_PATH = os.path.join(STATIC_ROOT, "logs")
# QVIS_URL = "https://qvis.quictools.info/"

templates = Jinja2Templates(directory=os.path.join(ROOT, "templates"))

frame_queue = queue.Queue(maxsize=1)

class BallSimVideoTrack(MediaStreamTrack):
    kind = "video"

    def __init__(self, sim):
        super().__init__()
        self.sim = sim
        self.frame_count = 0

    async def recv(self):
        self.frame_count += 1
        # get latest frame
        while True:
            try:
                frame = self.sim.queue.get_nowait()
                break
            except queue.Empty:
                await asyncio.sleep(0.001)  # Small wait if no frame ready

        # Convert to WebRTC VideoFrame
        video_frame = VideoFrame.from_ndarray(frame, format="bgr24")
        video_frame.pts = self.frame_count
        video_frame.time_base = fractions.Fraction(1, self.sim.fps)
        return video_frame

def force_codec(pc, sender, forced_codec):
    kind = forced_codec.split("/")[0]
    codecs = RTCRtpSender.getCapabilities(kind).codecs
    matching_codecs = [c for c in codecs if c.mimeType == forced_codec]
    transceiver = next(t for t in pc.getTransceivers() if t.sender == sender)
    transceiver.setCodecPreferences(matching_codecs)

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
                if obj.get("type") == "sdp-offer":
                    print("received sdp offer ")
                    
                    sim = BallSimulator(width=640, height=480, fps=60, gravity=980, velocity=(1000.0, 1000.0), restitution=0.98)
                    sim.start()
                    track = BallSimVideoTrack(sim)
                    sender = pc.addTrack(track)
                    force_codec(pc, sender, "video/H264")

                    await pc.setRemoteDescription(RTCSessionDescription(sdp=obj["sdp"], type="offer"))
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
