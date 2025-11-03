# Setup Guide - AI Email Sorter

Complete setup instructions for development and production.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Google OAuth Setup](#google-oauth-setup)
- [OpenAI Setup](#openai-setup)
- [Local Development Setup](#local-development-setup)
- [Testing](#testing)
- [Common Issues](#common-issues)

## Prerequisites

### Required Software:
- **Python 3.11+**: [Download](https://www.python.org/downloads/)
- **Node.js 18+**: [Download](https://nodejs.org/)
- **PostgreSQL 15+**: [Download](https://www.postgresql.org/download/)
- **Redis** (optional for development): [Download](https://redis.io/download)
- **Git**: [Download](https://git-scm.com/)

### API Keys Needed:
- Google Cloud Project with OAuth credentials
- OpenAI API key

## Google OAuth Setup

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name: "AI Email Sorter" (or your choice)
4. Click "Create"

### 2. Enable Gmail API

1. In your project, go to "APIs & Services" → "Library"
2. Search for "Gmail API"
3. Click on it and click "Enable"

### 3. Configure OAuth Consent Screen

1. Go to "APIs & Services" → "OAuth consent screen"
2. Choose "External" (for testing)
3. Fill in required fields:
   - App name: "AI Email Sorter"
   - User support email: Your email
   - Developer contact: Your email
4. Click "Save and Continue"
5. **Add Scopes**:
   - Click "Add or Remove Scopes"
   - Add these scopes:
     - `https://www.googleapis.com/auth/gmail.readonly`
     - `https://www.googleapis.com/auth/gmail.modify`
     - `https://www.googleapis.com/auth/userinfo.email`
     - `https://www.googleapis.com/auth/userinfo.profile`
   - Click "Update" and "Save and Continue"
6. **Add Test Users**:
   - Click "Add Users"
   - Add email: `webshookeng@gmail.com`
   - Add your own email for testing
   - Click "Save and Continue"
7. Click "Back to Dashboard"

### 4. Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Application type: "Web application"
4. Name: "Email Sorter Web Client"
5. **Authorized redirect URIs**:
   - For development: `http://localhost:8000/auth/callback`
   - For production: `https://your-domain.com/auth/callback`
6. Click "Create"
7. **Save your credentials**:
   - Copy the Client ID
   - Copy the Client Secret
   - Keep these secure!

## OpenAI Setup

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Go to "API Keys" section
4. Click "Create new secret key"
5. Name it "Email Sorter"
6. Copy the key (you won't see it again!)
7. Keep it secure

## Local Development Setup

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd jump-ai-email-sorter
```

### 2. Database Setup

#### Option A: PostgreSQL (Recommended)

```bash
# Install PostgreSQL (macOS)
brew install postgresql@15
brew services start postgresql@15

# Or on Ubuntu/Debian
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Create database
createdb email_sorter

# Or using psql
psql postgres
CREATE DATABASE email_sorter;
\q
```

#### Option B: Use Docker

```bash
docker run -d --name postgres \
  -e POSTGRES_USER=email_sorter \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=email_sorter \
  -p 5432:5432 \
  postgres:15
```

### 3. Redis Setup (Optional)

```bash
# Install Redis (macOS)
brew install redis
brew services start redis

# Or on Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# Or use Docker
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

### 4. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
playwright install-deps  # Install system dependencies

# Create .env file
cat > .env << EOF
DATABASE_URL=postgresql://email_sorter:password@localhost:5432/email_sorter
SECRET_KEY=$(openssl rand -hex 32)
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here
OPENAI_API_KEY=your-openai-api-key-here
REDIS_URL=redis://localhost:6379
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
EOF

# Edit .env and replace the placeholder values with your actual credentials
nano .env  # or use your preferred editor

# Run database migrations (tables created automatically)
# Test the backend
uvicorn app.main:app --reload
```

The backend should now be running at http://localhost:8000

### 5. Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
echo "REACT_APP_API_URL=http://localhost:8000" > .env

# Start development server
npm start
```

The frontend should now be running at http://localhost:3000

### 6. Verify Setup

1. Open http://localhost:3000 in your browser
2. Click "Sign in with Google"
3. You should be redirected to Google OAuth
4. Sign in with a test user account
5. Grant permissions
6. You should be redirected back to the dashboard

## Testing

### Backend Tests

```bash
cd backend
source venv/bin/activate  # if not already activated

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

### Frontend Tests

```bash
cd frontend

# Run tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run tests in watch mode
npm test -- --watch
```

## Development Workflow

### Running the Full Stack

Terminal 1 - Backend:
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

Terminal 2 - Frontend:
```bash
cd frontend
npm start
```

### Making Changes

1. **Backend changes**: Save the file, FastAPI auto-reloads
2. **Frontend changes**: Save the file, React auto-reloads
3. **Database changes**: Update models in `backend/app/models.py`
4. **API changes**: Update routers in `backend/app/routers/`

### Database Management

```bash
# Connect to database
psql email_sorter

# Useful commands:
\dt              # List tables
\d users         # Describe users table
SELECT * FROM users;  # Query users
\q               # Quit
```

## Common Issues

### Issue: Import errors in Python

**Solution**: Make sure virtual environment is activated
```bash
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate  # Windows
```

### Issue: Database connection failed

**Solutions**:
1. Check PostgreSQL is running: `pg_isready`
2. Verify DATABASE_URL in .env
3. Test connection: `psql email_sorter`

### Issue: OAuth redirect_uri_mismatch

**Solutions**:
1. Check Google Cloud Console redirect URIs
2. Ensure they match exactly: `http://localhost:8000/auth/callback`
3. No trailing slashes
4. Check for typos

### Issue: Playwright browser not found

**Solution**: Install browsers
```bash
playwright install chromium
playwright install-deps
```

### Issue: OpenAI API errors

**Solutions**:
1. Verify API key is correct
2. Check you have credits: https://platform.openai.com/usage
3. Ensure API key has correct permissions

### Issue: CORS errors

**Solutions**:
1. Check FRONTEND_URL in backend .env matches frontend URL
2. Verify REACT_APP_API_URL in frontend .env
3. Clear browser cache

### Issue: Gmail API quota exceeded

**Solutions**:
1. Check quota usage in Google Cloud Console
2. Wait for quota to reset (usually daily)
3. Request quota increase if needed

### Issue: Port already in use

**Solutions**:
```bash
# Find process using port 8000
lsof -ti:8000
# Kill it
kill -9 $(lsof -ti:8000)

# Or use different port
uvicorn app.main:app --reload --port 8001
```

## Next Steps

1. **Create categories**: Define your email categories
2. **Sync emails**: Click "Sync Emails" to import
3. **Test features**: Try all functionality
4. **Read API docs**: http://localhost:8000/docs
5. **Deploy**: See DEPLOYMENT.md for production setup

## Development Tips

### Backend:
- API docs available at: http://localhost:8000/docs
- Use `print()` for quick debugging
- Check logs in terminal
- Use Python debugger: `import pdb; pdb.set_trace()`

### Frontend:
- React DevTools browser extension recommended
- Check browser console for errors
- Use `console.log()` for debugging
- Redux DevTools if you add Redux later

### Database:
- Use DBeaver or pgAdmin for GUI
- Regular backups: `pg_dump email_sorter > backup.sql`
- Reset database: Drop and recreate

## Getting Help

1. Check this guide
2. Check README.md
3. Check DEPLOYMENT.md
4. Search existing issues
5. Create new issue with:
   - Error message
   - Steps to reproduce
   - Environment details
   - Relevant logs

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Playwright Documentation](https://playwright.dev/)

