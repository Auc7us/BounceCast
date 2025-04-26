# Work tracker

Note: Use webRTC (aiortc)  and webTransport

## Sim
- [x] Create sandbox.py to design the sim
- [x] Add gravity physics
- [x] Add Collision physics
- [x] Generate frames

## Server
- [ ] Spawn Sim Thread
- [ ] Consume frames
- [ ] Encode in h.264 
- [ ] Send over webRTC

## WebApp

### Client
- [ ] Setup simple webApp using js
- [ ] get frames from server
- [ ] Display frame and find ball location
- [ ] Return location and meta data via WebTransport

## Server
- [ ] Receive detected location
- [ ] Compute error and transmit to client via WebTransport

### Client