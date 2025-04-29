# Work tracker

Note: Use webRTC(aiortc) and webTransport(aioquic)</br>

instructions :

- Run `python3 http3_server.py -c certificate.pem -k certificate.key --fps 60 --grav 0 --vel 1000.0 1000.0 --cor 1` for latency check from server
- Run `python3 http3_server.py -c certificate.pem -k certificate.key --fps 60 --grav 980 --vel 1000.0 1000.0 --cor 0.98` for realistic stream from server
- Run `google-chrome   --enable-experimental-web-platform-features   --ignore-certificate-errors-spki-list=ggR1vjmsgl5RdfYS3f5C2nYyZ3LRrjfOyD/Va/JLcXQ=   --origin-to-force-quic-on=localhost:4433   https://localhost:4433/` for web app
- Click on `connect` to start
- Modify `window_size`, `framerate`, `initial velocity vector` and `coefficient of restituition` in [demo.py](../server/demo.py)


## Sim
- [x] Create sandbox.py to design the sim
- [x] Add gravity physics
- [x] Add Collision physics
- [x] Generate frames

## Client
- [x] Setup simple webApp using js
- [x] Send a webRTC request over webtransport (tried hard to set up own webTransport http3 server based on googlechrome/examples; switched to using [demo.py](https://github.com/aiortc/aioquic/blob/main/examples/demo.py) and [http3_server.py](https://github.com/aiortc/aioquic/blob/main/examples/http3_server.py) example from aioquic after wasting a lot of time)
(to gen key and certificate, look at comment in [googlechrome/samples/webtransport/webtransport_server.py](https://github.com/GoogleChrome/samples/blob/gh-pages/webtransport/webtransport_server.py))

## Server
- [x] Establish handshake by confirming connection with client (datagrams were small and are apparently inherently unreliable for handshakes by design, the offer was 5.5kb from client i kept getting errors so i switch to stream, encountered unterminated json and realised that streams are sent as packets so added buffers on server and client to send and receive long messages) (not clear on what to send back after receiving offer, does it mean echo back? made no sense as it wasnt being used or displayed, assumed it to be responding with answer and sent it back with frames)
- [x] Attempt streaming blank frames to test communication
- [x] Spawn Simulation Thread (used a queue of size 10 as )
- [x] Consume frames 
- [x] Encode in h.264 (used aiortc/examples's force_codec)
- [x] Send over webRTC (Verified using chrome://webrtc-internals/)

## Client
- [x] get frames from server
- [x] Display frame and find ball location
- [x] Return location via WebTransport. (Unclear on what "both WebTransport" means, assuming it means the bidirectional stream)( copying the frame to hiddencanvas, get pixel data, find weighted average  of with their indices on red channel to find centroid, used a small r>5 to remove minor compression artifacts if they occur; noticed some in vp8 before forcing codec, not sure if theyll occure here but just being safe. )

## Server
- [x] Receive detected location 
- [x] Compute error and transmit to client via WebTransport (store current location when frames geenrated, access in demo.py and check with received detections, maybe used to check latency? better to have constant velocity (coeff or restitution = 1; gravity = 0))

## Client
- [x] Receive the transmitted err data and display (limited to 2 decimal places as output statement was jittery)

## Shutdown
- [x] Handle graceful shutdown of server (cleaned up resources based on on_shutdown from webcam.py example in aiortc/examples and closed simulation thread. caught sigint in http3_server and triggered on_shutdown)

## Testing
- [x] Unit tests for simulation worker (ball physics, frame generation, thread start and stop) 
- [x] use unittest. 
- [x] Pass all tests
- [x] Documented

- test_collision_with_floor: 

- test_collision_with_roof

- test_collision_with_left_wall

-  

## Deployment
- [ ] Dockerize server
- [ ] Deploy using kubernetes
- [ ] Document deploying and decisions
- [ ] Share screen capture
- [ ] include submission_date.txt containing the date that you finished the code
- [ ] copress in valid zip and upload (git archive --format=zip --output /full/path/to/zipfile.zip main )
