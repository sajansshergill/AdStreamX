import os, json, time, uuid, random
from datetime import datetime, timezone
from faker import Faker
from dotenv import load_dotenv
from confluent_kafka import Producer
from ingestion.schemas import AdEvent

load_dotenv()

fake = Faker()

DEVICES = ["mobile", "desktop", "console", "tablet"]
GEOs = ["US-NY", "US-CA", "US-TX", "US-FL", "CA-ON", "IN-DL", "GB-LND"]

def make_event() -> dict:
    # simple behavior model:
    # every impression -> occassional click -> rare conversion
    ad_id = random.randint(1, 5000)
    user_id = f"u_{random.randint(1, 2_000_000)}"
    device = random.choice(DEVICES)
    geo = random.choice(GEOs)
    
    r = random.random()
    if r < 0.80:
        et = "impression"
        revenue = 0.0
    elif r < 0.97:
        et = "click"
        revenue = 0.0
    else:
        et = "conversion"
        revenue = round(random.uniform(0.2, 25.0), 2)
        
    evt = AdEvent(
        event_id = str(uuid.uuid4()),
        ts=datetime.now(timezone.utc),
        user_id=user_id,
        ad_id=ad_id,
        device=device,
        geo=geo,
        event_type=et,
        revenue=revenue,
    )
    return evt.model_dump(mode="json")

def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")
    # else: keep quiet for throughput
    
def main():
    bootstrap = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
    topic = os.getenv("KAFKA_TOPIC", "adx_events")
    
    producer = Producer({"bootstrap.servers": bootstrap})
    
    rate_per_sec = int(os.getenv("GEN_RATE_PER_SEC", "500")) # tune for your machine
    print(f"Producing to topic={topic} @ ~{rate_per_sec}/sec, bootstrap={bootstrap}")
    
    try:
        while True:
            t0 = time.time()
            for _ in range(rate_per_sec):
                payload = make_event()
                producer.produce(topic, json.dumps(payload).encode("utf-8"), callback=delivery_report)
            producer.poll(0)
            # pace to ~1s
            elapsed = time.time() - t0
            if elapsed < 1.0:
                time.sleep(1.0 - elapsed)
    except KeyboardInterrupt:
        pass
    finally:
        producer.flush(10)
        
        
if __name__ == "__main__":
    main()