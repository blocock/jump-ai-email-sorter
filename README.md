# AI Email Sorter

An intelligent email management application that uses AI to automatically categorize, summarize, and organize your Gmail emails.

## Features

- **Google OAuth Authentication**: Secure sign-in with your Google account
- **Multiple Gmail Accounts**: Connect and manage multiple Gmail accounts
- **Custom Categories**: Create custom categories with descriptions for AI-powered sorting
- **AI Categorization**: Automatically categorize incoming emails using OpenAI
- **AI Summarization**: Get concise AI-generated summaries of each email
- **Auto-Archive**: Emails are automatically archived in Gmail after import
- **Bulk Actions**: Select multiple emails to delete or unsubscribe
- **Smart Unsubscribe**: AI agent automatically navigates unsubscribe pages and forms
- **Beautiful UI**: Modern, responsive interface with excellent UX

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **PostgreSQL**: Primary database
- **SQLAlchemy**: ORM for database operations
- **OpenAI API**: AI categorization and summarization
- **Gmail API**: Email integration
- **Playwright**: Automated unsubscribe functionality
- **Redis**: Task queue (optional)

### Frontend
- **React**: UI framework
- **TypeScript**: Type-safe JavaScript
- **React Router**: Client-side routing
- **Axios**: HTTP client

## Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Google Cloud Project with Gmail API enabled
- OpenAI API key

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API
4. Go to "Credentials" and create OAuth 2.0 Client ID
5. Add authorized redirect URIs:
   - `http://localhost:8000/auth/callback` (development)
   - `https://your-domain.com/auth/callback` (production)
6. Add test users in OAuth consent screen:
   - Add `webshookeng@gmail.com` as a test user
7. Copy Client ID and Client Secret

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Create .env file
cp .env.example .env

# Edit .env with your credentials
DATABASE_URL=postgresql://user:password@localhost:5432/email_sorter
SECRET_KEY=your-secret-key-here
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
OPENAI_API_KEY=your-openai-api-key
REDIS_URL=redis://localhost:6379
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000

# Run database migrations (tables will be created automatically)
# The app uses SQLAlchemy and creates tables on startup

# Run the backend
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
echo "REACT_APP_API_URL=http://localhost:8000" > .env

# Run the frontend
npm start
```

The app will be available at `http://localhost:3000`

## Running Tests

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Deployment

### Using Docker

```bash
# Build and run with Docker Compose
docker-compose up -d

# The app will be available at:
# - Frontend: http://localhost:3000
# - Backend: http://localhost:8000
```

### Deploy to Render

1. Create a new account on [Render](https://render.com)
2. Connect your GitHub repository
3. Use the provided `render.yaml` for automatic deployment
4. Set environment variables in Render dashboard:
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
   - `OPENAI_API_KEY`
5. Update OAuth redirect URIs in Google Cloud Console with your Render URLs

### Deploy to Fly.io

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Deploy backend
cd backend
fly launch --dockerfile ../Dockerfile.backend

# Deploy frontend
cd frontend
fly launch --dockerfile ../Dockerfile.frontend
```

## Usage

1. **Sign In**: Click "Sign in with Google" and authorize the app
2. **Create Categories**: Click "+ Add Category" and define categories with descriptions
   - Example: "Newsletters" - "Marketing and promotional emails, newsletters, updates"
3. **Sync Emails**: Click "Sync Emails" to import and categorize your emails
4. **Browse Emails**: Click on a category to see emails sorted into it
5. **View Details**: Click on an email to read the full content
6. **Bulk Actions**:
   - Select emails using checkboxes
   - Click "Delete" to move to trash
   - Click "Unsubscribe" to automatically unsubscribe
7. **Multiple Accounts**: Click "+ Connect Account" to add more Gmail accounts

## How It Works

1. **Authentication**: Users sign in with Google OAuth and grant Gmail permissions
2. **Email Fetching**: The app fetches new emails using Gmail API
3. **AI Categorization**: Each email is sent to OpenAI with category descriptions
4. **AI Summarization**: OpenAI generates a concise summary of the email
5. **Auto-Archive**: Emails are archived in Gmail after being imported
6. **Storage**: Emails and summaries are stored in PostgreSQL
7. **Unsubscribe Agent**: Playwright-based bot navigates unsubscribe pages automatically

## API Endpoints

### Authentication
- `GET /auth/login` - Initiate Google OAuth
- `GET /auth/callback` - OAuth callback
- `POST /auth/connect-account` - Connect additional account

### Categories
- `GET /categories/` - List categories
- `POST /categories/` - Create category
- `GET /categories/{id}` - Get category
- `PUT /categories/{id}` - Update category
- `DELETE /categories/{id}` - Delete category

### Emails
- `GET /emails/category/{id}` - List emails in category
- `GET /emails/{id}` - Get email details
- `POST /emails/sync` - Sync new emails
- `POST /emails/bulk-action` - Bulk delete/unsubscribe
- `DELETE /emails/{id}` - Delete email

### Accounts
- `GET /accounts/` - List Gmail accounts
- `DELETE /accounts/{id}` - Disconnect account

## Security Considerations

- OAuth tokens are securely stored in the database
- JWT tokens are used for API authentication
- Passwords are never stored (using Google OAuth)
- API keys should be kept secret and not committed to version control
- The app requires specific Gmail API scopes for minimal permissions

## Limitations

- Google OAuth apps in development mode require test users to be added
- Unsubscribe feature may not work for all email types
- Some newsletters may not have standard unsubscribe links
- Rate limits apply to OpenAI and Gmail APIs

## Future Enhancements

- Email search functionality
- Category rules and filters
- Email scheduling and reminders
- Analytics and insights
- Mobile app
- Email templates and responses
- Integration with other email providers

## License

MIT License

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Author

Built for the Jump AI Hiring Challenge - October 2025
