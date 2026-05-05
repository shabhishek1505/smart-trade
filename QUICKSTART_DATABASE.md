# Quick Start: Local SQL Database Setup

Get up and running with Smart-Trade using PostgreSQL in 10 minutes.

## Prerequisites

- Python 3.11+
- PostgreSQL 13+ 
- Node.js 18+
- Git

## Installation

### 1️⃣ PostgreSQL Setup (5 minutes)

**Windows:**
1. Download installer: https://www.postgresql.org/download/windows/
2. Run installer, set password for `postgres` user
3. Add PostgreSQL to PATH

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### 2️⃣ Create Database (2 minutes)

```bash
# Connect as postgres user
psql -U postgres

# Run these commands
CREATE DATABASE smart_trade_db;
CREATE USER smart_trade WITH PASSWORD 'smart_trade_password';
ALTER ROLE smart_trade SET client_encoding TO 'utf8';
GRANT ALL PRIVILEGES ON DATABASE smart_trade_db TO smart_trade;
\c smart_trade_db
GRANT ALL ON SCHEMA public TO smart_trade;
\q
```

**Verify connection:**
```bash
psql -U smart_trade -d smart_trade_db -h localhost -c "SELECT 1"
# Should output: 1
```

### 3️⃣ Clone & Setup Project (3 minutes)

```bash
git clone https://github.com/yourusername/smart-trade.git
cd smart-trade

# Create backend environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create frontend environment
cd frontend
npm install
cd ..
```

### 4️⃣ Configure Environment

Create `.env` in project root:
```
DATABASE_URL=postgresql://smart_trade:smart_trade_password@localhost:5432/smart_trade_db
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
FRONTEND_URL=http://localhost:3000
```

Create `frontend/.env`:
```
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_WS_URL=ws://localhost:8000/api/ws
REACT_APP_ENVIRONMENT=development
```

### 5️⃣ Initialize Database Tables

```bash
# Activate venv if needed
source venv/bin/activate

python << 'EOF'
from common.db.base import Base
from common.db.models.user import User
from common.db.models.trade_history import TradeHistory
from common.db.models.position import Position
from common.db.models.strategy import StrategyMaster, StrategyPlan
from common.db.models.strategy_signal import StrategySignal
from common.db.database import engine

# Create all tables
Base.metadata.create_all(bind=engine)
print("✅ Database tables created successfully!")

# Seed default strategies
from common.db.database import SessionLocal
db = SessionLocal()

strategies = [
    StrategyMaster(
        strategy_name="sma_rsi_macd",
        description="Combination of SMA, RSI, and MACD indicators",
        default_cron="*/5 * * * *",
        default_params={"fast_sma": 10, "slow_sma": 20, "rsi_period": 14}
    ),
    StrategyMaster(
        strategy_name="moving_avg_crossover",
        description="Golden/Death cross strategy using moving averages",
        default_cron="*/5 * * * *",
        default_params={"short_period": 50, "long_period": 200}
    ),
    StrategyMaster(
        strategy_name="rsi_macd",
        description="RSI and MACD divergence strategy",
        default_cron="*/5 * * * *",
        default_params={"rsi_period": 14, "macd_fast": 12, "macd_slow": 26}
    ),
]

for strategy in strategies:
    existing = db.query(StrategyMaster).filter_by(strategy_name=strategy.strategy_name).first()
    if not existing:
        db.add(strategy)

db.commit()
db.close()
print("✅ Default strategies seeded!")
EOF
```

## Run the Application

### Terminal 1: Backend API

```bash
source venv/bin/activate
uvicorn worker.api.main:app --reload --port 8000
```

Server runs on: **http://localhost:8000**  
API Docs on: **http://localhost:8000/docs**

### Terminal 2: Frontend React

```bash
cd frontend
npm start
```

App runs on: **http://localhost:3000**

## Create Test User & Data

### Option 1: Via API (Using Swagger UI)

1. Go to http://localhost:8000/docs
2. Find `POST /api/auth/register`
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
5. Click "Execute"
6. Copy the `access_token` from response

### Option 2: Via Python Script

```bash
python << 'EOF'
from common.db.database import SessionLocal
from common.db.models.user import User
from common.db.models.strategy import StrategyPlan
from worker.api.auth import hash_password
import uuid

db = SessionLocal()

# Create user
user = User(
    username="trader1",
    email="trader@example.com",
    password_hash=hash_password("testpass123"),
    full_name="John Trader"
)
db.add(user)
db.commit()
user_id = user.id

# Assign strategies to user
strategies = [1, 2, 3]  # IDs from StrategyMaster
for strategy_id in strategies:
    for symbol in ["INFY", "TCS", "RELIANCE"]:
        plan = StrategyPlan(
            user_id=user_id,
            strategy_id=strategy_id,
            stock_symbol=symbol,
            enabled=False,  # Disabled by default
        )
        db.add(plan)

db.commit()
db.close()

print(f"✅ Created user: trader1 (ID: {user_id})")
print("✅ Assigned strategies to user")
EOF
```

