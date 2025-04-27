const connect_btn = document.getElementById('connect_btn');
const remote_video = document.getElementById('remote_video');
const error_display = document.getElementById('error_display');

async function init() {
  console.log('Connect button clicked');
  const url = 'https://localhost:4433/wt';

  let transport;
  try {

    transport = new WebTransport(url);
    await transport.ready;
    console.log('wt session is ready');
    error_display.textContent = 'Connected';
    
    const pc = new RTCPeerConnection();
    const offer = await pc.createOffer();
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

    transport.closed
      .then(() => {error_display.textContent = 'Session closed';})
      .catch((err) => {error_display.textContent = 'Session closed unexpectedly';});

    await writer.write((encoder.encode(JSON.stringify(message))));
    console.log('sent sdp offer to server');

    (async () => {
      while (true) {
        const { value, done } = await reader.read();
        if (done) {
          error_display.textContent = 'stream closed';
          break;
        }
        error_display.textContent = decoder.decode(value);
      }
    })();

  } 
  
  catch (e) {
    console.error('webTransport failed:', e);
    error_display.textContent = `Error: ${e.message}`;
  }

}

connect_btn.addEventListener('click', init);
