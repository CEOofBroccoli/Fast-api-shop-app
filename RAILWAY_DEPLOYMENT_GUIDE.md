# Railway Integration Guide for Fast-API Shop App

## Prerequisites ✓

- [x] GitHub account (for connecting to Railway)
- [x] FastAPI app ready (your app is ready!)
- [x] Railway dockerfile created ✓
- [x] Railway configuration file created ✓

## Step-by-Step Integration

### Step 1: Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Sign up with your GitHub account (recommended for easy integration)

### Step 2: Prepare Your Repository

Before connecting to Railway, ensure your repository is properly set up:

```bash
# Make sure all files are committed to Git
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### Step 3: Create New Railway Project

1. In Railway dashboard, click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your `Fast-api-shop-app` repository
4. Railway will automatically detect the railway.dockerfile

### Step 4: Add Environment Variables

In your Railway project settings, add these environment variables:

**Required Variables:**

```
# Database (Railway will provide PostgreSQL)
DATABASE_URL=${PGDATABASE_URL}  # Railway auto-generates this

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-min-32-characters
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Configuration (optional - can skip for now)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com

# App Configuration
ENVIRONMENT=production
DEBUG=false
```

### Step 5: Add PostgreSQL Service

1. In your Railway project, click "New Service"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically create the database and set DATABASE_URL

### Step 6: Add Redis Service (Optional but Recommended)

1. Click "New Service" again
2. Select "Database" → "Redis"
3. Add this environment variable to your main service:
   ```
   REDIS_URL=${REDIS_URL}
   ```

### Step 7: Configure Domain (Optional)

1. In your service settings, go to "Settings"
2. Under "Domains", you can:
   - Use the auto-generated Railway domain (free)
   - Add a custom domain (if you have one)

### Step 8: Monitor Deployment

1. Check the "Deployments" tab to see build progress
2. View logs in real-time
3. Once deployed, test your API endpoints

## Post-Deployment Checklist

### Test Your Endpoints

Your app will be available at: `https://your-app-name.railway.app`

Test these endpoints:

- `GET /` - Health check
- `GET /docs` - API documentation
- `POST /api/auth/register` - User registration
- `GET /api/products` - Product listing

### Environment Variables Reference

Create a `.env.railway` file locally for reference (don't commit this):

```env
# Railway Environment Variables Template
DATABASE_URL=postgresql://username:password@host:port/database
REDIS_URL=redis://host:port
JWT_SECRET_KEY=your-super-secret-jwt-key-min-32-characters
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production
DEBUG=false
PORT=8000
```

## Troubleshooting Common Issues

### 1. Build Fails

- Check railway.dockerfile syntax
- Ensure all requirements.txt dependencies are compatible
- Check Railway logs for specific error messages

### 2. Database Connection Issues

- Verify DATABASE_URL is set correctly
- Check if PostgreSQL service is running
- Ensure alembic migrations run successfully

### 3. Memory Issues

- Railway free tier has 1GB RAM limit
- Our railway.dockerfile is optimized for this
- Monitor memory usage in Railway dashboard

### 4. Environment Variables

- Ensure all required variables are set
- Check variable names match exactly
- Verify sensitive values are properly escaped

## Next Steps After Deployment

1. **Set up monitoring**: Use Railway's built-in monitoring
2. **Configure custom domain**: If you have one
3. **Set up automated deployments**: Already configured via GitHub
4. **Add frontend**: Deploy your Jinja2 templates
5. **Performance optimization**: Monitor and adjust as needed

## Cost Optimization

**Railway Free Tier Limits:**

- 1GB RAM
- 1GB Storage
- 100GB Network
- No credit card required

**Upgrade Triggers:**

- If you exceed free tier limits
- Need more storage/bandwidth
- Want custom domains with SSL

Would you like me to help you with any specific step in this process?
