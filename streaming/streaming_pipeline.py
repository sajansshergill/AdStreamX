import os
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, window, sum as Fsum, count as Fcount, when, to_timestamp

load_dotenv()

EVENT_SCHEMA = """
    event_id STRING,
    ts STRING,
    user_id STRING,
    ad_id LONG,
    device STRING,
    geo STRING,
    event_type STRING,
    revenue DOUBLE
"""

def main():
    kafka_bootstrap = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
    topic = os.getenv("KAFKA_TOPIC", "adx_events")
    
    spark = (
        SparkSession.builder
        .appName("adx_streaming_features")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    
    raw = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", kafka_bootstrap)
        .option("subscribe", topic)
        .option("startingOffsets", "latest")
        .load()
    )
    
    parsed = (
        raw.selectExpr("CAST(value AS STRING) AS json_str")
        .select(from_json(col("json_str"), EVENT_SCHEMA).alias("e"))
        .select("e.*")
        .withColumn("event_time", to_timestamp(col("ts")))
        .drop("ts")
    )
    
    # 5-minute timbling window aggregation per ad_id
    agg = (
        parsed
        .withinWatermark("event_time", "2 minutes")
        .groupBy(window(col("event_time"), "5 minutes"), col("ad_id"))
        .agg(
            Fcount(when(col("event_type") == "impression", True)).alias("impressions"),
            Fcount(when(col("event_type") == "click", True)).alias("clicks"),
            Fsum(when(col("event_type") == "conversion", col("revenue"))).alias("revenue"),
        )
        .withColumn("ctr", when(col("impressions") > 0, col("clicks") / col("impressions")).otherwise(0.0))
        
    )
    
    # write VIA foreachBatch to Redis & Postgres
    def foreach_batch(batch_df, batch_id: int):
        if batch_df.rdd.isEmpty():
            return

        # Collect only requried fields (small aggregation output)
        rows = (
            batch_df.select(
                col("window.start").alias("window_start"),
                col("window.end").alias("window_end"),
                col("ad_id"),
                col("impressions"),
                col("clicks"),
                col("ctr"),
            )
            .toPandas()
        )
        
        # Import here to Spark workers don't require these at parse time
        from streaming.sinks import upsert_minute_metrics_pg, write_online_features_redis
        
        pg_rows = []
        redis_rows = []
        for r in rows.itertuples(index=False):
            # Postgres upsert
            pg_rows.append((r.window_start.to_pydatetime(), r.window_end.to_pydatetime(), int(r.ad_id), int(r.impressions), int(r.clicks), float(r.ctr)))
            # Redis: store by window_end ISO
            redis_rows.append((r.window_end.isoformat(), int(r.ad_id), int(r.impressions), int(r.clicks), float(r.ctr)))

        upsert_minute_metrics_pg(pg_rows)
        write_online_features_redis(redis_rows)
        
        print(f"[batch={batch_id}] wrote {len(pg_rows)} rows to PG and Redis")
        
    query = (
        agg.writeStream
        .outputMode("update")
        .foreachBatch(foreach_batch)
        .option("checkpointLocation", "/tmp/adstreamx_chkpt")
        .start()
    )
    query.awaitTermination()
    
if __name__ == "__main__":
    main()