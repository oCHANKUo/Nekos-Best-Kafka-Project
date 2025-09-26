# consumer_console.py
import json
from kafka import KafkaConsumer
from collections import Counter # for counting images per category

KAFKA_BOOTSTRAP = "localhost:9092"
KAFKA_TOPIC = "nekos-images"

consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP,
    group_id="nekos-consumer-group",
    value_deserializer=lambda x: json.loads(x.decode('utf-8')), # JSON serialization
)

counter = Counter()

print("Listening for events...\n")

for msg in consumer:
    event = msg.value
    cat = event["category"]
    url = event["payload"]["url"]
    artist = event["payload"].get("artist_name", "Unknown")
    counter[cat] += 1
    print(counter)
    print(f"[{cat}] {url} (artist: {artist})")