# Real-Time Data &amp; ML Infrastructure Platform

## 📌 Overview
AdStreamX is a production-grade, real-time advertising data infrastructure platform designed to simulate a large-scale ad personalization 
and ranking systems similar to those powering modern immersive platforms like Roblox.

This project demonstrates how to build:
- High-throughput streaming data pipelines
- Online + offline ML feature stores
- Scalable ad retrieval and ranking systems
- A/B experimentation frameworks
- Privacy-compliant, observable data systems

It is designed to reflect the responsibilities of a **Senior Data Engineer (Ads Infrastructure & ML Features)** role.

---

## Problem Statement

Modern advertising systems must:
- Process millions of real-time user interactions
- Compute low-latency ML features
- Support large-scale model training
- Enable rapid experimentation
- Maintain reliability, observability, and privacy compliance

AdStreamX simulates a full-stack ads infrastructure powering:
- Personalization
- Ranking
- Measurement
- Experimentation

## 🏗 High-Level Architecture

<img width="233" height="216" alt="image" src="https://github.com/user-attachments/assets/caca6712-3327-42f2-acf2-c3eba87d054b" />

<img width="1024" height="576" alt="image" src="https://github.com/user-attachments/assets/0972a2b2-06b5-4d9f-becb-4bf214aff8c6" />

<img width="1400" height="689" alt="image" src="https://github.com/user-attachments/assets/e590d78a-6516-4623-9d4d-29986c7cde84" />

<img width="1600" height="1117" alt="image" src="https://github.com/user-attachments/assets/b80e70ef-3e13-416f-bd8f-f173eb0771fb" />

                   ┌──────────────────────┐
                   │  Event Generator     │
                   └─────────┬────────────┘
                             │
                        (Kafka)
                             │
        ┌────────────────────┴────────────────────┐
        │                                         │
  Streaming Pipeline                        Batch Pipeline
 (Spark Structured)                        (Spark Jobs)
        │                                         │
  Online Feature Store                     Offline Feature Store
     (Redis)                                 (Parquet/SQL)
        │                                         │
        └──────────────┬──────────────────────────┘
                       │
                Ranking Service (FastAPI)
                       │
                Ad Serving Simulation
                       │
                A/B Experimentation


---

## Core Capabilities

1️⃣ High Throughput Event Integestion
Simuates 10M+ events including:
- user_id
- ad_id
- impression
- click
- conversion
- revenue
- device
- geo
- timestamp

Technology:
- Kafka
- Python producer

2️⃣ Real-Time Streaming Feature Computation
Built using:
- Spark Structured Streaming
- Kafka

Real-time features:
- 5-min CTR
- User engagement rate
- Ad popularity
- Recency features
- Frequency capping
- Device/geo signals

Outputs:
- Redis (Online Feature Store)
- PostgreSQL / Druid (Analytics)

3️⃣ Batch ML Feature Pipeline
Daily Spark jobs compute:
- 7-day CTR
- Conversion rate
- User lifetime value
- Time-of-day engagement
- Campaign performance mertics

Output:
- Offline training dataset (Parquet)

4️⃣ Hybrid Feature Store (Online + Offline)
| Layer   | Tech               | Purpose               |
| ------- | ------------------ | --------------------- |
| Online  | Redis              | Low-latency inference |
| Offline | Parquet / Postgres | Training & analytics  |

Feature APIs:
GET /features/user/{id}
GET /features/ad/{id}

5️⃣ Ad Retrieval & Ranking Service
Retrieval Layer
- Geo targeting
- Device targeting
- Campaign eligibility
- Frequency caps

Ranking Layer
- Logistic Regression / XGBoost
- Predict CTR / Conversion Probability
- Score & sort ads

API:
POST /rank_ads

6️⃣ A/B Experimentation Framework
- Traffic split (50/50)
- Model A vs Model B
- Online metric logging
- CTR uplift
- Revenue lift
- Statistical significance testing

Outputs:
- Experiment dashboard
- Performance comparison report

7️⃣ Observability & Reliability
- Prometheus metrics:
  - Event lag
  - Feature freshness
  - API latency
- Data quality validation
- Idempotent streaming writes
- Retry logic
- Structure logging

8️⃣ Privacy & Compliance
- User ID hashing
- PII masking
- Consent filtering
- Data retention enforcement
- GDPR-style data deletion simulation

## Tech Stack
| Category         | Tools                  |
| ---------------- | ---------------------- |
| Language         | Python                 |
| Streaming        | Kafka                  |
| Processing       | Spark                  |
| Online Store     | Redis                  |
| Offline Store    | Parquet / PostgreSQL   |
| ML               | Scikit-learn / XGBoost |
| Serving          | FastAPI                |
| Orchestration    | Airflow                |
| Monitoring       | Prometheus             |
| Containerization | Docker                 |

## 📂 Project Structure

<img width="215" height="595" alt="image" src="https://github.com/user-attachments/assets/d3ac5dc7-a71a-4c93-a4e8-1e037e1377e0" />

## ⚡ Getting Started
1️⃣ Clone Repo
git clone https://github.com/yourusername/adstreamx.git
cd adstreamx

2️⃣ Start infrastructure
docker-compose up -d

Starts:
- Kafka
- Zookeeper
- Redis
- Postgres
- Prometheus

3️⃣ Run Event Generator
python ingestion/event_generator.py

4️⃣ Start Streaming Job
python streaming/streaming_pipeline.py

5️⃣ Train Ranking Model
python ranking_service/model.py

6️⃣ Launch API
uvicorn ranking_service.api:app --reload

## 📊 Example Ranking Response
{
  "user_id": "hashed_123",
  "ranked_ads": [
    {"ad_id": 87, "score": 0.92},
    {"ad_id": 41, "score": 0.84},
    {"ad_id": 13, "score": 0.76}
  ]
}

## 📈 Scalability Design Considerations
- Partitioned Kafka topics
- Distributed Spark executors
- Redis sharding simulation
- Horizontal API scaling
- Stateless service design

## 🧠 Design Principles
- Treat data as a product
- Feature reusability & discoverability
- Low-latency inference
- ML-friendly interfaces
- Observability-first mindset
- Clean modular architecture

## 🎯 Why This Project Matters
The project demonstrates:
- Production-grade data engineering
- ML infrastructure enablement
- Real-time systems design
- Ads persoanlization systems
- Cross-functional ML colaboration
- Platform thinking at scale

It mirrors the architecture behind large-scale advertising ecosystems and immersive digital platforms.

## 🚀 Future Enhancements
- Replace Spark with Flink
- Add Ray for distributed pipeline
- Implement Kubeflow pipeline
- Deploy to Kubernetes
- Add feature lineage tracking
- Build internal feature catalog UI


