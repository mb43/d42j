# Deployment Guide

This guide walks you through deploying the d42j platform in your environment.

## Architecture Overview

The d42j platform consists of two components:

1. **Backend API** - Python FastAPI service (runs on your internal network)
2. **Frontend Dashboard** - React static web app (hosted on GitHub Pages)

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────┐
│  GitHub Pages   │────────▶│   Backend API    │────────▶│  Device42   │
│   (Frontend)    │         │  (Internal Net)  │         └─────────────┘
└─────────────────┘         └──────────────────┘
                                     │
                                     │
                                     ▼
                            ┌─────────────────┐
                            │  Jira Service   │
                            │     Desk        │
                            └─────────────────┘
```

## Backend Deployment

### Prerequisites

- Linux server on your internal network (Ubuntu 20.04+ recommended)
- Python 3.9 or higher
- Access to Device42 instance
- Access to Jira ServiceDesk instance
- 2GB RAM minimum, 4GB recommended
- Network access to Device42 and Jira

### Step 1: Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv nginx -y

# Create application directory
sudo mkdir -p /opt/d42j
sudo chown $USER:$USER /opt/d42j
```

### Step 2: Clone and Setup Backend

```bash
# Clone repository
cd /opt/d42j
git clone <your-repo-url> .

# Create virtual environment
cd backend
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Configure Backend

```bash
# Run configuration wizard
python configure.py
```

The wizard will prompt for:
- Device42 hostname, credentials
- Jira URL, API token
- Risk assessment thresholds
- Manufacturer API keys (optional)

Configuration is saved to `backend/config.json` (not committed to git).

### Step 4: Test Backend

```bash
# Test the configuration
python main.py
```

Visit `http://localhost:8000/docs` to see the API documentation.

Press Ctrl+C to stop.

### Step 5: Setup as System Service

```bash
# Copy systemd service file
sudo cp deploy/d42j-api.service /etc/systemd/system/

# Edit service file to match your setup
sudo nano /etc/systemd/system/d42j-api.service

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable d42j-api
sudo systemctl start d42j-api

# Check status
sudo systemctl status d42j-api
```

### Step 6: Setup Nginx Reverse Proxy (Optional)

```bash
# Copy nginx configuration
sudo cp deploy/nginx.conf /etc/nginx/sites-available/d42j-api

# Edit configuration
sudo nano /etc/nginx/sites-available/d42j-api

# Enable site
sudo ln -s /etc/nginx/sites-available/d42j-api /etc/nginx/sites-enabled/

# Test and reload nginx
sudo nginx -t
sudo systemctl reload nginx
```

### Step 7: Configure Firewall

```bash
# Allow HTTP/HTTPS (if using nginx)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Or allow direct API access
sudo ufw allow 8000/tcp
```

## Frontend Deployment (GitHub Pages)

### Prerequisites

- Node.js 16+ and npm
- GitHub repository
- Access to your backend API from wherever you'll access the dashboard

### Step 1: Configure API Endpoint

```bash
cd frontend

# Create production environment file
cp .env.production.example .env.production

# Edit and set your backend API URL
nano .env.production
```

Set `REACT_APP_API_URL` to your backend API URL (e.g., `http://api-server.yourcompany.local:8000`)

### Step 2: Build Frontend

```bash
# Install dependencies
npm install

# Build for production
npm run build
```

The build output will be in `frontend/build/`.

### Step 3: Deploy to GitHub Pages

#### Option A: Using GitHub Actions (Recommended)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install and Build
        run: |
          cd frontend
          npm install
          npm run build

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./frontend/build
```

Then:
1. Push to GitHub
2. Go to repository Settings → Pages
3. Set source to `gh-pages` branch
4. Your site will be available at `https://yourusername.github.io/d42j/`

#### Option B: Manual Deployment

```bash
# Install gh-pages
npm install -g gh-pages

# Deploy
cd frontend
npm run build
gh-pages -d build
```

### Step 4: Update CORS in Backend

Update `backend/config.json` to include your GitHub Pages URL:

```json
{
  "server": {
    "cors_origins": [
      "http://localhost:3000",
      "https://yourusername.github.io"
    ]
  }
}
```

Restart the backend service:

```bash
sudo systemctl restart d42j-api
```

## Verification

### Backend Health Check

```bash
curl http://your-api-server:8000/health
```

Should return:
```json
{
  "status": "healthy",
  "connections": {
    "device42": true,
    "jira": true
  }
}
```

### Frontend Access

1. Navigate to your GitHub Pages URL
2. You should see the dashboard
3. Check browser console for any API connection errors

## Troubleshooting

### Backend Issues

**Service won't start:**
```bash
# Check logs
sudo journalctl -u d42j-api -f

# Check if port is in use
sudo netstat -tulpn | grep 8000
```

**API connection errors:**
- Verify Device42/Jira credentials in `config.json`
- Check network connectivity to Device42/Jira
- Review firewall rules

### Frontend Issues

**Cannot connect to API:**
- Check `REACT_APP_API_URL` in `.env.production`
- Verify CORS configuration in backend
- Check browser console for specific errors
- Ensure backend API is accessible from your network

**GitHub Pages not updating:**
- Check GitHub Actions logs
- Verify gh-pages branch exists
- Clear browser cache

## Maintenance

### Update Data Manually

```bash
curl -X POST http://your-api-server:8000/api/refresh -H "Content-Type: application/json" -d '{"force": true}'
```

### Scheduled Updates

Add to crontab:
```bash
# Refresh data every 6 hours
0 */6 * * * curl -X POST http://localhost:8000/api/refresh -d '{"force": true}'
```

### Backup Configuration

```bash
# Backup config (contains encrypted secrets)
sudo cp /opt/d42j/backend/config.json /opt/d42j/backend/config.json.backup
sudo cp /opt/d42j/backend/.encryption_key /opt/d42j/backend/.encryption_key.backup
```

### Update Application

```bash
cd /opt/d42j
git pull
cd backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart d42j-api
```

## Security Considerations

1. **Backend API** should only be accessible on your internal network
2. **Config files** contain encrypted credentials - protect them
3. **API endpoint** in frontend is visible to users - don't expose sensitive internal hostnames
4. **HTTPS** is recommended for production (use Let's Encrypt for free certificates)
5. **Firewall rules** should restrict backend access to authorized networks only

## Support

For issues or questions:
- Check logs: `sudo journalctl -u d42j-api -f`
- Review API docs: `http://your-api-server:8000/docs`
- Open GitHub issue with logs and error details
