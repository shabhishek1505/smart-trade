# Database Setup Guide

This guide explains how to set up and use the Smart-Trade database with actual SQL queries.

## Database Schema

The application uses PostgreSQL with the following main tables:

### User Management
- **users** - User accounts with authentication
- **user_settings** - User preferences and configuration

### Trading Data
- **strategy_master** - Trading strategy definitions (templates)
- **strategy_plan** - Per-user per-symbol strategy instances
- **strategy_signals** - Generated trading signals
- **trade_history** - Executed trades with P&L
- **positions** - Current open positions

### Supporting Tables
- **broker_credentials** - Encrypted broker API keys
- **price_data** - Historical price data
- **broker_order** - Order history
- **strategy_performance** - Performance metrics

## Key Relationships

```
User (1) ──→ (Many) StrategyPlan
          ──→ (Many) TradeHistory
          ──→ (Many) StrategySignal
          ──→ (Many) Position
          ──→ (Many) BrokerCredentials

StrategyMaster (1) ──→ (Many) StrategyPlan

StrategyPlan (1) ──→ (Many) StrategySignal
```

## Database Models with user_id

### TradeHistory
```python
{
    id: Integer (Primary Key)
    user_id: Integer (Foreign Key -> users.id)
    stock_symbol: String(20)
    action: String(10)  # BUY/SELL
    entry_price: Float
    exit_price: Float (nullable)
    quantity: Integer
    pnl: Float  # Profit & Loss
    status: String(20)  # OPEN/CLOSED
    strategy: String(100)  # Strategy name
    entry_time: DateTime
    exit_time: DateTime (nullable)
    created_at: DateTime
    updated_at: DateTime
}
```

### Position
```python
{
    id: Integer (Primary Key)
    user_id: Integer (Foreign Key -> users.id)
    symbol: String(20)
    quantity: Integer
    average_price: Float
    current_price: Float
    invested_value: Float
    current_value: Float
    strategy: String(100)
    entry_time: DateTime
    created_at: DateTime
    updated_at: DateTime
}
```

### StrategySignal
```python
{
    id: Integer (Primary Key)
    user_id: Integer (Foreign Key -> users.id)
    event_id: UUID
    strategy_id: Integer
    plan_id: Integer
    stock_symbol: String(20)
    signal_type: String(10)  # BUY/SELL/HOLD
    confidence: Float  # 0.0 to 1.0
    price: Float
    upper_bound: Float (nullable)
    lower_bound: Float (nullable)
    reason: String (nullable)
    status: String(20)  # PENDING/EXECUTED/CANCELLED
    timestamp: DateTime
    executed: Boolean
    executed_at: DateTime (nullable)
    created_at: DateTime
}
```

### StrategyPlan
```python
{
    plan_id: Integer (Primary Key)
    user_id: Integer (Foreign Key -> users.id)
    strategy_id: Integer (Foreign Key -> strategy_master.strategy_id)
    stock_symbol: String(20)
    enabled: Boolean
    override_cron: String(50) (nullable)
    override_params: JSON (nullable)
    total_signals: Integer
    total_trades: Integer
    win_rate: Float
    total_pnl: Float
    last_executed_at: DateTime (nullable)
    created_at: DateTime
    updated_at: DateTime
}
```

## Setup Instructions

### 1. PostgreSQL Installation

```bash
# On Windows (using PostgreSQL installer)
# Download from: https://www.postgresql.org/download/windows/

# On macOS (using Homebrew)
brew install postgresql@15

# On Linux (Ubuntu/Debian)
sudo apt-get install postgresql postgresql-contrib
```

### 2. Create Database and User

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE smart_trade_db;

# Create user
CREATE USER smart_trade WITH PASSWORD 'smart_trade_password';

# Grant privileges
ALTER ROLE smart_trade SET client_encoding TO 'utf8';
ALTER ROLE smart_trade SET default_transaction_isolation TO 'read committed';
ALTER ROLE smart_trade SET default_transaction_deferrable TO on;
ALTER ROLE smart_trade SET default_transaction_read_uncommitted TO off;
GRANT ALL PRIVILEGES ON DATABASE smart_trade_db TO smart_trade;

# Connect to the database
\c smart_trade_db

# Grant schema permissions
GRANT ALL ON SCHEMA public TO smart_trade;
```

### 3. Environment Configuration

Create `.env` file:
```
DATABASE_URL=postgresql://smart_trade:smart_trade_password@localhost:5432/smart_trade_db
```

### 4. Create Tables

Using SQLAlchemy models (from `common/db/models/`):

```bash
# Python script to create tables
python -c "
from common.db.base import Base
from common.db.models.user import User
from common.db.models.trade_history import TradeHistory
from common.db.models.position import Position
from common.db.models.strategy import StrategyMaster, StrategyPlan
from common.db.models.strategy_signal import StrategySignal
from common.db.database import engine

Base.metadata.create_all(bind=engine)
print('Tables created successfully!')
"
```

Or use Alembic migrations (if configured):

```bash
alembic upgrade head
```

### 5. Seed Initial Data

```python
from sqlalchemy.orm import Session
from common.db.database import SessionLocal
from common.db.models.strategy import StrategyMaster
from datetime import datetime

db = SessionLocal()

