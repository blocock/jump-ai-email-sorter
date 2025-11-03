#!/bin/bash

# AI Email Sorter - Test Script
# Runs all tests for backend and frontend

set -e

echo "================================"
echo "Running Tests"
echo "================================"
echo ""

# Backend tests
echo "Running backend tests..."
cd backend
source venv/bin/activate
pytest tests/ -v --cov=app --cov-report=term-missing
BACKEND_EXIT=$?
cd ..

echo ""

# Frontend tests
echo "Running frontend tests..."
cd frontend
npm test -- --coverage --watchAll=false
FRONTEND_EXIT=$?
cd ..

echo ""
echo "================================"
echo "Test Results"
echo "================================"

if [ $BACKEND_EXIT -eq 0 ]; then
    echo "✓ Backend tests passed"
else
    echo "✗ Backend tests failed"
fi

if [ $FRONTEND_EXIT -eq 0 ]; then
    echo "✓ Frontend tests passed"
else
    echo "✗ Frontend tests failed"
fi

# Exit with error if any tests failed
if [ $BACKEND_EXIT -ne 0 ] || [ $FRONTEND_EXIT -ne 0 ]; then
    exit 1
fi

