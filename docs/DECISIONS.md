# Decisions, Learnings and Challenges

## Server

- Being fairly new to networking, internet was my ally. Since I had to use webTransport and webRTC, with webTransport being failry new and not widely adopted, most of the sources recommended `aiortc` and `aioquic` in python, as they are most beginner friendly. aioquic and aiortc being developed by the same oraganisation also made it an easy choice to begin with. This would also make openCV based frame generation eazy. 

## Web APP

- The WebApp was supposed to play video in a browser and communicate with the server so I natually chose js. Having previous made a webGL based game, it was easy to get started and have a basic webpage to test my code.

## Simulation
I decided on starting with the simulation part of the project as this was something I fin really fun and could quickly get out of the way. 

- I had to design a bouncing ball simulator. Started with the idea of simulating gravity for simple free fall mechanics. Then added a coefficient of restitution to add a more natural fell to the simulation of the bouncing ball. 
- I assumed the ball to be a standard size 7 basketball. computed radius and it cameout to be really close to 12cm. Hence decided to 1 pixel = 1cm scale and chose a decent 640x480 VGA frame (6.4m x4.8m room) for the ball to bounce. and hence picked orange for the ball. 
- Need the fps to be configurable so recorded timestamps, computed frame generation time and used that to decide the sleep time to maintain consistent fps frame generation.
- Collision mechanics were fairly simple, check if edges of the ball (center+-radius) touched the edge and reverse velocity vector components
- Finally created a queue of size 10 (just being safe) to push frames to and pull frames from. Couldve used a circular buffer but felt in-built queue with get and push would suffice as time complexity is same o(1) per frame and no significant benefit in python.


## WebTransport
- I had to spend significant amount of time trying to understand what each term meant, and how the protocol worked. Found the documention and resouces available for aioquic to be significantly limiting and examples provided too overwheling to just dive into. 
- Found a [GoogleChrome sample](https://github.com/GoogleChrome/samples/blob/gh-pages/webtransport/webtransport_server.py) that helped me understand the process a bit better. I started working on my own python server for http3 communication based on this example and documentation. Spent 5-6 hours on this with no luck on being able to display a simple web page I wrote in js to open.

- I then and finally decided to pivot and spend time understanding the provided [http3_server.py](https://github.com/aiortc/aioquic/blob/main/examples/http3_server.py) and after some effort felt I could directly use it as the backend to my backend for webTransport communication. Turns out I had overlooked their [demo.py]((https://github.com/aiortc/aioquic/blob/main/examples/demo.py)) which soon helped me a lot in getting started. 

- Stripped it down and was finally able to get the web page to launch. The time spent on google chrome sample was also useful as it helped me with setting the right flags for the browser, generating fingerprint and launching.

- Establish handshake by confirming connection with client was the next goal. I started with datagrams, but they were small and are apparently inherently unreliable for handshakes by design, the SDP offer was 5.5kb from client. I kept noticing no messages being sent, so I switched to using streams.

- Then I encountered unterminated json and realised that streams are sent as packets so added buffers on server and client to send and receive long messages . I was not clear on what to send back after receiving offer, does it mean echo back? made no sense as it wasnt being used or displayed, assumed it to be responding with answer and sent it back with frames.


## WebRTC
- This was relatively eazy compared to sending the first message over using webTransport. Found aiortc/examples like webcam and server extremely helpful along with a couple of community written articles. 
- Created a video request sdp offer from client, sent it to server, and tested a response with a trial blank video stream i set up to send the sdp answer back. 
- I noticed the default codec was the first one in the sdp offer which was VP8. Used aiortc/examples's force_codec method to enforce H264 and verified it using chrome://webrtc-internals/
- Created a stream using `MediaStreamTrack` from aioRTC after spinning up a thread on receiveing offer. 
- Finally sent the stream and was able to receive it on the client end.

## Compute Center on Client
- Copied frame to a hidden canvas element in order to access frame pixel data. iterated over all pixels to find ones greater than a small threshold in red channel. Computed centroid using weighted average. 
- The small threshold was used as i noticed a lot of artifacts when i streamed using VP8 and wanted to be safe in case of aritfacts due to encoding in h264. 
- Unclear on what "both WebTransport" means, assuming it means the bidirectional stream. 

## Subsequent Communication
- This was fairly simple and straight fardward after all the time I put into the project. Had the bidirectional stream on both, used them to send messages over WT and checked type to trigger respective fucntions

## Error
- Felt the Error was being used to test communication latency and hence made velocity configurable  and started using gravity set to 0 and perfectly elastic collisions as we need to maintain magnitude of velocity.

## Tests 
- Wrote unit tests to test all of ball physics and collisions. Tests to assert tread start stop. Finally  check frame generation and video track generation by asserting expected frame datatypes.


## Kubernetes:
- I mostly used `docker compose` and our own wrapper of docker compose called `autonomy-toolkit`, so getting comfortable with kubernetes took some effort and time. Once I got started, I had a hard time getting my homepage to show on launching the web app. 

- Then spent a lot of time trying to get first handshake established after deployment. Started using loadbalancer as its usually used in minikube. Could not get it to work and after spending a lot of time digging, I noticed these on google:
    - Load Balancer Support: Cloud vendor LoadBalancers may have limited support for QUIC, especially concerning IETF QUIC protocol and QUIC address migration. 
    - Kube-proxy Issues: When using NodePort to expose QUIC services, if kube-proxy adopts the ipvs mode, it can encounter bugs that discard UDP packets, potentially causing QUIC services to be unavailable. 
    Hence use `nodePort` instead of `LoadBalancer` and `hostNetWork: True`. 

- I finally had the homepage displayed.

- Next the sdp webtransport handshake did not pass. Turns out coz I was using a hardcoded URL in `app.js` to trigger webTrasport, due to portforwarding in minikube, the localhost URL is no longer valid. I  had to switch to dynamis URL based on homepage URL. At this point docker inside minikube decided to cache the information and despite using `--no-cache` flag in build I kept seeing the same hardcoded URL. took a while to fix as I finally had to delete minikube, start over, force prune docker and delete all lingerining images and containers before I could proceed. 

- I was finally able to get the vvideo to play and stream data and display error but i notice that i freezes sometime after it start. I spent a decent chunk of time trying to find a fix but all the articles, reddit posts, github issues i read made it seem like QUIC isnt fully supported on kubenetes/minikube. Maybe increasing my allocated resources to the VM might help but I unfortunately didnt have enough time to test and document. 