# Deployment Guide

This guide covers deploying the AI Email Sorter to production.

## Prerequisites

1. Google Cloud Project with OAuth configured
2. OpenAI API key
3. PostgreSQL database
4. Hosting platform account (Render, Fly.io, or similar)

## Option 1: Deploy to Render (Recommended)

Render provides easy deployment with the included `render.yaml` configuration.

### Steps:

1. **Create a Render account** at https://render.com

2. **Fork/Push this repository to GitHub**

3. **Connect Render to your GitHub repository**
   - Go to Render Dashboard
   - Click "New" → "Blueprint"
   - Connect your repository
   - Render will automatically detect the `render.yaml`

4. **Set Environment Variables**
   
   For the backend service, add these in Render Dashboard:
   - `GOOGLE_CLIENT_ID`: Your Google OAuth Client ID
   - `GOOGLE_CLIENT_SECRET`: Your Google OAuth Client Secret
   - `OPENAI_API_KEY`: Your OpenAI API key
   
   Other variables are auto-configured by Render.

5. **Update OAuth Redirect URIs**
   
   In Google Cloud Console, add:
   - `https://your-backend-url.onrender.com/auth/callback`
   
   Replace `your-backend-url` with your actual Render URL.

6. **Add Test User**
   
   In Google Cloud Console OAuth consent screen:
   - Add `webshookeng@gmail.com` as a test user

7. **Deploy**
   
   Render will automatically:
   - Create PostgreSQL database
   - Create Redis instance
   - Deploy backend
   - Deploy frontend
   - Connect all services

8. **Verify Deployment**
   
   Visit your frontend URL and test the login flow.

### Render Configuration Details

The `render.yaml` includes:
- **Backend**: Python web service with auto-scaling
- **Frontend**: Static site with optimized build
- **Database**: PostgreSQL with automatic backups
- **Redis**: For background tasks

## Option 2: Deploy to Fly.io

### Prerequisites:
- Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
- Create account: `fly auth signup`

### Deploy Backend:

```bash
# Login
fly auth login

# Create and deploy backend
cd backend
fly launch --name email-sorter-backend --region sea

# Set secrets
fly secrets set \
  SECRET_KEY=$(openssl rand -hex 32) \
  GOOGLE_CLIENT_ID=your-client-id \
  GOOGLE_CLIENT_SECRET=your-client-secret \
  OPENAI_API_KEY=your-openai-key

# Create PostgreSQL database
fly postgres create --name email-sorter-db --region sea
fly postgres attach email-sorter-db

# Create Redis
fly redis create --name email-sorter-redis --region sea
fly redis attach email-sorter-redis

# Deploy
fly deploy
```

### Deploy Frontend:

```bash
cd frontend

# Create app
fly launch --name email-sorter-frontend --region sea

# Set environment
fly secrets set REACT_APP_API_URL=https://email-sorter-backend.fly.dev

# Deploy
fly deploy
```

## Option 3: Deploy with Docker

### Using Docker Compose (Local/VPS):

```bash
# Clone repository
git clone <your-repo>
cd jump-ai-email-sorter

# Create .env file
cat > .env << EOF
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
OPENAI_API_KEY=your-openai-key
EOF

# Build and start services
docker-compose up -d

# Check logs
docker-compose logs -f
```

### Manual Docker Deployment:

```bash
# Build images
docker build -f Dockerfile.backend -t email-sorter-backend .
docker build -f Dockerfile.frontend -t email-sorter-frontend .

# Run PostgreSQL
docker run -d --name postgres \
  -e POSTGRES_USER=email_sorter \
  -e POSTGRES_PASSWORD=secure_password \
  -e POSTGRES_DB=email_sorter \
  -p 5432:5432 \
  postgres:15

# Run Redis
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Run Backend
docker run -d --name backend \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://email_sorter:secure_password@postgres:5432/email_sorter \
  -e SECRET_KEY=$(openssl rand -hex 32) \
  -e GOOGLE_CLIENT_ID=your-client-id \
  -e GOOGLE_CLIENT_SECRET=your-client-secret \
  -e OPENAI_API_KEY=your-openai-key \
  -e REDIS_URL=redis://redis:6379 \
  -e FRONTEND_URL=http://your-domain.com \
  -e BACKEND_URL=http://api.your-domain.com \
  --link postgres:postgres \
  --link redis:redis \
  email-sorter-backend

# Run Frontend
docker run -d --name frontend \
  -p 3000:80 \
  -e REACT_APP_API_URL=http://api.your-domain.com \
  --link backend:backend \
  email-sorter-frontend
```

## Option 4: Deploy to AWS/GCP/Azure

### General Steps:

1. **Database Setup**
   - Create managed PostgreSQL instance
   - Create managed Redis instance
   - Note connection strings

