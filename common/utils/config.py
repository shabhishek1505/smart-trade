import os

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:admin@localhost:5432/smart-trade")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
PLAN_PROCESSING_KAFKA_TOPIC = os.getenv("PLAN_PROCESSING_KAFKA_TOPIC", "plan-processing-requests")
REFRESH_INTERVAL = int(os.getenv("SCHEDULE_REFRESH_SECONDS", 300))
