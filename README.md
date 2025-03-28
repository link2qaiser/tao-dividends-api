# Tao Dividends API

A FastAPI-based asynchronous service for querying Tao dividends from the Bittensor blockchain with sentiment-based staking.

## Project Overview

This project implements a production-grade asynchronous API service that:

1. Provides an authenticated FastAPI endpoint to query Tao dividends from the Bittensor blockchain
2. Caches blockchain query results in Redis for 2 minutes
3. Optionally triggers background stake/unstake operations based on Twitter sentiment:
   - Queries Twitter via Datura.ai API for tweets about the subnet
   - Analyzes tweet sentiment using Chutes.ai LLM
   - Stakes or unstakes TAO proportional to sentiment score (-100 to +100)
4. Uses Celery workers to handle async blockchain and sentiment analysis tasks
5. Stores historical data in a high-concurrency asynchronous database

## Architecture

The application follows modern async patterns:

- FastAPI handles HTTP requests
- Redis serves as cache and message broker
- Celery workers process background tasks
- PostgreSQL database with async access stores results
- Docker containers orchestrate all components

## Key Features

- **Asynchronous Design**: Leverages asyncio throughout for non-blocking operations
- **Authentication**: Secure API access with JWT tokens
- **Caching**: Efficient Redis caching to minimize blockchain queries
- **Sentiment Analysis**: Twitter sentiment analysis to guide trading decisions
- **Real Blockchain Integration**: Direct communication with Bittensor blockchain
- **Scalable Background Processing**: Celery tasks for long-running operations
- **Comprehensive Testing**: Unit, integration, and concurrency tests

## Project Structure

```
📦 tao-dividends-api
 ┣ 📂 alembic        # Database migration files
 ┣ 📂 app
 ┃ ┣ 📂 api          # API endpoints and routes
 ┃ ┣ 📂 core         # Core functionality (config, security)
 ┃ ┣ 📂 crud         # Database CRUD operations
 ┃ ┣ 📂 models       # Database models
 ┃ ┣ 📂 schemas      # Pydantic schemas for validation
 ┃ ┣ 📂 services     # Business logic services
 ┃ ┣ 📂 tasks        # Celery background tasks
 ┃ ┣ 📜 main.py      # FastAPI application entry point
 ┃ ┗ 📜 worker.py    # Celery worker configuration
 ┣ 📂 tests          # Test files
 ┣ 📜 .env.example   # Example environment variables
 ┣ 📜 docker-compose.yml  # Docker configuration
 ┣ 📜 Dockerfile     # Docker build configuration
 ┣ 📜 README.md      # Project documentation
 ┗ 📜 requirements.txt  # Python dependencies
```

## Key Components

### API Routes

- `GET /api/v1/tao_dividends`: Get Tao dividends data for a subnet and hotkey
- `POST /api/v1/auth/token`: Obtain JWT token for authentication
- `POST /api/v1/auth/register`: Register a new user
- `GET /api/v1/sentiment/analyze`: Analyze sentiment for a subnet
- `GET /api/v1/sentiment/tweets`: Search for tweets about a subnet

### Services

- **BlockchainService**: Handles interactions with the Bittensor blockchain
- **SentimentService**: Manages sentiment analysis via Datura.ai and Chutes.ai
- **RedisCache**: Provides caching functionality

### Background Tasks

- **process_sentiment_stake**: Analyzes sentiment and performs stake/unstake operations

## Setup Instructions

### Prerequisites

- Docker and Docker Compose
- PostgreSQL (included in Docker setup)
- Redis (included in Docker setup)

### Environment Variables

Create a `.env` file based on `.env.example` with the following variables:

```
# API and Security
API_TOKEN=your_api_token
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/tao_dividends
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=tao_dividends

# Redis
REDIS_URL=redis://redis:6379/0
CACHE_TTL=120

# Bittensor
BITTENSOR_CHAIN_ENDPOINT=ws://127.0.0.1:9944
BITTENSOR_NETWORK=testnet
DEFAULT_NETUID=18
DEFAULT_HOTKEY=5FFApaS75bv5pJHfAp2FVLBj9ZaXuFDjEypsaBNc1wCfe52v
WALLET_SEED=diamond like interest affair safe clarify lawsuit innocent beef van grief color

# API Keys
DATURA_API_KEY=your_datura_api_key
CHUTES_API_KEY=your_chutes_api_key
```

### Running with Docker

1. Build and start the services:

```bash
docker-compose up --build
```

2. The application should be accessible at:
   - FastAPI server: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-mock pytest-cov

# Run the tests
pytest
```

## API Usage Examples

### Authentication

```bash
# Register a new user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "email": "test@example.com", "password": "password123"}'

# Get authentication token
curl -X POST "http://localhost:8000/api/v1/auth/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=testuser&password=password123"
```

### Query Tao Dividends

```bash
# Get Tao dividends for a specific netuid and hotkey
curl -X GET "http://localhost:8000/api/v1/tao_dividends?netuid=18&hotkey=5FFApaS75bv5pJHfAp2FVLBj9ZaXuFDjEypsaBNc1wCfe52v" \
     -H "Authorization: Bearer your_token_here"

# Get Tao dividends with trade=true to trigger sentiment analysis
curl -X GET "http://localhost:8000/api/v1/tao_dividends?trade=true" \
     -H "Authorization: Bearer your_token_here"
```

### Sentiment Analysis

```bash
# Analyze sentiment for a subnet
curl -X GET "http://localhost:8000/api/v1/sentiment/analyze?netuid=18" \
     -H "Authorization: Bearer your_token_here"

# Search for tweets
curl -X GET "http://localhost:8000/api/v1/sentiment/tweets?query=Bittensor%20netuid%2018" \
     -H "Authorization: Bearer your_token_here"
```

## Completed Implementations

1. ✅ **Blockchain Integration**: Implemented real blockchain queries using AsyncSubtensor
2. ✅ **API Endpoints**: Created authenticated endpoints for dividends and sentiment data
3. ✅ **Background Processing**: Set up Celery tasks for sentiment-based staking
4. ✅ **Caching**: Implemented Redis caching to minimize blockchain queries
5. ✅ **Testing**: Added comprehensive test suite with mocks for external services
6. ✅ **Authentication**: Implemented JWT-based authentication
7. ✅ **Documentation**: Created API documentation with Swagger UI

## Future Enhancements

1. 🔲 **Monitoring & Alerting**: Add Prometheus metrics and alerts
2. 🔲 **Performance Optimization**: Improve handling of large-scale concurrent requests
3. 🔲 **Admin Dashboard**: Create a UI for monitoring operations
4. 🔲 **Extended Testing**: Add load testing and security testing
5. 🔲 **CI/CD Pipeline**: Automate testing and deployment

[Watch the video on YouTube](https://youtu.be/swvUhwnoz_A)
