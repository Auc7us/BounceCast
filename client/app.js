const connect_btn = document.getElementById('connect_btn');
const remote_video = document.getElementById('remote_video');
const error_display = document.getElementById('error_display');

async function init() {
  console.log('Connect button clicked. Setting up client…');

    //start webtransport
    //send SDP
    // display frame
    // detect ball
    // send detected x,y center on both?
    //receive err over webtrtansport and visualize it   

  error_display.textContent = 'Initializating';
}

connect_btn.addEventListener('click', init);
