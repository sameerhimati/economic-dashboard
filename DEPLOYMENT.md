# Economic Dashboard - Deployment Guide

## Overview

This guide covers deploying the Economic Dashboard application:
- **Backend**: FastAPI (Python) on Railway
- **Frontend**: React + TypeScript on Cloudflare Pages
- **Domain**: dash.itamih.com (Cloudflare DNS)

## Backend Deployment (Railway)

### Current Status
- Already deployed at: https://economic-dashboard-production.up.railway.app
- Auto-deploys from `main` branch
- PostgreSQL database provisioned

### Environment Variables (Railway)
```
DATABASE_URL=<provided by Railway PostgreSQL>
SECRET_KEY=<your-secret-key>
```

## Frontend Deployment (Cloudflare Pages)

### Prerequisites
1. Cloudflare account
2. Domain connected to Cloudflare (dash.itamih.com)
3. GitHub repository access

### Step 1: Build Verification
```bash
cd frontend
npm install
npm run build
```

Should produce a `dist/` directory with:
- index.html
- assets/ (CSS and JS bundles)

### Step 2: Deploy to Cloudflare Pages

#### Option A: Via Cloudflare Dashboard (Recommended)

1. **Login to Cloudflare Dashboard**
   - Go to https://dash.cloudflare.com
   - Navigate to Workers & Pages > Create application > Pages

2. **Connect Repository**
   - Select "Connect to Git"
   - Authorize GitHub access
   - Choose your repository: `economic-dashboard`

3. **Configure Build Settings**
   ```
   Project name: economic-dashboard
   Production branch: main
   Build command: cd frontend && npm install && npm run build
   Build output directory: frontend/dist
   Root directory: (leave empty)
   ```

4. **Environment Variables**
   Add the following variable:
   ```
   VITE_API_URL = https://economic-dashboard-production.up.railway.app
   ```

5. **Deploy**
   - Click "Save and Deploy"
   - Wait for build to complete (~2-3 minutes)
   - Your app will be available at a Cloudflare Pages URL

6. **Set up Custom Domain**
   - Go to your project > Custom domains
   - Click "Set up a custom domain"
   - Enter: `dash.itamih.com`
   - Cloudflare will automatically configure DNS
   - SSL certificate is automatically provisioned

#### Option B: Via Wrangler CLI

```bash
# Install Wrangler globally
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Build the project
cd frontend
npm install
npm run build

# Deploy
wrangler pages deploy dist --project-name=economic-dashboard

# Set environment variable
wrangler pages deployment tail --project-name=economic-dashboard
```

### Step 3: Configure Custom Domain

1. **In Cloudflare Dashboard**
   - Go to Pages project > Custom domains
   - Click "Set up a custom domain"
   - Enter: `dash.itamih.com`

2. **DNS Configuration** (Auto-configured by Cloudflare)
   ```
   Type: CNAME
   Name: dash
   Target: economic-dashboard.pages.dev
   Proxy: Yes (Orange cloud)
   ```

3. **SSL/TLS**
   - Go to SSL/TLS > Overview
   - Set encryption mode to "Full (strict)"
   - Certificate is auto-provisioned

### Step 4: Verify Deployment

1. **Check Build Logs**
   - In Cloudflare Pages > Deployments
   - Click on latest deployment
   - Review build logs for errors

2. **Test the Application**
   - Visit https://dash.itamih.com
   - Should see the login page
   - Register a new account
   - Verify dashboard loads

3. **Test API Connection**
   - Open browser DevTools > Network tab
   - Login with credentials
   - Verify API requests go to Railway backend
   - Check for CORS errors (should be none)

## Post-Deployment Checklist

### Frontend
- [ ] Build completes without errors
- [ ] Production bundle is optimized (<600KB)
- [ ] Environment variables are set
- [ ] Custom domain is configured
- [ ] SSL certificate is active
- [ ] CORS is working with backend

