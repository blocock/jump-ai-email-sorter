#!/bin/bash

# AI Email Sorter - Setup Script
# This script automates the initial setup process

set -e

echo "================================"
echo "AI Email Sorter - Setup Script"
echo "================================"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

command -v python3 >/dev/null 2>&1 || { echo "Error: Python 3 is required but not installed."; exit 1; }
command -v node >/dev/null 2>&1 || { echo "Error: Node.js is required but not installed."; exit 1; }
command -v psql >/dev/null 2>&1 || { echo "Error: PostgreSQL is required but not installed."; exit 1; }

echo "✓ All prerequisites found"
echo ""

# Backend setup
echo "Setting up backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Install Playwright
echo "Installing Playwright browsers..."
playwright install chromium
playwright install-deps

# Create .env if not exists
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo ""
    echo "⚠️  Please edit backend/.env and add your API credentials:"
    echo "   - GOOGLE_CLIENT_ID"
    echo "   - GOOGLE_CLIENT_SECRET"
    echo "   - OPENAI_API_KEY"
    echo ""
fi

cd ..

# Frontend setup
echo "Setting up frontend..."
cd frontend

# Install dependencies
echo "Installing Node dependencies..."
npm install

# Create .env if not exists
if [ ! -f ".env" ]; then
    echo "Creating frontend .env file..."
    echo "REACT_APP_API_URL=http://localhost:8000" > .env
fi

cd ..

echo ""
echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env with your API credentials"
echo "2. Create PostgreSQL database: createdb email_sorter"
echo "3. Start Redis (optional): redis-server"
echo "4. Start backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "5. Start frontend (new terminal): cd frontend && npm start"
echo ""
echo "See SETUP_GUIDE.md for detailed instructions"

