# app.py
import json
import threading
from collections import Counter
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from kafka import KafkaConsumer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

KAFKA_BOOTSTRAP = "localhost:9092"
KAFKA_TOPIC = "nekos-images"

# Global variables to store state
latest_images = {}  # Store latest image for each category
counter = Counter()

class KafkaThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP,
            group_id="nekos-web-consumer-group",
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            auto_offset_reset='latest'  # Only get new messages
        )

    def run(self):
        print("Starting Kafka consumer thread...")
        for msg in self.consumer:
            try:
                event = msg.value
                cat = event["category"]
                url = event["payload"]["url"]
                artist = event["payload"].get("artist_name", "Unknown")
                timestamp = event["timestamp"]
                
                # Update global state
                counter[cat] += 1
                latest_images[cat] = {
                    "url": url,
                    "artist": artist,
                    "timestamp": timestamp,
                    "count": counter[cat]
                }
                
                # Broadcast to all connected clients
                socketio.emit('new_image', {
                    "category": cat,
                    "url": url,
                    "artist": artist,
                    "timestamp": timestamp,
                    "count": counter[cat],
                    "counters": dict(counter)
                })
                
                print(f"Broadcasted [{cat}] {url} (artist: {artist})")
                
            except Exception as e:
                print(f"Error processing message: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    # Send current state to newly connected client
    emit('initial_data', {
        "latest_images": latest_images,
        "counters": dict(counter)
    })

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    # Start Kafka consumer thread
    kafka_thread = KafkaThread()
    kafka_thread.start()
    
    # Start Flask-SocketIO server
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)