# producer_nekos.py

import time
import requests
from kafka import KafkaProducer
import json

KAFKA_BOOTSTRAP = "localhost:9092"
KAFKA_TOPIC = "nekos-images"
BASE_URL = "https://nekos.best/api/v2"

CATEGORIES = ["neko", "waifu", "kitsune", "hug", "pat"]

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def fetch_images(category, amount=1):
    url = f"{BASE_URL}/{category}"
    params = {"amount": amount}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json().get("results", [])
    except requests.RequestException as e:
        print(f"Error fetching images for category {category}: {e}")
        return []
    
def main():
    while True:
        for cat in CATEGORIES:
            results = fetch_images(cat, amount=1)
            for item in results:
                event = {
                    "category": cat,
                    "timestamp": int(time.time()),
                    "payload": item
                }
                producer.send(KAFKA_TOPIC, event)
                print(f"Sent {cat}: {item.get('url')}")
            producer.flush()
            time.sleep(10) # fetch every 10 seconds

if __name__ == "__main__":
    main()