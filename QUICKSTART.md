# Quick Start Guide

Get the d42j platform up and running in 15 minutes.

## Prerequisites

- Python 3.9+
- Node.js 16+
- Access to Device42 (hostname: rhmd42 or your instance)
- Access to Jira ServiceDesk

## Backend Setup (5 minutes)

```bash
# 1. Clone repository
git clone <your-repo-url>
cd d42j/backend

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure
python configure.py
```

Follow the prompts to enter:
- Device42 host (default: rhmd42)
- Device42 credentials
- Jira URL
- Jira API token
- Risk thresholds (accept defaults)

```bash
# 5. Start server
python main.py
```

Server runs at `http://localhost:8000`

Visit `http://localhost:8000/docs` for API documentation.

## Frontend Setup (5 minutes)

Open a new terminal:

```bash
cd d42j/frontend

# 1. Install dependencies
npm install

# 2. Configure API endpoint
# Edit src/config.js and set API_BASE_URL if needed
# Default is http://localhost:8000

# 3. Start development server
npm start
```

Frontend opens at `http://localhost:3000`

## First Use (5 minutes)

1. **Dashboard** - View summary statistics and risk distribution
2. **All Assets** - Browse and filter your infrastructure assets
3. **Risk Assessment** - Review detailed risk analysis and recommendations
4. **Discrepancies** - Check for mismatches between Device42 and Jira

## Key Features to Try

### 1. Filter Critical Risk Assets
- Go to "All Assets"
- Set Risk Level filter to "Critical"
- Review assets needing immediate attention

### 2. Review Age Distribution
- Dashboard shows average infrastructure age
- Look for assets over 7 years old
- Review recommendations in Risk Assessment page

### 3. Check Jira Integration
- Dashboard shows Jira match statistics
- Go to Discrepancies to see unmatched assets
- Export discrepancies as CSV

### 4. Refresh Data
- Click Refresh icon in top-right
- Data updates from Device42 and Jira
- Takes 1-5 minutes depending on asset count

## Next Steps

1. **Customize Risk Thresholds**
   - Edit `backend/config.json`
   - Adjust `risk_assessment.age_thresholds`
   - Restart backend: `python main.py`

2. **Add Manufacturer APIs**
   - Get API keys from Dell, Cisco, HP
   - Run `python configure.py` again
   - Select manufacturer integrations

3. **Deploy to Production**
   - See [DEPLOYMENT.md](DEPLOYMENT.md)
   - Backend: systemd service on internal server
   - Frontend: GitHub Pages for easy access

## Troubleshooting

**Backend won't start:**
```bash
# Check config file exists
ls -la backend/config.json

# Check Python version
python3 --version  # Should be 3.9+

# Check logs
python main.py  # Look for error messages
```

**Frontend can't connect:**
```bash
# Check backend is running
curl http://localhost:8000/health

# Check CORS in backend/config.json
# Should include "http://localhost:3000"

# Check browser console for errors
# Press F12 → Console tab
```

**No data showing:**
```bash
# Check Device42 connection
curl http://localhost:8000/health
# Should show device42: true

# Check Jira connection
# Should show jira: true

# Trigger manual refresh
curl -X POST http://localhost:8000/api/refresh -d '{"force": true}'
```

## Support

- Full documentation: [README.md](README.md)
- Deployment guide: [DEPLOYMENT.md](DEPLOYMENT.md)
- Architecture details: [ARCHITECTURE.md](ARCHITECTURE.md)
- API docs: `http://localhost:8000/docs`

## Example Output

After successful setup, your dashboard should show:
- Total asset count from Device42
- Risk distribution chart
- Critical risk count
- Average infrastructure age
- Jira match percentage

If you see these metrics, you're all set! 🎉
