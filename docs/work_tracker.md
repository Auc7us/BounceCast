# Work tracker

Note: Use webRTC(aiortc) and webTransport(aioquic)

## Sim
- [x] Create sandbox.py to design the sim
- [x] Add gravity physics
- [x] Add Collision physics
- [x] Generate frames

## Client
- [x] Setup simple webApp using js
- [x] Send a webRTC request over webtransport 

## Server
- [x] Establish handshake by confirming connection with client
- [ ] Spawn Simulation Thread
- [ ] Consume frames
- [ ] Encode in h.264 
- [ ] Send over webRTC

## Client
- [ ] get frames from server
- [ ] Display frame and find ball location
- [ ] Return location and meta data via WebTransport

## Server
- [ ] Receive detected location
- [ ] Compute error and transmit to client via WebTransport

## Client
- [ ] Receive the transmitted err data and display

# Testing
- [ ] Unit tests for client functions (frame parsing, error display, WebTransport/WebRTC connections)
- [ ] Unit tests for server functions (WebTransport handshake, error calculation, graceful shutdown)
- [ ] Unit tests for simulation worker (ball physics and frame generation)
- [ ] Any end to end tests?

## Deployment
- [ ] Dockerize server
- [ ] Deploy using kubernetes
- [ ] Document deploying and decisions
- [ ] Share screen capture
- [ ] include submission_date.txt containing the date that you finished the code
- [ ] copress in valid zip and upload (git archive --format=zip --output /full/path/to/zipfile.zip main )
