import os
import joblib
import numpy as np
import pandas as pd
import psycopg2
from dotenv import load_dotenv
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

load_dotenv()

def read_pg():
    conn = psycopg2.connect(
        host=os.getenv("PG_HOST", "localhost"),
        port=int(os.getenv("PG_PORT", 5432)),
        dbname=os.getenv("PG_DB", "adx"),
        user=os.getenv("PG_USER", "adx"),
        password=os.getenv("PG_PASSWORD", "adx"),
    )
    try:
        q = """
        SELECT ad_id, impressions, clicks, ctr
        FROM ad_minute_metrics
        WHERE impressions >= 10;
        """
        df = pd.read_sql(q, conn)
        return df
    finally:
        conn.close()
        
def main():
    df = read_pg()
    if df.empty:
        raise SystemExit("No training data yet. Run streaming for a few minutes first.")

    # Build a toy supervised dataset:
    # predict whether ctr is "high" (>= median) using impressions/clicks
    y = (df["ctr"] >= df["ctr"].median()).astype(int)
    X = df[["impressions", "clicks", "ctr"]].astype(float)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = LogisticRegression(max_iter=200)
    model.fit(X_train, y_train)
    
    proba = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, proba)
    print(f"AUC: {auc:.4f} (toy objective)")
    
    out = os.getenv("MODEL_PATH", "ranking_service/model.joblib")
    joblib.dump(model, out)
    print(f"Saved model -> {out}")
    
if __name__ == "__main__":
    main()