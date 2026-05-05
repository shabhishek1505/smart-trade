# Quick Start Guide - Broker Integration

## 5-Minute Setup

### 1. Generate Encryption Key
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Copy the output
```

### 2. Create .env File
```bash
cat > .env << EOF
ENCRYPTION_KEY=paste_your_key_here
DATABASE_URL=postgresql://postgres:admin@localhost:5432/smart-trade
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
BROKER_DEFAULT=angel_one
PRICE_FETCH_INTERVAL_MINUTES=5
LOG_LEVEL=INFO
EOF
```

### 3. Install Dependencies
```bash
pip install cryptography smartapi-python apscheduler pyotp
```

### 4. Create Database Tables
```bash
python scripts/init_broker_tables.py
```

### 5. Test with Mock Broker
```python
from worker.brokers.factory import BrokerFactory
from common.db.models.broker_credentials import BrokerCredentials

# Create mock credentials
creds = BrokerCredentials(user_id=1, broker_type="mock")
creds.set_credentials("test", "test")

# Create broker and test
broker = BrokerFactory.create_broker("mock", creds)
broker.authenticate()

# Place test order
response = broker.place_order("INFY", "BUY", 10)
print(f"Order: {response.order_id}, Status: {response.status}")
```

## Common Commands

### Add Angel One Credentials
```bash
python scripts/manage_credentials.py add
# Interactive prompt for API key, secret, client code, PIN
```

### List All Credentials
```bash
python scripts/manage_credentials.py list
```

### Test Broker Connection
```bash
python scripts/manage_credentials.py test
```

### Fetch Prices for a User
```python
from worker.jobs.price_fetcher import fetch_prices_for_user
fetch_prices_for_user(user_id=1)
```

### Execute a Signal
```python
from common.dto.signal import StrategySignalData
from worker.services.signal_service import SignalService
from common.db.session import get_session
from datetime import datetime

signal = StrategySignalData(
    plan_id=1,
    strategy_id=1,
    strategy_name="sma_rsi_macd",
    stock_symbol="INFY",
    signal="BUY",
    confidence_score=0.9,
    price=1850.0,
    lower_bound_price=1800.0,
    upper_bound_price=1900.0,
    evaluated_at=datetime.now(),
    user_id=1,
    broker_type="angel_one",
    order_type="MARKET"
)

session = get_session()
service = SignalService(session)
result = service.execute_signal(signal)
print(result)
```

### Check Executed Orders
```python
from common.db.repository.broker_order_repository import BrokerOrderRepository
from common.db.session import get_session

session = get_session()
repo = BrokerOrderRepository(session)

# Get pending orders
pending = repo.get_pending_orders(user_id=1)
for order in pending:
    print(f"{order.broker_order_id}: {order.status}")

# Get filled orders
filled = repo.get_filled_orders(user_id=1)
for order in filled:
    print(f"Filled {order.symbol} x{order.filled_quantity} @ {order.filled_price}")
```

## Project Structure

```
smart-trade/
├── common/                      # Shared code
│   ├── db/                     # Database layer
│   │   ├── models/             # SQLAlchemy models
│   │   └── repository/         # Repository pattern
│   ├── dto/                    # Data transfer objects
│   └── utils/                  # Utilities (config, logging, encryption)
├── worker/                      # Worker/execution layer
│   ├── brokers/                # Broker integrations (NEW)
│   ├── services/               # Business logic (SignalService, PriceService)
│   ├── jobs/                   # Cron jobs (price fetcher)
│   ├── strategy/               # Trading strategies
│   └── kafka/                  # Kafka consumers/producers
└── strategy-scheduler/         # Scheduler service
```

## Key Classes

### BrokerClient (Abstract)
```python
from worker.brokers.base_broker import BrokerClient

class MyBroker(BrokerClient):
    def authenticate(self) -> bool: ...
    def place_order(...) -> OrderResponse: ...
    def get_live_price(symbol) -> PriceData: ...
    def get_positions() -> List[Position]: ...
    # ... more methods
```

### SignalService
```python
from worker.services.signal_service import SignalService

service = SignalService(db_session)
result = service.execute_signal(signal_data)
# Returns: {"status": "EXECUTED", "order_id": "...", ...}
```

### PriceService
```python
from worker.services.price_service import PriceService

service = PriceService()
service.fetch_and_store_prices(user_id=1, symbols=["INFY", "TCS"])
prices = service.get_cached_prices("INFY", days=30)
latest = service.get_latest_price("INFY")
```

### BrokerFactory
```python
from worker.brokers.factory import BrokerFactory

# Create broker client
broker = BrokerFactory.create_broker("angel_one", credentials)

# Supported types: "angel_one", "zerodha", "mock"
```

## Database Schema

### broker_credentials
- id, user_id, broker_type
- encrypted_api_key, encrypted_api_secret
- encrypted_client_code, encrypted_pin, encrypted_totp_key
- is_active, created_at, updated_at

### price_data
- id, symbol, open_price, high_price, low_price, close_price, volume
- interval (5M, 15M, 1H, 1D), timestamp
- Indexed: (symbol, timestamp), (symbol, interval)

### broker_order
- id, user_id, signal_id, broker_order_id
- symbol, action (BUY/SELL), order_type (MARKET/LIMIT/STOPLOSS)
- quantity, price, sl_price, target_price
- status, filled_quantity, filled_price
- created_at, updated_at, filled_at

### strategy_performance
- id, user_id, strategy_name
- total_trades, winning_trades, losing_trades, win_rate
- total_pnl, avg_profit, avg_loss, max_profit, max_loss
- max_drawdown, profit_factor, sharpe_ratio, sortino_ratio
- total_signals, executed_signals, signal_accuracy

## Environment Variables

```
# Required
ENCRYPTION_KEY                    # Encryption key for credentials
DATABASE_URL                      # PostgreSQL connection string

# Broker
BROKER_DEFAULT=angel_one
PRICE_FETCH_INTERVAL_MINUTES=5
PRICE_HISTORY_DAYS=30
SYMBOLS_TO_TRADE=INFY,TCS,...

# Trading
TRADE_CAPITAL_PERCENT=5.0

# Kafka
KAFKA_BOOTSTRAP_SERVERS
PLAN_PROCESSING_KAFKA_TOPIC
SIGNAL_PROCESSING_KAFKA_TOPIC

# Logging
LOG_LEVEL=INFO

# API (Phase 2)
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=False
```

## Troubleshooting

### "ENCRYPTION_KEY environment variable not set"
Generate key: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`

### "No active Angel One credentials for user"
Add credentials: `python scripts/manage_credentials.py add`

### "Broker authentication failed"
- Check API key, secret, client code in database
- Verify Angel One account is active
- Check PIN and TOTP if applicable

### "Could not fetch live price"
- Verify symbol is valid
- Check Angel One API rate limits
- Ensure WebSocket connection is active

## Next Steps

1. ✅ **Phase 1**: Broker Integration (DONE)
   - Read: `BROKER_INTEGRATION_GUIDE.md`
   - Setup: Follow 5-minute setup above

2. 📋 **Phase 2**: Backend REST API
   - Coming soon

3. 🎨 **Phase 3**: Frontend Dashboard
   - Coming soon

## Support

- **Setup Help**: See `BROKER_INTEGRATION_GUIDE.md`
- **Architecture**: See `PHASE1_COMPLETION_SUMMARY.md`
- **API Docs**: Angel One SmartAPI (https://smartapi.angelbroking.com/)

---

**Ready to trade!** 🚀
