# Quick Start Guide

Get the AI Email Sorter running in **under 15 minutes**!

## Prerequisites (5 minutes)

1. **Google OAuth Credentials**
   - Go to https://console.cloud.google.com/
   - Create project → Enable Gmail API
   - Create OAuth credentials
   - Add redirect URI: `http://localhost:8000/auth/callback`
   - Add test user: `webshookeng@gmail.com`

2. **OpenAI API Key**
   - Go to https://platform.openai.com/
   - Create API key

3. **Install Software**
   - Python 3.11+
   - Node.js 18+
   - PostgreSQL 15+

## Setup (5 minutes)

```bash
# 1. Clone and enter directory
cd /home/kaiden/Documents/jump-ai-email-sorter

# 2. Create database
createdb email_sorter

# 3. Run automated setup
chmod +x scripts/*.sh
./scripts/setup.sh

# 4. Configure environment
cd backend
nano .env  # Add your credentials:
# GOOGLE_CLIENT_ID=your-client-id
# GOOGLE_CLIENT_SECRET=your-client-secret
# OPENAI_API_KEY=your-openai-key
# DATABASE_URL=postgresql://user:pass@localhost/email_sorter
```

## Run (2 minutes)

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm start
```

Visit: http://localhost:3000

## First Use (3 minutes)

1. Click "Sign in with Google"
2. Authorize the app
3. Create a category:
   - Name: "Newsletters"
   - Description: "Marketing emails, newsletters, promotional content"
4. Click "Sync Emails"
5. Wait 30 seconds
6. See your categorized emails!

## Docker Alternative (5 minutes)

```bash
# Set environment variables
export GOOGLE_CLIENT_ID="your-id"
export GOOGLE_CLIENT_SECRET="your-secret"
export OPENAI_API_KEY="your-key"

# Start everything
docker-compose up -d

# View logs
docker-compose logs -f
```

Visit: http://localhost:3000

## Deploy to Render (10 minutes)

1. Push code to GitHub
2. Go to https://render.com
3. New → Blueprint
4. Connect your repository
5. Add environment variables:
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
   - `OPENAI_API_KEY`
6. Update OAuth redirect URI in Google Console
7. Deploy!

## Troubleshooting

**Can't connect to database?**
```bash
createdb email_sorter
# Or check if PostgreSQL is running:
pg_isready
```

**Module not found?**
```bash
# Backend:
cd backend && source venv/bin/activate && pip install -r requirements.txt

# Frontend:
cd frontend && npm install
```

**OAuth error?**
- Verify redirect URI matches exactly
- Check test user is added
- Ensure credentials are correct

**Playwright error?**
```bash
cd backend
source venv/bin/activate
playwright install chromium
playwright install-deps
```

## Common Commands

```bash
# Run tests
./scripts/test.sh

# Start both services
./scripts/start.sh

# Reset database
dropdb email_sorter && createdb email_sorter

# Check API
curl http://localhost:8000/health

# View logs
# Backend: Check terminal
# Frontend: Check browser console
```

## Documentation

- **Full Setup**: [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Overview**: [README.md](README.md)

## Support

- Check documentation first
- Review error messages
- Check environment variables
- Verify API keys are valid
- Open GitHub issue if stuck

## What to Expect

- **First sync**: May take 30-60 seconds for 10-20 emails
- **AI categorization**: Very accurate with good descriptions
- **Unsubscribe**: Works on ~80% of emails (those with standard links)
- **Performance**: Handles hundreds of emails efficiently

## Next Steps

Once running:
1. Create 3-4 categories with detailed descriptions
2. Sync emails
3. Browse categorized emails
4. Try bulk actions
5. Test unsubscribe feature
6. Read full email content

Enjoy! 🎉

