# Work tracker

Note: Use webRTC(aiortc) and webTransport(aioquic)</br>


## Sim
- [x] Create sandbox.py to design the sim
- [x] Add gravity physics
- [x] Add Collision physics
- [x] Generate frames

## Client
- [x] Setup simple webApp using js
- [x] Send a webRTC request over webtransport 
(to gen key and certificate, look at comment in [googlechrome/samples/webtransport/webtransport_server.py](https://github.com/GoogleChrome/samples/blob/gh-pages/webtransport/webtransport_server.py))

## Server
- [x] Establish handshake by confirming connection with client 
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
- [x] Document code  

## Deployment
- [x] Dockerize server (finalized minimal requirments.txt, tested using local run, eposing port directly didnt work, had to explicitly state udp to expose udp port)
- [x] Deploy using kubernetes
- [x] Document deploying 
- [x] and decisions
- [x] add clear comments
- [ ] Share screen capture
- [x] include submission_date.txt containing the date that you finished the code
- [ ] copress in valid zip and upload (git archive --format=zip --output /full/path/to/zipfile.zip main )


## Instructions :

### Server:
#### Docker:
- build docker image: `docker build -t nimble-challenge-server .`
- run docker container: 
`docker run --rm -p 4433:4433/udp --name nimble-local-test  nimble-challenge-server`
- stop container: `docker stop nimble-local-test`

#### Python:
- `cd server`
- Run `python http3_server.py -c certificate.pem -k certificate.key --fps 60 --grav 0 --vel 1000.0 1000.0 --cor 1` for latency check from server
- Run `python http3_server.py -c certificate.pem -k certificate.key --fps 60 --grav 980 --vel 1000.0 1000.0 --cor 0.98` for realistic stream from server

### Client:
In a new terminal:
- Run `google-chrome   --enable-experimental-web-platform-features   --ignore-certificate-errors-spki-list=ggR1vjmsgl5RdfYS3f5C2nYyZ3LRrjfOyD/Va/JLcXQ=   --origin-to-force-quic-on=localhost:4433   https://localhost:4433/` for web app
- Click on `connect` to start


**Note:** You can modify `frame window size`, `framerate`, `initial velocity vector` and `coefficient of restituition` in [demo.py](../server/demo.py) or pass them as arguments used to run http3_server.py in cli as suggested above or in the [dockerfile](../dockerfile).

To test:
- Run `python server/unit_tests.py`