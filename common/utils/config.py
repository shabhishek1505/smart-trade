import os

# Database Configuration
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:admin@localhost:5432/smart-trade")

# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
PLAN_PROCESSING_KAFKA_TOPIC = os.getenv("PLAN_PROCESSING_KAFKA_TOPIC", "plan-processing-requests")
SIGNAL_PROCESSING_KAFKA_TOPIC = os.getenv("SIGNAL_PROCESSING_KAFKA_TOPIC", "signal-processing-requests")
REFRESH_INTERVAL = int(os.getenv("SCHEDULE_REFRESH_SECONDS", 300))
WORKER_GROUP = os.getenv("WORKER_GROUP", "strategy-worker")

# Encryption Configuration
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", None)  # Must be set for production

# Broker Configuration
BROKER_DEFAULT = os.getenv("BROKER_DEFAULT", "angel_one")
PRICE_FETCH_INTERVAL_MINUTES = int(os.getenv("PRICE_FETCH_INTERVAL_MINUTES", 5))
PRICE_HISTORY_DAYS = int(os.getenv("PRICE_HISTORY_DAYS", 30))

# Trading Configuration
SYMBOLS_TO_TRADE = os.getenv("SYMBOLS_TO_TRADE", "INFY,TCS,RELIANCE,HDFC,ICICIBANK,WIPRO,LT,MARUTI,BAJAJFINSV,HCLTECH").split(",")
TRADE_CAPITAL_PERCENT = float(os.getenv("TRADE_CAPITAL_PERCENT", 5.0))  # % of capital per trade

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# API Configuration (for future REST API)
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
API_DEBUG = os.getenv("API_DEBUG", "False").lower() == "true"
