#!/bin/bash

# Script to run FastAPI application on port 8001
echo "Starting FastAPI application on port 8001..."
python3 his_fastapi.py

# Alternative command:
# uvicorn his_fastapi:app --reload --port 8001
