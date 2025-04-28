const connect_btn = document.getElementById('connect_btn');
const remote_video = document.getElementById('remote_video');
const status_display = document.getElementById('status_display');

async function init() {
  console.log('Connect button clicked');
  const url = 'https://localhost:4433/wt';

  let transport;
  try {

    transport = new WebTransport(url);
    await transport.ready;
    console.log('wt session is ready');
    status_display.textContent = 'Connected';
    
    const pc = new RTCPeerConnection();
    pc.ontrack = (event) => {
      if (event.track.kind === 'video') {
        remote_video.srcObject = event.streams[0];
      }
    };

    const offer = await pc.createOffer({ offerToReceiveVideo: true });
    await pc.setLocalDescription(offer);

    const sdpOfferString = offer.sdp;

    const { readable, writable } = await transport.createBidirectionalStream();  

    const writer = writable.getWriter();
    const reader = readable.getReader();
    const encoder = new TextEncoder();
    const decoder = new TextDecoder();

    const message = {
      type: "sdp-offer",
      sdp: sdpOfferString
    };

    console.log('spd-offer',JSON.stringify(message))
    transport.closed
      .then(() => {status_display.textContent = 'Session closed';})
      .catch((err) => {status_display.textContent = 'Session closed unexpectedly';});

    await writer.write((encoder.encode(JSON.stringify(message))));
    console.log('sent sdp offer to server');

    (async () => {
      let buffer = "";
      while (true) {
        const { value, done } = await reader.read();
        if (done) {
          status_display.textContent = 'stream closed';
          break;
        }
        buffer += decoder.decode(value);
        try {
          const message = JSON.parse(buffer);
          console.log('Received complete json:', message);
          status_display.textContent = "Received reply";
          if (message.type === "sdp-answer") {
            const remoteDesc = new RTCSessionDescription({
              type: "answer",
              sdp: message.sdp
            });
            await pc.setRemoteDescription(remoteDesc);
            status_display.textContent = "Hand shake completed; connection established";
          }

          buffer = "";
        } catch (e) {
          // not a complete json. buffer.
        }
      }
    })();

  } 
  
  catch (e) {
    console.error('webTransport failed:', e);
    status_display.textContent = `Error: ${e.message}`;
  }

}

connect_btn.addEventListener('click', init);