# Insert default strategies
strategies = [
    StrategyMaster(
        strategy_name="sma_rsi_macd",
        description="Combination of SMA, RSI, and MACD indicators",
        default_cron="*/5 * * * *",
        default_params={
            "fast_sma": 10,
            "slow_sma": 20,
            "rsi_period": 14,
            "rsi_overbought": 70,
            "rsi_oversold": 30,
        }
    ),
    StrategyMaster(
        strategy_name="moving_avg_crossover",
        description="Golden/Death cross strategy using moving averages",
        default_cron="*/5 * * * *",
        default_params={
            "short_period": 50,
            "long_period": 200,
        }
    ),
    StrategyMaster(
        strategy_name="rsi_macd",
        description="RSI and MACD divergence strategy",
        default_cron="*/5 * * * *",
        default_params={
            "rsi_period": 14,
            "macd_fast": 12,
            "macd_slow": 26,
            "signal_period": 9,
        }
    ),
]

db.add_all(strategies)
db.commit()
print(f"Inserted {len(strategies)} strategies")
db.close()
```

## API Routes and Database Queries

### Strategies
- `GET /api/strategies` - Queries `strategy_plan` with `user_id` filter
- `GET /api/strategies/{name}` - Queries `strategy_master` by name
- `POST /api/strategies/{name}/start` - Updates `strategy_plan.enabled = true`
- `POST /api/strategies/{name}/stop` - Updates `strategy_plan.enabled = false`

### Trades
- `GET /api/trades` - Queries `trade_history` with `user_id` filter
- `GET /api/trades/{id}` - Gets single trade by `id` and `user_id`
- `GET /api/trades/summary` - Aggregates P&L from trades
- `GET /api/trades/statistics` - Calculates metrics from trades

### Positions
- `GET /api/positions` - Queries `position` with `user_id` filter
- `GET /api/positions/summary` - Sums position values
- `POST /api/positions/{id}/close` - Deletes position

### Signals
- `GET /api/signals` - Queries `strategy_signals` with `user_id` filter
- `POST /api/signals/{id}/execute` - Updates `status = EXECUTED`
- `POST /api/signals/{id}/cancel` - Updates `status = CANCELLED`

### Account
- `GET /api/account/balance` - Calculates from trades + positions
- `GET /api/account/info` - Gets user info + trade counts

### Analytics
- `GET /api/analytics/performance` - Aggregates all trade metrics
- `GET /api/analytics/strategies` - Groups trades by strategy
- `GET /api/analytics/monthly-returns` - Groups trades by month
- `GET /api/analytics/equity-curve` - Calculates running balance

## Database Indexing

For optimal query performance, the following indexes are created:

```sql
-- User lookups
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

-- User-related data
CREATE INDEX idx_trade_history_user_id ON trade_history(user_id);
CREATE INDEX idx_trade_history_symbol ON trade_history(stock_symbol);
CREATE INDEX idx_position_user_id ON position(user_id);
CREATE INDEX idx_strategy_signal_user_id ON strategy_signals(user_id);
CREATE INDEX idx_strategy_plan_user_id ON strategy_plan(user_id);

-- Time-based queries
CREATE INDEX idx_trade_history_created ON trade_history(created_at);
CREATE INDEX idx_strategy_signal_timestamp ON strategy_signals(timestamp);
```

## Testing Database Queries

### Using psql CLI

```bash
psql -U smart_trade -d smart_trade_db

-- View all trades for a user
SELECT * FROM trade_history WHERE user_id = 1;

-- Get P&L summary
SELECT SUM(pnl) as total_pnl, COUNT(*) as trade_count FROM trade_history WHERE user_id = 1 AND status = 'CLOSED';

-- Get open positions
SELECT * FROM positions WHERE user_id = 1;

-- Get strategy performance
SELECT strategy, COUNT(*) as trades, SUM(pnl) as total_pnl FROM trade_history WHERE user_id = 1 GROUP BY strategy;
```

### Using Python with SQLAlchemy

```python
from sqlalchemy.orm import Session
from common.db.database import SessionLocal
from common.db.models.trade_history import TradeHistory
from common.db.models.user import User

db = SessionLocal()

# Get user trades
user_id = 1
trades = db.query(TradeHistory).filter(
    TradeHistory.user_id == user_id,
    TradeHistory.status == "CLOSED"
).all()

for trade in trades:
    print(f"{trade.stock_symbol}: {trade.action} {trade.quantity} @ {trade.entry_price} → P&L: {trade.pnl}")

db.close()
```

## Backup and Restore

### Backup Database

```bash
pg_dump -U smart_trade -d smart_trade_db -f backup.sql
```

### Restore Database

```bash
psql -U smart_trade -d smart_trade_db -f backup.sql
```

## Troubleshooting

### Connection Issues

```bash
# Test connection
psql -U smart_trade -h localhost -d smart_trade_db -c "SELECT 1"

# Check PostgreSQL status
sudo systemctl status postgresql  # Linux
brew services list  # macOS
```

### Permission Denied Errors

```sql
-- Grant proper permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO smart_trade;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO smart_trade;
```

### Reset Database

```bash
# Drop and recreate (development only!)
dropdb -U smart_trade smart_trade_db
createdb -U smart_trade -O smart_trade smart_trade_db
```

## Performance Tuning

### Query Optimization

```sql
-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM trade_history WHERE user_id = 1 AND status = 'CLOSED';

-- Update statistics
ANALYZE trade_history;
ANALYZE positions;
ANALYZE strategy_signals;
```

### Connection Pooling

The application uses SQLAlchemy with connection pooling. Configure in database session:

```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)
```

## Migration to Production

See `DEPLOYMENT.md` for production database setup with replication and backup strategies.