### Backend
- [ ] API is accessible at Railway URL
- [ ] Database migrations are applied
- [ ] CORS allows dash.itamih.com
- [ ] Authentication endpoints work
- [ ] Dashboard endpoints return data

### Full Stack
- [ ] User registration works
- [ ] User login works
- [ ] Protected routes redirect to login
- [ ] Dashboard loads data from API
- [ ] Logout works correctly
- [ ] Token persistence works
- [ ] Error handling works

## Troubleshooting

### Build Fails on Cloudflare

**Issue**: Build command fails
```bash
Error: Command failed with exit code 1
```

**Solution**:
- Check Node.js version (should be 18+)
- Verify `package.json` and `package-lock.json` are committed
- Check build logs for specific errors

### CORS Errors

**Issue**: API requests fail with CORS errors
```
Access to XMLHttpRequest blocked by CORS policy
```

**Solution**:
- Verify backend CORS configuration includes `dash.itamih.com`
- Check Railway environment variables
- Ensure HTTPS is used (not HTTP)

### API Connection Fails

**Issue**: Frontend can't connect to backend
```
Network Error / Failed to fetch
```

**Solution**:
- Verify `VITE_API_URL` environment variable
- Check Railway backend is running
- Test API directly: `curl https://economic-dashboard-production.up.railway.app/health`

### Authentication Not Working

**Issue**: Login succeeds but immediately logs out

**Solution**:
- Check browser localStorage for token
- Verify JWT token is valid
- Check backend `/auth/me` endpoint
- Review axios interceptors

### Custom Domain Not Working

**Issue**: dash.itamih.com not accessible

**Solution**:
- Wait for DNS propagation (up to 24 hours)
- Check DNS settings in Cloudflare
- Verify CNAME record points to Pages URL
- Check SSL/TLS encryption mode

## Updating the Application

### Frontend Updates
```bash
# Make changes to code
git add .
git commit -m "Update frontend"
git push origin main

# Cloudflare Pages auto-deploys from main branch
```

### Backend Updates
```bash
# Make changes to code
git add .
git commit -m "Update backend"
git push origin main

# Railway auto-deploys from main branch
```

## Monitoring

### Frontend (Cloudflare)
- Analytics: Cloudflare Pages > Analytics
- Build history: Cloudflare Pages > Deployments
- Real-time logs: `wrangler pages deployment tail`

### Backend (Railway)
- Logs: Railway project > Deployments > View logs
- Metrics: Railway project > Metrics
- Database: Railway project > PostgreSQL > Data

## Rollback

### Frontend Rollback
1. Go to Cloudflare Pages > Deployments
2. Find working deployment
3. Click "..." > Rollback to this deployment

### Backend Rollback
1. Go to Railway project > Deployments
2. Find working deployment
3. Click "Redeploy"

## Performance Optimization

### Frontend
- Enable Cloudflare caching for static assets
- Use Cloudflare CDN for global distribution
- Enable Brotli compression
- Set up Cloudflare Web Analytics

### Backend
- Enable Railway auto-scaling
- Add Redis for caching (optional)
- Monitor database query performance
- Set up database connection pooling

## Security

### Frontend
- HTTPS enforced by Cloudflare
- Environment variables hidden
- No secrets in client code
- CSP headers configured

### Backend
- HTTPS enforced by Railway
- Database credentials secure
- JWT tokens with expiration
- Rate limiting enabled
- Input validation on all endpoints

## Cost Estimate

### Cloudflare Pages
- Free tier: Unlimited requests
- Custom domain: Free
- SSL certificate: Free
- **Total: $0/month**

### Railway
- Free tier: 500 hours/month, $5 credit
- Hobby plan: $5/month
- PostgreSQL: Included
- **Total: $0-5/month**

### Domain (itamih.com)
- Varies by registrar
- ~$10-15/year

## Support

- Frontend issues: Check Cloudflare Pages logs
- Backend issues: Check Railway logs
- DNS issues: Check Cloudflare DNS settings
- General: Review application logs in browser DevTools
