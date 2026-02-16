import os
import redis
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

def get_redis():
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        decode_responses=True,
    )
    
def get_pg():
    return psycopg2.connect(
        host=os.getenv("PG_HOST", "localhost"),
        port=int(os.getenv("PG_PORT", 5432)),
        dbname=os.getenv("PG_DB", "adx"),
        user=os.getenv("PG_USER", "adx"),
        password=os.getenv("PG_PASSWORD", "adx"),
    )
    
def upsert_minute_metrics_pg(rows):
    """
    rows: list of tuples (window_start, window_end, ad_id, impressions, clicks, ctr)
    """
    if not rows:
        return
    conn = get_pg()
    try:
        with conn, conn.cursor() as cur:
            sql = """
            INSERT INTO ad_minute_metrics(window_start, window_end, ad_id, impressions, clicks, ctr)
            VALUES %s
            ON CONFLICT (window_start, window_end, ad_id)
            DO UPDATE SET impressions=EXCLUDED.impressions,
            clicks=EXCLUDED.clicks,
            ctr=EXCLUDED.ctr,
            updated_at=NOW();
            """
            execute_values(cur, sql, rows)
    finally:
        conn.close()
        
def write_online_features_redis(rows):
    """
    Store online features keyed by ad_id, eg:
    key: ad:{ad_id}
    fields: ctr_5m, impressions_5m, clicks_5m, feature_ts
    """
    if not rows:
        return
    r = get_redis()
    pipe = r.pipeline(transaction=False)
    for (window_end_iso, ad_id, impressions, clicks, ctr) in rows:
        key = f"ad:{ad_id}"
        pipe.hset(
            key,
            mapping={
                "ctr_5m": str(ctr),
                "impressions_5m": str(impressions),
                "clicks_5m": str(clicks),
                "feature_ts": window_end_iso,
            },
        )
        pipe.expire(key, 60 * 30) # 30min TTL
    pipe.execute()