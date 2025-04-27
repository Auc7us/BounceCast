const connect_btn = document.getElementById('connect_btn');
const remote_video = document.getElementById('remote_video');
const error_display = document.getElementById('error_display');

async function init() {
  console.log('Connect button clicked. Starting handhshake');
  const url = 'https://localhost:4433/connect';

  let transport;
  try {

    transport = new WebTransport(url);
    await transport.ready;
    console.log('wt session is ready');
    error_display.textContent = 'Connected';

    transport.closed
      .then(() => console.log('session closed normally'))
      .catch((err) => console.warn('session closed unexpectedly', err));

    const { readable, writable } = await transport.createBidirectionalStream();  

    const writer = writable.getWriter();
    const reader = readable.getReader();
    const encoder = new TextEncoder();
    const decoder = new TextDecoder();

    await writer.write(encoder.encode('Hello from client!'));

    (async () => {
      while (true) {
        const { value, done } = await reader.read();
        if (done) {
          console.log('stream closed by server');
          break;
        }
        console.log('Received data:', decoder.decode(value));
      }
    })();

  } 
  
  catch (e) {
    console.error('webTransport failed:', e);
    error_display.textContent = `Error: ${e.message}`;
  }

}

connect_btn.addEventListener('click', init);
