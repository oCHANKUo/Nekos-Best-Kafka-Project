# consumer_console.py
import json
from kafka import KafkaConsumer

KAFKA_BOOTSTRAP = "localhost:9092"
KAFKA_TOPIC = "nekos-images"

consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP,
    group_id="nekos-consumer-group",
    value_deserializer=lambda x: json.loads(x.decode('utf-8')), # JSON serialization
)

print("Listening for events...\n")

for msg in consumer:
    event = msg.value
    cat = event["category"]
    url = event["payload"]["url"]
    artist = event["payload"].get("artist_name", "Unknown")
    print(f"[{cat}] {url} (artist: {artist})")