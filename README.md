# Stock Monitor

Personal NSE stock monitoring system with daily automated analysis, Telegram alerts, and a React dashboard.

**Stack:** React + Vite (Vercel) · Flask (Render) · GitHub Actions · Telegram Bot  
**Cost:** ₹0/month

## Structure

```
├── frontend/       React UI (deploy to Vercel)
├── backend/        Flask API (deploy to Render)
├── analyser/       Python analysis scripts (runs via GitHub Actions)
├── config/
│   ├── stocks.json     Stock watchlist + settings (source of truth)
│   └── results.json    Latest analysis output (auto-updated by Actions)
└── .github/workflows/daily_analyse.yml
```

## Quick Start

### 1. Backend (local)
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 2. Frontend (local)
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173

### 3. Analyser (local test)
```bash
cd analyser
pip install -r requirements.txt
TELEGRAM_BOT_TOKEN=dummy python analyse.py
```

## GitHub Secrets Required

| Secret | Description |
|--------|-------------|
| `TELEGRAM_BOT_TOKEN` | From @BotFather |
| `RENDER_BACKEND_URL` | Your Render deployment URL |

## Deployment

- **Render** — connect repo, root: `backend`, start: `gunicorn app:app`
- **Vercel** — connect repo, root: `frontend`, add `VITE_API_URL=<render-url>`
- **GitHub Actions** — cron runs at 10:17 UTC (15:47 IST) Mon–Fri

## Strategies

| ID | Name |
|----|------|
| `rsi_ema` | RSI(14) + EMA(20/50) |
| `macd` | MACD(12,26,9) crossover |
| `breakout` | 52-week high breakout |
| `bollinger` | Bollinger Band squeeze |
| `volume_surge` | Volume spike (3× avg) |
