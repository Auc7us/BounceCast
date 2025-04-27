import argparse
import asyncio
import aioquic
from typing import Dict, Optional
from aioquic.asyncio import QuicConnectionProtocol, serve
from aioquic.h3.connection import H3_ALPN, H3Connection
from aioquic.h3.events import (H3Event, HeadersReceived, WebTransportStreamDataReceived)
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import ProtocolNegotiated, QuicEvent
import logging
import os
CLIENT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, "client")
)

BIND_ADDR = "0.0.0.0"
BIND_PORT = 4433
logging.basicConfig(level=logging.INFO)

class wtServerProtocol(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._http: Optional[H3Connection] = None
        self._buffers: Dict[int, bytearray] = {}

    def quic_event_received(self, event: QuicEvent) -> None:
        if isinstance(event, ProtocolNegotiated) and event.alpn_protocol in H3_ALPN:
                logging.info("enabling wt")
                self._http = H3Connection(self._quic, enable_webtransport=True)
        if self._http is not None:
            for h3_event in self._http.handle_event(event):
                self._h3_event_received(h3_event)
    
    def _h3_event_received(self, event: H3Event) -> None:
        if isinstance(event, HeadersReceived):
            headers = {}
            for header, value in event.headers:
                headers[header] = value
            
            method = headers.get(b":method")
            path   = headers.get(b":path", b"/").decode()

            logging.info(f"Received headers: {headers}")


            if method == b"GET":
                rel = path.lstrip("/")
                if not rel:
                    rel = "index.html"
                fp = os.path.join(CLIENT_ROOT, rel)

                try:
                    with open(fp, "rb") as f:
                        data = f.read()
                    ctype = "text/html"
                    if fp.endswith(".js"):
                        ctype = "application/javascript"
                    elif fp.endswith(".css"):
                        ctype = "text/css"

                    self._http.send_headers(
                        stream_id=event.stream_id,
                        headers=[
                            (b":status", b"200"),
                            (b"content-type", ctype.encode()),
                            (b"alt-svc", b'h3=":4433"; ma=86400')
                        ],
                        end_stream=False
                    )
                    self._http.send_data(
                        stream_id=event.stream_id,
                        data=data,
                        end_stream=True
                    )
                except FileNotFoundError:
                    self._send_response(event.stream_id, 404, end_stream=True)
                return

            if (headers.get(b":method") == b"CONNECT" and headers.get(b":protocol") == b"webtransport"):
                self._handshake_webtransport(event.stream_id, headers)
            else:
                self._send_response(event.stream_id, 400, end_stream=True)
        
        elif isinstance(event, WebTransportStreamDataReceived):
            sid = event.stream_id
            logging.info(f"received data on wt stream")
            if sid not in self._buffers:
                self._buffers[sid] = bytearray()
            self._buffers[sid].extend(event.data)

            if event.stream_ended: 
                data = bytes(self._buffers.pop(sid))
                self._http.send_data(stream_id=sid, data=data, end_stream=True)

    def _handshake_webtransport(self, stream_id: int, request_headers: Dict[bytes, bytes]) -> None:
        authority = request_headers.get(b":authority")
        path = request_headers.get(b":path")
        if authority is None or path is None:
            # `:authority` and `:path` must be provided.
            logging.warning("authority/path is none")
            self._send_response(stream_id, 400, end_stream=True)
            return
        if path == b"/connect":
            logging.warning("handshake succesful")
            self._send_response(stream_id, 200)
            self._session_id = self._http.create_webtransport_session(stream_id)
            logging.warning("wt session created")

        else:
            self._send_response(stream_id, 404, end_stream=True)

    def _send_response(self, stream_id: int, status_code: int, end_stream=False) -> None:
        headers = [(b":status", str(status_code).encode())]
        if status_code == 200:
            headers.append((b"sec-webtransport-http3-draft", b"draft02"))
        self._http.send_headers(stream_id=stream_id, headers=headers, end_stream=end_stream)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('certificate')
    parser.add_argument('key')
    args = parser.parse_args()

    configuration = QuicConfiguration(
        alpn_protocols=H3_ALPN,
        is_client=False,
        max_datagram_frame_size=65536,
    )
    configuration.load_cert_chain(args.certificate, args.key)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        serve(
            BIND_ADDR,
            BIND_PORT,
            configuration=configuration,
            create_protocol=wtServerProtocol,
        )
    )
    logging.info("Listening on https://{}:{}".format(BIND_ADDR, BIND_PORT))

    try:
        loop.run_forever()

    except KeyboardInterrupt:
        print("Shutting down")