from flask import Flask, Response, request, render_template
from cv2 import VideoCapture, imencode, resize, INTER_AREA
from kafka import KafkaProducer
from threading import Thread

app = Flask(__name__, static_folder='assets', static_url_path='/assets')

def image_resize(image, width = None, height = None, inter = INTER_AREA):
    """Resize image maintaining the aspect ratio"""
    dim = None
    (h, w) = image.shape[:2]
    if width is None and height is None:
        return image

    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    resized = resize(image, dim, interpolation = inter)
    return resized

def publish_frames(url, topic):
    producer = KafkaProducer(bootstrap_servers=['kafka:19091'])
    camera = VideoCapture(url)
    while True:
        success, frame = camera.read()
        if not success:
            break
        frame = image_resize(frame, 640, 640)
        ret, buffer = imencode('.jpg', frame)
        frame = buffer.tobytes()
        producer.send(topic, value=frame)

def get_frames(url):
    """Get frames from rtsp camera"""
    camera = VideoCapture(url)
    while True:
        success, frame = camera.read()
        if not success:
            break
        frame = image_resize(frame, 640, 640)
        ret, buffer = imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/video_feed', methods=['POST'])
def start_feed():
    if request.headers.get('Content-Type') != 'application/json':
        return Response("Unsupported media type", status=415)
    
    cam_url = request.json['cam_url']
    topic = request.json['topic']
    
    if not cam_url or not cam_url.strip or not cam_url.startswith('rtsp://'):
        return Response('please enter valid value for cam_url', status=400)
    if not topic or not  cam_url.strip or not cam_url.isalnum:
        return Response('please enter alpha numeric value for topic', status=400)
        
    thread = Thread(target=publish_frames, args=(cam_url, topic))
    thread.start()
    
    return Response('Ok', status=200)
        
@app.route('/video_feed', methods=['GET'])
def video_feed():
    cam_url = request.args.get('cam_url')
    try:
        frame = get_frames(cam_url)
        return Response(frame, mimetype='multipart/x-mixed-replace; boundary=frame')
    except:
        return Response(status=404)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")