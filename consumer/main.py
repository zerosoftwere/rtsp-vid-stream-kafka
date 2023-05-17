from flask import Flask, Response, request, render_template
from kafka import KafkaConsumer
app = Flask(__name__, static_folder='assets', static_url_path='/assets')

def get_frames(topic):
    consumer = KafkaConsumer(topic, bootstrap_servers=['kafka:19091'], enable_auto_commit=True, 
                             value_deserializer= lambda x : x, group_id="cam", auto_offset_reset="earliest")
    for msg in consumer:
        frame = msg.value
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/video_feed', methods=['GET'])
def video_feed():
    topic = request.args.get('topic')
    frame = get_frames(topic)
    return Response(frame, mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")