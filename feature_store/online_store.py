import os
import redis
from dotenv import load_dotenv

load_dotenv()

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True,
)

def get_ad_features(ad_id: int) -> dict:
    key = f"ad:{ad_id}"
    data = r.hgetall(key)
    if not data:
        return {"ad_id": ad_id, "ctr_5m": 0.0, "impressions_5m": 0, "clicks_5m": 0, "feature_ts": None}
    return {
        "ad_id": ad_id,
        "ctr_5m": float(data.get("ctr_5m", 0.0)),
        "impressions_5m": int(data.get("impressions_5m", 0)),
        "clicks_5m": int(data.get("clicks_5m", 0)),
        "feature_ts": data.get("feature_ts", None),
    }