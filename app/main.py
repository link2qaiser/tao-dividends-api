from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Tao Dividends API",
    description="API service for querying Tao dividends from the Bittensor blockchain",
    version="0.1.0",
)


@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}
