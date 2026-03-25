#!/bin/bash
set -e  # Exit on any error

# Run database migrations
alembic upgrade head

# Start the application using uvicorn (recommended for FastAPI)
# uvicorn main:app --host 0.0.0.0 --port $PORT
python main.py