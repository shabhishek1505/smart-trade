# Broker Integration Guide

## Overview

Smart-Trade now includes full broker integration with Angel One, supporting:
- Multi-user credential management (encrypted)
- Order placement (MARKET, LIMIT, STOPLOSS)
- Price data fetching
- Trade tracking and performance metrics
- Strategy signal execution with real broker orders

## Architecture

```
Signal Generation (Strategies)
  ↓
Kafka Pipeline (signal-processing-requests topic)
  ↓
SignalService (validates, executes)
  ↓
BrokerClient (Angel One API)
  ↓
Database (BrokerOrder, TradeHistory, Prices)
  ↓
UI Dashboard (realtime updates)
```

## Setup Instructions

### 1. Generate Encryption Key

First, generate an encryption key for storing credentials securely:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy the output and set it as an environment variable.

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Copy from .env.example
cp .env.example .env

# Edit .env with your settings
# CRITICAL: Set ENCRYPTION_KEY from step 1
ENCRYPTION_KEY=your_generated_key_here
```

### 3. Install Dependencies

```bash
pip install cryptography smartapi-python apscheduler pyotp
```

### 4. Initialize Database

Create the new database tables:

```bash
from common.db.base import Base
from common.db.session import engine

# Create all tables
Base.metadata.create_all(engine)
```

Or using Alembic migrations (if set up):

```bash
alembic upgrade head
```

### 5. Add User Credentials

Users need to store their Angel One credentials in the database. This can be done via:

**Option A: API Endpoint (Recommended)**
```bash
POST /api/credentials/add-broker
{
    "broker_type": "angel_one",
    "api_key": "your_api_key",
    "api_secret": "your_api_secret",
    "client_code": "your_client_code",
    "pin": "your_pin",
    "totp_key": "your_totp_key"  # Optional
}
```

**Option B: Direct Database Insert**
```python
from common.db.models.broker_credentials import BrokerCredentials
from common.db.session import get_session

session = get_session()

credentials = BrokerCredentials(
    user_id=1,
    broker_type="angel_one"
)
credentials.set_credentials(
    api_key="your_api_key",
    api_secret="your_api_secret",
    client_code="your_client_code",
    pin="your_pin"
)

session.add(credentials)
session.commit()
```

### 6. Start Price Fetcher Cron Job

Add to your main application startup:

```python
from worker.jobs.price_fetcher import schedule_price_fetcher

# In your application startup
scheduler = schedule_price_fetcher()
```

Or run manually:

```python
from worker.jobs.price_fetcher import fetch_prices_for_user

# Fetch prices for user 1
fetch_prices_for_user(user_id=1)
```

## Testing the Integration

### 1. Mock Broker Testing (No Credentials Required)

```python
from worker.brokers.factory import BrokerFactory
from common.db.models.broker_credentials import BrokerCredentials

# Create mock credentials
mock_creds = BrokerCredentials(
    user_id=999,
    broker_type="mock"
)
mock_creds.set_credentials("dummy", "dummy")

# Create mock broker
broker = BrokerFactory.create_broker("mock", mock_creds)

# Test
if broker.authenticate():
    price = broker.get_live_price("INFY")
    print(f"INFY Price: {price.price}")
```

### 2. Angel One Sandbox Testing

Use Angel One's sandbox/demo account:

1. Log in to Angel One website
2. Go to Settings → API Access
3. Generate API credentials
4. Set `BROKER_API_URL=demo` to use sandbox API
5. Store credentials via API/database

### 3. Signal Execution Test

```python
from common.dto.signal import StrategySignalData
from worker.services.signal_service import SignalService
from common.db.session import get_session
from datetime import datetime

# Create test signal
signal = StrategySignalData(
    plan_id=1,
    strategy_id=1,
    strategy_name="test_strategy",
    stock_symbol="INFY",
    signal="BUY",
    confidence_score=0.95,
    price=1850.0,
    upper_bound_price=1900.0,
    lower_bound_price=1800.0,
    evaluated_at=datetime.now(),
    user_id=1,
    broker_type="angel_one",
    order_type="MARKET"
)

# Execute signal
session = get_session()
service = SignalService(session)
result = service.execute_signal(signal)

