from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging

from app.api.routes import tao_dividends, auth, sentiment
from app.core.config import settings
from app.models.database import engine, Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Tao Dividends API",
    description="API service for querying Tao dividends from the Bittensor blockchain",
    version="0.1.0",
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify exact domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    tao_dividends.router,
    prefix="/api/v1",
    tags=["tao_dividends"],
)

app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["auth"],
)

app.include_router(
    sentiment.router,
    prefix="/api/v1/sentiment",
    tags=["sentiment"],
)


@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}
