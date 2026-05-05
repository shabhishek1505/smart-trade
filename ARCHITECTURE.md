# Smart-Trade Architecture

## Service-Oriented Design

The application is structured as **three independent deployable services** that communicate through shared databases and message queues.

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React 18)                      │
│                    http://localhost:3000                     │
└──────────────┬────────────────────────────┬─────────────────┘
               │                            │
         HTTP/REST                    WebSocket
               │                            │
        ┌──────▼──────────┐        ┌───────▼─────────┐
        │   REST API      │        │  WebSocket      │
        │  (FastAPI)      │        │  Connection     │
        │  Port 8000      │        │  Manager        │
        └──────┬──────────┘        └───────┬─────────┘
               │                           │
               └───────────┬───────────────┘
                           │
              ┌────────────▼────────────┐
              │  Shared PostgreSQL DB   │
              │  • Users               │
              │  • Trades             │
              │  • Positions          │
              │  • Strategies         │
              │  • Signals            │
              └────────────┬─────────────┘
                           │
         ┌─────────────────┼──────────────────┐
         │                 │                  │
    ┌────▼────┐      ┌────▼────┐      ┌─────▼─────┐
    │  Kafka  │      │  Kafka  │      │  Kafka    │
    │  Topic: │      │  Topic: │      │  Topic:   │
    │ signals │      │ trades  │      │ prices    │
    └────┬────┘      └────┬────┘      └─────┬─────┘
         │                 │                  │
         └─────────────────┼──────────────────┘
                           │
              ┌────────────▼────────────┐
              │  Worker Service        │
              │  (Background Jobs)     │
              │  • Consume signals     │
              │  • Execute trades      │
              │  • Process positions   │
              └───────────────────────┘
```

## Directory Structure

```
smart-trade/
├── api/                          # REST API Service (Separate Deployable)
│   ├── main.py                  # FastAPI application entry point
│   ├── config.py                # Configuration management
│   ├── auth.py                  # JWT authentication utilities
│   ├── dependencies.py          # Dependency injection
│   ├── routes/
│   │   ├── auth.py             # Authentication endpoints
│   │   ├── strategies.py       # Strategy management
│   │   ├── trades.py           # Trade history
│   │   ├── positions.py        # Position management
│   │   ├── signals.py          # Signal handling
│   │   ├── account.py          # Account info
│   │   ├── analytics.py        # Performance metrics
│   │   ├── credentials.py      # Broker credentials
│   │   └── prices.py           # Price data
│   ├── schemas/
│   │   ├── auth.py             # Auth request/response models
│   │   └── response.py         # Standard API responses
│   └── websocket/
│       └── manager.py          # WebSocket connection management
│
├── worker/                      # Background Worker Service (Separate Deployable)
│   ├── strategy/               # Trading strategy implementations
│   │   ├── sma_rsi_macd.py
│   │   ├── moving_avg_crossover.py
│   │   └── factory.py
│   ├── kafka/                  # Message queue consumers
│   │   ├── consumer.py
│   │   ├── producer.py
│   │   └── plan_processing_consumer.py
│   ├── main.py                 # Worker entry point (future)
│   ├── jobs/                   # Background job handlers
│   ├── brokers/                # Broker integrations
│   ├── services/               # Business logic services
│   └── signal/                 # Signal processing
│
├── common/                      # Shared Code (No Deployable)
│   ├── db/
│   │   ├── models/            # SQLAlchemy ORM models
│   │   │   ├── user.py
│   │   │   ├── trade_history.py
│   │   │   ├── position.py
│   │   │   ├── strategy.py
│   │   │   └── strategy_signal.py
│   │   ├── repository/        # Data access layer
│   │   ├── base.py            # Base model configuration
│   │   └── database.py        # Database connection
│   ├── dto/                   # Data transfer objects
│   └── utils/                 # Shared utilities
│       ├── config.py
│       ├── kafka.py
│       ├── encryption.py
│       └── logger.py
│
├── frontend/                   # React UI Service (Separate Deployable)
│   ├── src/
│   │   ├── pages/             # Page components
│   │   ├── components/        # Reusable components
│   │   ├── services/          # API client
│   │   ├── types/             # TypeScript definitions
│   │   ├── App.tsx
│   │   └── index.tsx
│   ├── public/
│   ├── package.json
│   └── Dockerfile
│
├── api_server.py              # API service entry point
├── worker_service.py          # Worker service entry point
├── docker-compose.yml         # Container orchestration
├── Dockerfile.backend         # Python service container
└── requirements.txt           # Python dependencies
```

## Services Breakdown

### 1. **API Service** (`api/` directory)
**Deployable**: YES  
**Port**: 8000  
**Entry Point**: `api_server.py` or `uvicorn api.main:app`

**Responsibilities**:
- Expose REST endpoints for client applications
- Handle authentication (JWT tokens)
- Validate requests and return responses
- Real-time updates via WebSocket
- Database queries for user data

**Deployment**: Can run multiple replicas behind a load balancer

```bash
# Start API service
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Or use entry point script
python api_server.py
```

### 2. **Worker Service** (`worker/` directory + `worker_service.py`)
**Deployable**: YES  
**Port**: None (background service)  
**Entry Point**: `worker_service.py`

**Responsibilities**:
- Consume trading signals from Kafka
- Execute trades via broker APIs
- Process strategy execution
- Update positions and P&L
- Generate new signals based on price data

**Deployment**: Can run multiple instances for parallelism

```bash
# Start worker service
python worker_service.py
```

### 3. **Frontend Service** (`frontend/` directory)
**Deployable**: YES  
**Port**: 3000  
**Entry Point**: `npm start` (development) or `serve` (production)

**Responsibilities**:
- User interface
- Form validation and submission
- Real-time updates via WebSocket
- Display trading data and analytics

**Deployment**: Served by React development server or Nginx

```bash
# Start frontend
cd frontend
npm start
```

### 4. **Common Library** (`common/` directory)
**Deployable**: NO  
**Purpose**: Shared code between services

**Contains**:
- Database models (SQLAlchemy ORM)
- Data repositories
- Shared utilities (logger, encryption, config)
- Data transfer objects (DTOs)

## Communication Patterns

### API ↔ Frontend
- **HTTP/REST**: Requests/responses
- **WebSocket**: Real-time updates (signals, trades, prices)

### Worker ↔ Services
- **Kafka**: Asynchronous message passing
  - `signals` topic: Trading signals to execute
  - `trades` topic: Executed trades
  - `prices` topic: Price updates
  - `orders` topic: Broker orders

### Services ↔ Database
- **PostgreSQL**: Persistent data storage
- **Connection Pooling**: Managed by SQLAlchemy

## Deployment Scenarios

### Development (Docker Compose)
```bash
docker-compose up -d
# All services in single command
```

### Production (Kubernetes)
```yaml
# Three separate deployments:
- api-deployment.yaml        (REST API)
- worker-deployment.yaml     (Background Worker)
- frontend-deployment.yaml   (React UI)

