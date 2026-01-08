# Infrastructure Asset Management & Risk Assessment Platform

**d42j** - Device42 + Jira Integration for Infrastructure Risk Management

## Overview

A comprehensive infrastructure management platform that integrates Device42 CMDB, Jira ServiceDesk, and manufacturer data sources to provide real-time visibility into asset inventory, age, support status, and risk assessment.

## Features

- 📊 **Live Dashboard** - Real-time infrastructure visualization
- 🔄 **Multi-Source Integration** - Device42, Jira ServiceDesk, manufacturer APIs
- ⚠️ **Risk Assessment** - Industry-standard failure rate analysis
- 🏢 **Asset Coverage** - Servers (physical/virtual), network devices, storage
- 📈 **Age Analysis** - Track asset age against 7-year lifecycle policy
- 🔍 **Cross-Reference** - Match assets between Device42 and Jira
- 📄 **Management Reports** - Automated executive reporting
- 🔒 **Support Tracking** - Monitor software versions and support expiration

## Architecture

### Backend API Service
- Python-based REST API (FastAPI)
- Runs on internal network with access to Device42 and Jira
- Scheduled data synchronization
- Risk calculation engine
- Manufacturer API integration

### Frontend Dashboard
- React-based static web application
- Hosted on GitHub Pages
- Interactive visualizations
- Export capabilities
- Configurable API endpoint

## Quick Start

### 🪟 Windows Users (ZScaler/VPN Required)

**If you need ZScaler or VPN to access Device42/Jira**, see the complete Windows installation guide:

📘 **[INSTALL_WINDOWS.md](INSTALL_WINDOWS.md)** - Complete step-by-step guide from scratch

Or use these quick-start scripts after getting the code:
- `start-all.bat` - Start both backend and frontend
- `backend/setup-windows.bat` - First-time setup

### 🐧 Linux/Mac Users

### Prerequisites

- Python 3.9+
- Node.js 16+
- Access to Device42 instance
- Access to Jira ServiceDesk instance

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Run first-time configuration:
```bash
python configure.py
```

4. Start the API server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure API endpoint in `frontend/src/config.js`

4. For development:
```bash
npm start
```

5. For production build (GitHub Pages):
```bash
npm run build
```

## Configuration

### First Run

On first run, you'll be prompted to configure:

- **Device42 Settings**
  - Host/URL (e.g., rhmd42 or https://rhmd42.company.com)
  - API credentials

- **Jira Settings**
  - Host/URL (e.g., https://jira.company.com)
  - API token or credentials

- **Risk Assessment Thresholds**
  - Age thresholds (default: 7 years)
  - Failure rate models

### Configuration File

Settings are stored in `backend/config.json` (not committed to git):

```json
{
  "device42": {
    "host": "rhmd42",
    "username": "admin",
    "password": "encrypted"
  },
  "jira": {
    "host": "https://jira.company.com",
    "username": "admin",
    "api_token": "encrypted"
  },
  "risk_thresholds": {
    "max_age_years": 7,
    "failure_rate_model": "industry_standard"
  }
}
```

## API Documentation

Once the backend is running, API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Deployment

### Backend Deployment

Deploy the backend on a server within your internal network that has access to both Device42 and Jira:

```bash
# Using systemd service (recommended)
sudo cp backend/deploy/d42j-api.service /etc/systemd/system/
sudo systemctl enable d42j-api
sudo systemctl start d42j-api
```

### Frontend Deployment (GitHub Pages)

1. Build the frontend:
```bash
cd frontend
npm run build
```

2. The build output in `frontend/build/` is configured to deploy to GitHub Pages

3. Push to GitHub and enable GitHub Pages in repository settings

## Risk Assessment Methodology

The platform uses industry-standard hardware failure rate models:

- **Bathtub Curve Analysis** - Early life, useful life, wear-out phases
- **Age-Based Risk Scoring** - Exponential increase after 5 years
- **Support Status** - Critical risk for expired support/EOL
- **Incident History** - Weight based on Jira ticket patterns

### Risk Categories

- 🟢 **Low Risk** - < 3 years, active support
- 🟡 **Medium Risk** - 3-5 years, approaching EOL
- 🟠 **High Risk** - 5-7 years, limited support
- 🔴 **Critical Risk** - > 7 years, expired support

## Supported Manufacturers

The platform integrates with manufacturer APIs for:
- Dell (warranty and EOL data)
- HP/HPE (support status)
- Cisco (EoL announcements)
- Juniper (hardware lifecycle)
- NetApp (support contracts)
- VMware (product lifecycle)

## License

MIT License - See LICENSE file for details

## Support

For issues and feature requests, please open a GitHub issue.
