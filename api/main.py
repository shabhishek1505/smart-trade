"""FastAPI application for Smart-Trade"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from api.config import settings
from api.routes import auth, credentials, strategies, signals, trades, positions, prices, account, analytics
from api.websocket.manager import ConnectionManager
from common.utils.logger import init_logger

logger = init_logger("fastapi-app")


# Initialize WebSocket manager
ws_manager = ConnectionManager()


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Smart-Trade API Server")
    logger.info(f"API Host: {settings.API_HOST}:{settings.API_PORT}")
    logger.info(f"CORS Origins: {settings.FRONTEND_URL}")
    yield
    # Shutdown
    logger.info("Shutting down Smart-Trade API Server")


# Create FastAPI application
app = FastAPI(
    title="Smart-Trade API",
    description="Trading Strategy Execution Platform",
    version="2.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Store WebSocket manager in app state
app.state.ws_manager = ws_manager


# ==================== MIDDLEWARE ====================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000", "http://localhost:8001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host Middleware - Disabled for development
# app.add_middleware(
#     TrustedHostMiddleware,
#     allowed_hosts=["localhost", "127.0.0.1", "localhost:3000", "localhost:8000", "*"]
# )


# ==================== ERROR HANDLING ====================

class APIException(Exception):
    """Custom API exception"""
    def __init__(self, status_code: int, detail: str, code: str = "ERROR"):
        self.status_code = status_code
        self.detail = detail
        self.code = code


@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    """Handle API exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "code": exc.code,
            "message": exc.detail,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    import traceback
    error_msg = f"Unhandled exception in {request.method} {request.url.path}: {type(exc).__name__}: {str(exc)}\n{traceback.format_exc()}"
    print(f"\n\n{'='*80}\n{error_msg}\n{'='*80}\n", flush=True)
    logger.error(error_msg)

    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "code": "INTERNAL_ERROR",
            "message": str(exc)[:200],  # Return actual error message for debugging
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    )


# ==================== LOGGING MIDDLEWARE ====================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = datetime.utcnow()

    response = await call_next(request)

    process_time = (datetime.utcnow() - start_time).total_seconds()
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )

    return response


# ==================== TEST ROUTES ====================

@app.get("/api/test")
async def test_endpoint():
    """Test endpoint to verify API is working"""
    return {"status": "ok", "message": "API is working"}


# ==================== ROUTES ====================

# Include authentication routes
app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Authentication"],
)

# Include credentials routes
app.include_router(
    credentials.router,
    prefix="/api/credentials",
    tags=["Credentials"],
)

# Include strategies routes
app.include_router(
    strategies.router,
    prefix="/api/strategies",
    tags=["Strategies"],
)

# Include signals routes
app.include_router(
    signals.router,
    prefix="/api/signals",
    tags=["Signals"],
)

# Include trades routes
app.include_router(
    trades.router,
    prefix="/api/trades",
    tags=["Trades"],
)

# Include positions routes
app.include_router(
    positions.router,
    prefix="/api/positions",
    tags=["Positions"],
)

# Include prices routes
app.include_router(
    prices.router,
    prefix="/api/prices",
    tags=["Prices"],
)

# Include account routes
app.include_router(
    account.router,
    prefix="/api/account",
    tags=["Account"],
)

# Include analytics routes
app.include_router(
    analytics.router,
    prefix="/api/analytics",
    tags=["Analytics"],
)


# ==================== HEALTH CHECK ====================

@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "2.0.0",
    }


@app.get("/", tags=["Info"])
async def root():
    """API information"""
    return {
        "name": "Smart-Trade API",
        "version": "2.0.0",
        "docs": "/api/docs",
        "health": "/api/health",
    }


# ==================== WEBSOCKET ====================

@app.websocket("/api/ws")
async def websocket_endpoint(websocket):
    """WebSocket endpoint for real-time updates"""
    try:
        await ws_manager.connect(websocket)
        while True:
            data = await websocket.receive_text()
            logger.debug(f"WebSocket message: {data}")
            # Echo back or process messages
            await websocket.send_text(data)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        ws_manager.disconnect(websocket)


# ==================== RUN ====================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_DEBUG,
        log_level="info",
    )