# Shared services:
- postgres-statefulset.yaml  (Database)
- kafka-deployment.yaml      (Message Queue)
- redis-deployment.yaml      (Cache)
```

### Cloud (AWS/GCP/Azure)
```
API Service:
  - ECS/Cloud Run for API container
  - ALB/Load Balancer in front
  - CloudWatch/Cloud Logging

Worker Service:
  - ECS/Cloud Run for Worker container
  - Auto-scaling based on Kafka lag
  - CloudWatch/Cloud Logging

Frontend:
  - S3/Cloud Storage + CloudFront CDN
  - Or: Cloud Run + Cloud Armor

Database:
  - RDS PostgreSQL (Managed)
  - Automated backups
  - Read replicas for scaling

Kafka:
  - Managed Kafka Service
  - Or: Self-hosted with auto-scaling
```

## Data Flow Example: Trade Execution

```
1. User Interface (Frontend)
   ↓ HTTP POST /api/signals/{id}/execute
2. API Service (FastAPI)
   ↓ Validate user ownership
   ↓ Update StrategySignal.status = EXECUTED
   ↓ Publish event to Kafka
3. Kafka Topic: "signals"
   ↓ Worker Service consumes
4. Worker Service
   ↓ Get broker credentials
   ↓ Call Angel One API to place order
   ↓ Create TradeHistory record
   ↓ Publish trade event to Kafka
5. Kafka Topic: "trades"
   ↓ All services can consume
6. API Service broadcasts via WebSocket
   ↓ Frontend receives update
7. User Interface (Frontend)
   ↓ Display trade execution in real-time
```

## Scalability Considerations

### Horizontal Scaling

**API Service** (Stateless)
- Add more instances behind load balancer
- Session state in JWT (stateless)
- No shared memory

**Worker Service** (Stateless)
- Add more instances
- Kafka handles job distribution
- Parallel execution of strategies

**Frontend** (Static files)
- Deploy to CDN
- Or run multiple instances

**Database** (Stateful)
- Read replicas for read scaling
- Write master for consistency
- Connection pooling per service

### Vertical Scaling

- Increase container memory/CPU limits
- Upgrade database instance size
- Optimize database indexes

## Technology Choices

| Component | Technology | Reason |
|-----------|-----------|--------|
| API Framework | FastAPI | Async, fast, automatic docs |
| Database | PostgreSQL | ACID, JSON support, reliability |
| Message Queue | Kafka | High throughput, durability, replayability |
| Frontend | React 18 | Component-based, ecosystem, performance |
| Styling | Tailwind CSS | Utility-first, responsive, fast |
| Container | Docker | Consistency, easy deployment |
| Orchestration | Docker Compose / K8s | Local dev / production |

## Future Enhancements

- **Service Mesh** (Istio): Traffic management, security
- **API Gateway** (Kong/AWS): Rate limiting, authentication
- **Caching** (Redis): Frequently accessed data
- **Monitoring** (Prometheus/Grafana): Metrics, alerts
- **Tracing** (Jaeger): Distributed tracing
- **Logging** (ELK/Loki): Centralized logs
- **Message Queue Backup**: DLQ for failed messages
- **Database Replication**: High availability setup

## Security Considerations

### API Service
- JWT token validation on all endpoints
- CORS restricted to frontend URL
- Rate limiting per user
- SQL injection prevention (ORM)
- XSS prevention (React escaping)

### Worker Service
- Encrypted credential storage
- Secure broker API communication
- Validation of all inputs
- Audit logging of trades

### Database
- User data isolation (user_id filter)
- Encrypted password hashes
- Encrypted broker credentials
- Parameterized queries (SQLAlchemy)

## Monitoring & Observability

Each service should expose:
- `/health` endpoint for liveness checks
- `/metrics` endpoint for Prometheus
- Structured JSON logging
- Distributed tracing headers
- Error tracking (Sentry)

---

This architecture supports:
✅ Independent scaling  
✅ Fault isolation  
✅ Team separation  
✅ Technology flexibility  
✅ Easy testing  
✅ Clear responsibilities
