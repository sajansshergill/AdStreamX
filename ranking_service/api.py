import os
import random
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from feature_store.online_store import get_ad_features

load_dotenv()

app = FastAPI(title="AdStreamX Ranking Service")

MODEL_PATH = os.getenv("MODEL_PATH", "ranking_service/model.joblib")
_model = None

class RankRequest(BaseModel):
    user_id: str
    geo: str = "US-NY"
    device: str = "mobile"
    candidate_ad_ids: list[int] | None = None
    k: int = 10
    
def load_model():
    global _model
    if _model is None:
        if not os.path.isfile(MODEL_PATH):
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Run train_model.py first.")
        _model = joblib.load(MODEL_PATH)
    return _model

def retrieve_candidates(req: RankRequest) -> list[int]:
    # Simple candidate retrieval (placeholder):
    # In a real system: targeting, budgets, pacing, policy, frequency caps, etc.
    if req.candidate_ad_ids:
        return req.candidate_ad_ids
    return random.sample(range(1,5001), k=min(200, 5000)) # 200 candidates

@app.get("/health")
def health():
    return {"ok":True}

@app.post("/rank_ads")
def rank_ads(req: RankRequest):
    try:
        model = load_model()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    candidates = retrieve_candidates(req)
    
    scored = []
    for ad_id in candidates:
        feats = get_ad_features(ad_id)
        X = [[feats["impressions_5m"], feats["clicks_5m"], feats["ctr_5m"]]]
        score = float(model.predict_proba(X)[0, 1])
        scored.append({"ad_id": ad_id, "score": score, "features": feats})
    
    scored.sort(key=lambda x: x["score"], reverse=True)
    topk = scored[: max(1, req.k)]
    
    return {
        "user_id": req.user_id,
        "k": req.k,
        "ranked_ads": topk,
    }