### Add Sample Trades

```bash
python << 'EOF'
from datetime import datetime, timedelta
from common.db.database import SessionLocal
from common.db.models.trade_history import TradeHistory

db = SessionLocal()
user_id = 1

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
        strategy="moving_avg_crossover",
        entry_time=datetime.utcnow() - timedelta(days=3),
        exit_time=datetime.utcnow() - timedelta(days=2),
    ),
    TradeHistory(
        user_id=user_id,
        stock_symbol="RELIANCE",
        action="BUY",
        entry_price=2800.00,
        exit_price=2850.50,
        quantity=20,
        pnl=1010.00,
        status="CLOSED",
        strategy="rsi_macd",
        entry_time=datetime.utcnow() - timedelta(days=1),
        exit_time=datetime.utcnow(),
    ),
]

for trade in trades:
    db.add(trade)

db.commit()
db.close()

print(f"✅ Added {len(trades)} sample trades for user {user_id}")
EOF
```

## Test the APIs

### Login & Get Token

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"trader1","password":"testpass123"}'
```

Response:
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

### Get Trades (Replace TOKEN with actual token)

```bash
curl -X GET "http://localhost:8000/api/trades" \
  -H "Authorization: Bearer TOKEN"
```

### Get Analytics

```bash
curl -X GET "http://localhost:8000/api/analytics/performance" \
  -H "Authorization: Bearer TOKEN"
```

## Verify Data in PostgreSQL

```bash
psql -U smart_trade -d smart_trade_db

-- Check users
SELECT id, username, email FROM users;

-- Check trades
SELECT id, stock_symbol, action, pnl, status FROM trade_history;

-- Check P&L summary
SELECT SUM(pnl) as total_pnl, COUNT(*) as total_trades FROM trade_history WHERE status = 'CLOSED';

-- Check positions
SELECT symbol, quantity, current_price, current_value FROM positions;
```

## Troubleshooting

### Can't Connect to Database

```bash
# Verify PostgreSQL is running
psql -U postgres -c "SELECT 1"

# Check connection string in .env
DATABASE_URL=postgresql://smart_trade:smart_trade_password@localhost:5432/smart_trade_db

# Test connection
psql -U smart_trade -d smart_trade_db -h localhost
```

### Tables Don't Exist

```bash
# Drop and recreate (careful with production data!)
psql -U smart_trade -d smart_trade_db << 'EOF'
DROP TABLE IF EXISTS trade_history CASCADE;
DROP TABLE IF EXISTS positions CASCADE;
DROP TABLE IF EXISTS strategy_signals CASCADE;
DROP TABLE IF EXISTS strategy_plan CASCADE;
DROP TABLE IF EXISTS strategy_master CASCADE;
DROP TABLE IF EXISTS users CASCADE;
EOF

# Re-run the table creation script
```

### Port Already in Use

```bash
# Use different port for backend
uvicorn worker.api.main:app --reload --port 8001

# Update frontend .env
REACT_APP_API_URL=http://localhost:8001/api
```

## Next Steps

1. ✅ Database is running
2. ✅ Tables are created
3. ✅ Sample data is added
4. ✅ Frontend and backend are running
5. 🔄 **Login** on http://localhost:3000
6. 🔄 **View Dashboard** - See portfolio summary from database
7. 🔄 **View Trades** - See trades you just created
8. 🔄 **Check Analytics** - See performance calculations from database

## Database Maintenance

### Backup Database

```bash
pg_dump -U smart_trade -d smart_trade_db > backup_$(date +%Y%m%d).sql
```

### Restore Database

```bash
psql -U smart_trade -d smart_trade_db < backup_20260410.sql
```

### View Database Size

```bash
psql -U smart_trade -d smart_trade_db -c "SELECT pg_size_pretty(pg_database_size('smart_trade_db'));"
```

## Performance Monitoring

### Check Active Queries

```bash
psql -U smart_trade -d smart_trade_db << 'EOF'
SELECT pid, usename, application_name, state, query 
FROM pg_stat_activity 
WHERE state != 'idle';
EOF
```

### Analyze Query Performance

```bash
psql -U smart_trade -d smart_trade_db << 'EOF'
EXPLAIN ANALYZE 
SELECT * FROM trade_history 
WHERE user_id = 1 AND status = 'CLOSED';
EOF
```

## API Documentation

Once running, view interactive API docs at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

All endpoints are documented with request/response examples.

## Success! 🎉

You now have:
- ✅ PostgreSQL database running locally
- ✅ FastAPI backend with real database queries
- ✅ React frontend connected to database
- ✅ Sample data and test user
- ✅ All APIs fully functional

Start building your trading application!
