CREATE TABLE IF NOT EXISTS ad_minute_metrics (
    window_start TIMESTAMP NOT NULL,
    window_end TIMESTAMP NOT NULL,
    ad_id BIGINT NOT NULL,
    impressions BIGINT NOT NULL,
    clicks BIGINT NOT NULL,
    ctr DOUBLE PRECISION NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    PRIMARY KEY (window_start, window_end, ad_id)
);