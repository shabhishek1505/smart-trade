# Local Development Guide

Run Smart-Trade services independently on your machine for faster development and testing.

## Prerequisites

- Python 3.10+ (for backend services)
- Node.js 18+ (for frontend)
- PostgreSQL 13+ (local database)
- Kafka 3.0+ (local message broker)
- Git

## Setup

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/smart-trade.git
cd smart-trade
```

### 2. Setup Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Setup Database

See `QUICKSTART_DATABASE.md` for PostgreSQL setup.

Quick version:
```bash
psql -U postgres

CREATE DATABASE smart_trade_db;
CREATE USER smart_trade WITH PASSWORD 'smart_trade_password';
ALTER ROLE smart_trade SET client_encoding TO 'utf8';
GRANT ALL PRIVILEGES ON DATABASE smart_trade_db TO smart_trade;

\c smart_trade_db
GRANT ALL ON SCHEMA public TO smart_trade;
\q
```

### 4. Create Tables

```bash
python << 'EOF'
from common.db.base import Base
from common.db.models.user import User
from common.db.models.trade_history import TradeHistory
from common.db.models.position import Position
from common.db.models.strategy import StrategyMaster, StrategyPlan
from common.db.models.strategy_signal import StrategySignal
from common.db.database import engine

Base.metadata.create_all(bind=engine)
print("✅ Tables created!")
EOF
```

### 5. Configure Environment

Create `.env` file in project root:

```
DATABASE_URL=postgresql://smart_trade:smart_trade_password@localhost:5432/smart_trade_db
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
FRONTEND_URL=http://localhost:3000
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
BROKER_API_KEY=dev_key
BROKER_API_SECRET=dev_secret
```

### 6. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cat > .env << 'EOF'
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_WS_URL=ws://localhost:8000/api/ws
REACT_APP_ENVIRONMENT=development
EOF
```

## Running Services

### Terminal 1: PostgreSQL (if not running as service)

```bash
# macOS with Homebrew
brew services start postgresql@15

# Or manually:
postgres -D /usr/local/var/postgres

# Verify
psql -U smart_trade -d smart_trade_db -c "SELECT 1"
```

### Terminal 2: Kafka (optional for local dev)

If you want to test Kafka message flow locally:

```bash
# Install Kafka locally or use Docker
docker run -d \
  --name kafka-local \
  -p 9092:9092 \
  -e KAFKA_BROKER_ID=1 \
  -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 \
  -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 \
  -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
  confluentinc/cp-kafka:7.5.0

# Or skip and use Docker Compose for Kafka + Zookeeper
docker-compose up -d kafka zookeeper
```

### Terminal 3: FastAPI Backend

```bash
# Make sure venv is activated
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start API service
python api_server.py

# Or directly:
uvicorn api.main:app --reload --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started server process [12345]
```

**Check**: Visit `http://localhost:8000/docs` - should see Swagger UI

### Terminal 4: Worker Service (optional)

```bash
# Make sure venv is activated
source venv/bin/activate

# Start worker service
python worker_service.py
```

Expected output:
```
Starting Smart-Trade Worker Service
Worker service ready for consuming Kafka messages
```

### Terminal 5: React Frontend

```bash
# From project root, navigate to frontend
cd frontend

# Start development server
npm start
```

Expected output:
```
Compiled successfully!

You can now view smart-trade in the browser.

Local:            http://localhost:3000
```

**Check**: Visit `http://localhost:3000` - should see login page

## Usage

### 1. Create Test User

Option A: Via API Swagger UI
1. Go to `http://localhost:8000/docs`
2. Find `POST /auth/register`
3. Click "Try it out"
4. Enter:
```json
{
  "username": "trader1",
  "email": "trader@example.com",
  "password": "testpass123",
  "full_name": "John Trader"
}
```
5. Execute and copy `access_token`

Option B: Via Python Script
```bash
python << 'EOF'
from common.db.database import SessionLocal
from common.db.models.user import User
from worker.api.auth import hash_password

db = SessionLocal()
user = User(
    username="trader1",
    email="trader@example.com",
    password_hash=hash_password("testpass123"),
    full_name="John Trader"
)
db.add(user)
db.commit()
print(f"✅ Created user: trader1")
db.close()
EOF
```

### 2. Login via Frontend

1. Go to `http://localhost:3000`
2. Enter credentials:
   - Username: `trader1`
   - Password: `testpass123`
3. Click Login

### 3. Create Test Data

