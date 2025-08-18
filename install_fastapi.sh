#!/bin/bash

# Script to install FastAPI dependencies

echo "Installing FastAPI and dependencies..."
pip install fastapi uvicorn[standard] pydantic sqlalchemy

echo "Installation completed."
echo "You can now run the FastAPI application using:"
echo "uvicorn his_fastapi:app --reload"
