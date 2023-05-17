var connected = false;
var img = null;

const connect = document.getElementById('connectBtn');
const previewBox = document.getElementById("preview-box");
const liveStream = document.getElementById("live-stream");
const streamPlaceholder = document.getElementById("stream-placeholder");
const topic = document.getElementById("topic");
const imgBox = document.getElementById("img-box");


connect.addEventListener('click', () => {
  if (connected) {
    connected = false;

    previewBox.style = "display: block;"
    connect.innerText="Connect";
    connect.className="btn btn-success"
    stopStream();

  } else {
    connected = true;

    previewBox.style = "display: none;"
    connect.innerText="Disconnect";
    connect.className="btn btn-danger"
    startStream();
  };
});

function startStream() {
  img = document.createElement('img');
  img.src = `/video_feed?topic=${topic.value}`;
  img.style = 'width: 100%; height: auto;'
  img.className = 'stream-preview';

  const node = liveStream.content.cloneNode(true);
  node.getElementById("img-box").appendChild(img);
  streamPlaceholder.appendChild(node);

  img.onerror = () => {
    console.log('error');
  }
}

function stopStream() {
  streamPlaceholder.innerHTML = '';
  img.src = null;
}
