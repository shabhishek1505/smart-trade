# Smart-Trade: Intelligent Trading Bot

A production-ready trading automation platform with real-time strategy monitoring, trade execution, and performance analytics. Built with FastAPI, React 18, PostgreSQL, and Kafka.

## Features

- **Multi-Strategy Support**: Run multiple trading strategies simultaneously
- **Real-Time Monitoring**: Live signal generation and trade execution updates via WebSocket
- **Performance Analytics**: Comprehensive dashboard with equity curves and metrics
- **Multi-Broker Support**: Angel One integration with extensible broker abstraction
- **Secure Authentication**: JWT-based multi-user authentication with encrypted credentials
- **Trade History & Analytics**: Complete trade history with P&L calculations
- **Responsive UI**: Mobile-friendly React dashboard with Tailwind CSS

## Tech Stack

### Backend
- FastAPI (Python 3.11+)
- PostgreSQL with SQLAlchemy ORM
- JWT authentication with bcrypt
- Apache Kafka for events
- WebSocket for real-time updates

### Frontend
- React 18 with TypeScript
- Tailwind CSS for styling
- Axios HTTP client
- Recharts for visualizations
- React Router v6

### Deployment
- Docker & Docker Compose
- PostgreSQL, Kafka, Zookeeper, Redis

## Quick Start

### Docker Compose (Recommended)

```bash
# Clone and setup
git clone https://github.com/yourusername/smart-trade.git
cd smart-trade

# Copy environment files
cp .env.example .env
cp frontend/.env.example frontend/.env

# Update broker credentials in .env

# Start services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Kafka UI: http://localhost:8080
```

### Local Development

#### Backend
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn worker.api.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm start
```

## API Endpoints

### Auth
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/auth/change-password`

### Strategies
- `GET /api/strategies`
- `POST /api/strategies/{name}/start`
- `POST /api/strategies/{name}/stop`
- `GET /api/strategies/{name}/performance`

### Trades & Signals
- `GET /api/trades`
- `GET /api/signals`
- `POST /api/signals/{id}/execute`

### Account
- `GET /api/account/balance`
- `GET /api/positions`

### Analytics
- `GET /api/analytics/performance`
- `GET /api/analytics/strategies`

### WebSocket
- `WS /api/ws` - Real-time updates

## Project Structure

```
smart-trade/
├── worker/
│   ├── api/                 # FastAPI application
│   │   ├── routes/         # API endpoints
│   │   ├── schemas/        # Pydantic models
│   │   └── websocket/      # WebSocket handlers
│   ├── strategy/           # Trading strategies
│   └── kafka/              # Message consumers
│
├── common/
│   ├── db/models/         # Database models
│   └── dto/               # Data transfer objects
│
├── frontend/
│   ├── src/
│   │   ├── pages/        # Page components
│   │   ├── services/     # API client
│   │   └── types/        # TypeScript types
│   └── public/           # Static files
│
├── docker-compose.yml
└── requirements.txt
```

## Configuration

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost:5432/smart_trade_db
SECRET_KEY=your-secret-key
API_PORT=8000
FRONTEND_URL=http://localhost:3000
BROKER_API_KEY=your_key
BROKER_API_SECRET=your_secret
```

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_WS_URL=ws://localhost:8000/api/ws
```

## Security

- Broker credentials encrypted at rest
- JWT tokens (HS256 signed)
- CORS restricted to frontend URL
- SQL injection prevention via ORM
- XSS prevention via React
- Password hashing with bcrypt

## Monitoring

- API Logs: `docker-compose logs -f api`
- Kafka UI: http://localhost:8080
- API Docs: http://localhost:8000/docs

## Troubleshooting

### Database Connection
```bash
psql -h localhost -U smart_trade -d smart_trade_db
```

### Kafka Connectivity
```bash
docker exec smart-trade-kafka kafka-broker-api-versions.sh --bootstrap-server localhost:9092
```

### View Logs
```bash
docker logs smart-trade-api
docker logs smart-trade-frontend
```

## Contributing

1. Create feature branch: `git checkout -b feature/amazing-feature`
2. Commit: `git commit -m 'Add feature'`
3. Push: `git push origin feature/amazing-feature`
4. Open Pull Request

## License

MIT License - see LICENSE file

## Roadmap

- [ ] Paper trading mode
- [ ] Advanced risk management
- [ ] More broker integrations
- [ ] Machine learning signals
- [ ] Mobile app (React Native)
- [ ] Advanced charting
- [ ] Email/SMS notifications
- [ ] PDF export

## Support

- Issues: GitHub Issues
- Email: support@smart-trade.io