```bash
python << 'EOF'
from datetime import datetime, timedelta
from common.db.database import SessionLocal
from common.db.models.trade_history import TradeHistory
from common.db.models.strategy import StrategyPlan, StrategyMaster
from common.db.models.position import Position

db = SessionLocal()
user_id = 1  # Or your actual user_id

# Create strategy master if not exists
strategy = db.query(StrategyMaster).filter_by(strategy_name="sma_rsi_macd").first()
if not strategy:
    strategy = StrategyMaster(
        strategy_name="sma_rsi_macd",
        description="Test strategy",
        default_cron="*/5 * * * *"
    )
    db.add(strategy)
    db.commit()

# Create strategy plan for user
plan = db.query(StrategyPlan).filter_by(
    user_id=user_id,
    strategy_id=strategy.strategy_id,
    stock_symbol="INFY"
).first()
if not plan:
    plan = StrategyPlan(
        user_id=user_id,
        strategy_id=strategy.strategy_id,
        stock_symbol="INFY",
        enabled=True
    )
    db.add(plan)
    db.commit()

# Create sample trades
trades = [
    TradeHistory(
        user_id=user_id,
        stock_symbol="INFY",
        action="BUY",
        entry_price=1850.50,
        exit_price=1890.25,
        quantity=10,
        pnl=3975.00,
        status="CLOSED",
        strategy="sma_rsi_macd",
        entry_time=datetime.utcnow() - timedelta(days=5),
        exit_time=datetime.utcnow() - timedelta(days=4),
    ),
    TradeHistory(
        user_id=user_id,
        stock_symbol="TCS",
        action="SELL",
        entry_price=4250.00,
        exit_price=4200.00,
        quantity=5,
        pnl=-250.00,
        status="CLOSED",
        strategy="sma_rsi_macd",
        entry_time=datetime.utcnow() - timedelta(days=2),
        exit_time=datetime.utcnow(),
    ),
]

for trade in trades:
    db.add(trade)

# Create sample position
position = Position(
    user_id=user_id,
    symbol="RELIANCE",
    quantity=20,
    average_price=2800.00,
    current_price=2850.50,
    invested_value=56000.00,
    current_value=57010.00,
    strategy="sma_rsi_macd",
)
db.add(position)
db.commit()

print(f"✅ Created {len(trades)} trades and 1 position for user {user_id}")
db.close()
EOF
```

### 4. View in Dashboard

Go to `http://localhost:3000/dashboard` - should see:
- Portfolio summary
- Recent trades
- Open positions
- Performance metrics

## Hot Reload

### Frontend (Automatic)
React dev server automatically reloads on file changes.

### Backend (Automatic)
FastAPI with `--reload` flag automatically reloads on file changes.

### Database
Schema changes require manual table updates or migrations.

## Testing APIs

### Test Authentication

```bash
# Register
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "email": "test@example.com",
    "password": "testpass123",
    "full_name": "Test User"
  }'

# Login and get token
RESPONSE=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "password": "testpass123"
  }')

TOKEN=$(echo $RESPONSE | jq -r '.data.access_token')
echo "Token: $TOKEN"
```

### Test API Endpoints

```bash
# Get trades (replace TOKEN with actual token)
curl -X GET "http://localhost:8000/api/trades" \
  -H "Authorization: Bearer $TOKEN"

# Get analytics
curl -X GET "http://localhost:8000/api/analytics/performance" \
  -H "Authorization: Bearer $TOKEN"

# Get positions
curl -X GET "http://localhost:8000/api/positions" \
  -H "Authorization: Bearer $TOKEN"
```

### Test WebSocket

```bash
# Using websocat (install: cargo install websocat)
websocat ws://localhost:8000/api/ws
```

Then in the WebSocket connection, type messages:
```
{"type": "test", "message": "hello"}
```

## Debugging

### Backend Logs

Check terminal where API is running for logs:
```
INFO:     127.0.0.1:59234 - "POST /api/auth/login HTTP/1.1" 200 OK
```

### Database Queries

Connect and query manually:
```bash
psql -U smart_trade -d smart_trade_db

SELECT * FROM users;
SELECT * FROM trade_history WHERE user_id = 1;
SELECT SUM(pnl) FROM trade_history WHERE user_id = 1;
```

### Frontend Console

Open browser DevTools (F12) and check Console tab for JavaScript errors.

### Network Requests

In browser DevTools, go to Network tab to see all API requests.

## Stopping Services

### Stop in Reverse Order
```bash
# Terminal 5: Ctrl+C
# Terminal 4: Ctrl+C  
# Terminal 3: Ctrl+C
# Terminal 2: (stop Kafka if running separately)
# Terminal 1: (stop PostgreSQL)
```

### Or Kill All

```bash
pkill -f "python api_server.py"
pkill -f "python worker_service.py"
pkill -f "npm start"
```

## Troubleshooting

### Port Already in Use

```bash
# Find and kill process using port 8000
lsof -i :8000
kill -9 <PID>

# Or use different port
uvicorn api.main:app --port 8001
```

### Database Connection Error

```bash
# Verify PostgreSQL is running
psql -U postgres -c "SELECT 1"

# Check connection string
psql -U smart_trade -d smart_trade_db -h localhost
```

### Kafka Connection Error

If not using Kafka locally, comment out Kafka code in `worker_service.py` and API routes.

### Module Not Found

Make sure venv is activated:
```bash
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows
```

## Tips for Development

1. **Use VS Code** with Python and REST Client extensions
2. **Set up debugger** in VS Code with FastAPI
3. **Use SQLAlchemy logging** to see SQL queries:
   ```python
   import logging
   logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
   ```
4. **Use pytest** for testing:
   ```bash
   pytest tests/ -v
   ```
5. **Format code** with black:
   ```bash
   black api/ worker/ common/
   ```

## Next Steps

- Read `ARCHITECTURE.md` for system design
- Read `DATABASE_SETUP.md` for database details
- Check `API.md` for endpoint documentation
- Review test files in `tests/` directory