2. **Backend Deployment**
   - Deploy using Elastic Beanstalk (AWS), App Engine (GCP), or App Service (Azure)
   - Set environment variables
   - Configure auto-scaling

3. **Frontend Deployment**
   - Build: `cd frontend && npm run build`
   - Upload to S3 (AWS), Cloud Storage (GCP), or Blob Storage (Azure)
   - Configure CDN (CloudFront, Cloud CDN, Azure CDN)

4. **Domain & SSL**
   - Configure custom domain
   - Enable HTTPS/SSL
   - Update OAuth redirect URIs

## Post-Deployment Checklist

- [ ] Test login flow
- [ ] Verify email sync works
- [ ] Test category creation
- [ ] Test AI categorization
- [ ] Test AI summarization
- [ ] Test bulk delete
- [ ] Test unsubscribe feature
- [ ] Check error logging
- [ ] Monitor performance
- [ ] Set up backups
- [ ] Configure monitoring/alerts

## Environment Variables Reference

### Backend Required:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret (generate with `openssl rand -hex 32`)
- `GOOGLE_CLIENT_ID`: From Google Cloud Console
- `GOOGLE_CLIENT_SECRET`: From Google Cloud Console
- `OPENAI_API_KEY`: From OpenAI dashboard
- `REDIS_URL`: Redis connection string
- `FRONTEND_URL`: Frontend URL (for CORS)
- `BACKEND_URL`: Backend URL (for OAuth callback)

### Frontend Required:
- `REACT_APP_API_URL`: Backend API URL

## OAuth Configuration

### Google Cloud Console:

1. Go to https://console.cloud.google.com/
2. Select your project
3. Navigate to "APIs & Services" → "Credentials"
4. Edit OAuth 2.0 Client ID
5. Add Authorized redirect URIs:
   - Production: `https://your-backend.com/auth/callback`
   - Development: `http://localhost:8000/auth/callback`
6. Save changes

### Add Test Users:

1. Go to "OAuth consent screen"
2. Under "Test users", click "Add Users"
3. Add: `webshookeng@gmail.com`
4. Add any other test users you need

## Monitoring & Maintenance

### Logs:
- **Render**: View in dashboard
- **Fly.io**: `fly logs`
- **Docker**: `docker-compose logs -f`

### Database Backups:
- Render: Automatic daily backups
- Fly.io: `fly postgres backup`
- Manual: `pg_dump` scheduled via cron

### Updates:
```bash
# Pull latest changes
git pull origin main

# Rebuild and redeploy
# Render: Automatic on git push
# Fly.io: fly deploy
# Docker: docker-compose up -d --build
```

## Troubleshooting

### OAuth Errors:
- Verify redirect URIs match exactly
- Check test users are added
- Ensure scopes are correct

### Database Connection:
- Verify DATABASE_URL format
- Check firewall rules
- Test connection: `psql $DATABASE_URL`

### Email Sync Issues:
- Check Gmail API quotas
- Verify OAuth scopes
- Check token expiration

### AI Features Not Working:
- Verify OpenAI API key
- Check API quotas/credits
- Review error logs

### Unsubscribe Failing:
- Check Playwright installation
- Verify browser dependencies
- Review page-specific logs

## Security Best Practices

1. **Never commit secrets** to git
2. **Use environment variables** for all credentials
3. **Enable HTTPS** in production
4. **Rotate secrets** regularly
5. **Monitor API usage** for anomalies
6. **Keep dependencies updated**
7. **Enable database backups**
8. **Use strong JWT secrets**
9. **Implement rate limiting** (production)
10. **Regular security audits**

## Scaling Considerations

### For High Traffic:

1. **Backend Scaling**:
   - Increase worker processes
   - Add more instances
   - Use load balancer

2. **Database**:
   - Add read replicas
   - Implement connection pooling
   - Add caching layer

3. **Background Jobs**:
   - Use Celery with Redis
   - Separate worker instances
   - Queue email processing

4. **Frontend**:
   - Use CDN
   - Enable caching
   - Optimize bundle size

## Cost Estimation

### Render (Recommended for MVP):
- Backend: $7-25/month
- Frontend: Free (static site)
- Database: $7-20/month
- Redis: $3-10/month
- **Total: ~$20-60/month**

### Fly.io:
- Backend: $5-30/month
- Frontend: $5-20/month
- Database: $15-50/month
- Redis: $5-15/month
- **Total: ~$30-115/month**

### AWS/GCP/Azure:
- Varies based on usage
- **Estimate: $50-200/month**

## Support

For deployment issues:
1. Check application logs
2. Review this guide
3. Check platform documentation
4. Open GitHub issue with details