print(f"Execution Result: {result}")
```

### 4. Check Executed Orders

```python
from common.db.repository.broker_order_repository import BrokerOrderRepository
from common.db.session import get_session

session = get_session()
repo = BrokerOrderRepository(session)

# Get pending orders
pending = repo.get_pending_orders(user_id=1)
for order in pending:
    print(f"Order {order.broker_order_id}: {order.status}")

# Get filled orders (last 30 days)
filled = repo.get_filled_orders(user_id=1, days=30)
for order in filled:
    print(f"Filled {order.symbol}: {order.filled_quantity} @ {order.filled_price}")
```

## Key Files

### Models
- `common/db/models/broker_credentials.py` - Encrypted credential storage
- `common/db/models/price_data.py` - OHLC price data
- `common/db/models/broker_order.py` - Order tracking
- `common/db/models/strategy_performance.py` - Performance metrics

### Brokers
- `worker/brokers/base_broker.py` - Abstract interface
- `worker/brokers/angel_one_broker.py` - Angel One implementation
- `worker/brokers/mock_broker.py` - Mock for testing
- `worker/brokers/factory.py` - Broker factory

### Services
- `worker/services/signal_service.py` - Signal execution engine
- `worker/services/price_service.py` - Price fetching service

### Jobs
- `worker/jobs/price_fetcher.py` - Cron job for price updates

### Utilities
- `common/utils/encryption.py` - Encryption/decryption utilities
- `common/utils/config.py` - Configuration management

## Configuration Options

### Database
```
DATABASE_URL=postgresql://user:password@localhost:5432/smart-trade
```

### Kafka
```
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
PLAN_PROCESSING_KAFKA_TOPIC=plan-processing-requests
SIGNAL_PROCESSING_KAFKA_TOPIC=signal-processing-requests
```

### Trading
```
PRICE_FETCH_INTERVAL_MINUTES=5      # How often to fetch prices
PRICE_HISTORY_DAYS=30               # How many days of history to keep
SYMBOLS_TO_TRADE=INFY,TCS,RELIANCE  # Which symbols to trade
TRADE_CAPITAL_PERCENT=5.0           # % of capital per trade
```

### Encryption
```
ENCRYPTION_KEY=your_generated_key   # CRITICAL: Must be set
```

## Error Handling

### Common Errors

**1. ENCRYPTION_KEY not set**
```
ValueError: ENCRYPTION_KEY environment variable not set
```
Solution: Generate and set ENCRYPTION_KEY in .env

**2. No credentials for user**
```
No angel_one credentials for user 1
```
Solution: Add credentials via API or database

**3. Broker authentication failed**
```
Failed to authenticate broker for user 1
```
Solution: Verify API key, secret, client code, PIN in database

**4. Order placement rejected**
```
Order placement failed: Insufficient margin
```
Solution: Check account balance, adjust quantity calculation

## Performance Considerations

1. **Price Fetching**: Runs every 5 minutes (configurable)
2. **Order Execution**: Synchronous (waits for broker response)
3. **Database**: Uses indexes on (symbol, timestamp) for fast lookups
4. **Credentials**: Cached in broker client after loading from DB

## Security Best Practices

1. **Never log credentials** - Ensure logging doesn't expose encrypted values
2. **Use environment variables** - Don't hardcode encryption keys
3. **Rotate encryption keys** - If key is compromised
4. **Database encryption** - Use SSL for database connections
5. **API authentication** - Implement JWT/OAuth for API endpoints

## Next Steps

1. ✅ Phase 1: Broker Integration (COMPLETED)
2. 📋 Phase 2: Backend REST API (In Progress)
3. 🎨 Phase 3: Frontend UI Dashboard
4. 📊 Phase 4: Analytics & Backtesting

## Support

For issues, check:
1. Log files (`logs/` directory)
2. Database queries and broker responses
3. Environment variables (.env file)
4. Angel One API documentation

## References

- [Angel One SmartAPI Documentation](https://smartapi.angelbroking.com/)
- [SmartAPI Python Client](https://github.com/angelbroking-github/smartapi-python)
- [Cryptography Fernet Documentation](https://cryptography.io/en/latest/fernet/)
