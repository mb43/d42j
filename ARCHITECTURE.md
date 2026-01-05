# d42j Platform Architecture

## System Overview

The d42j platform is a hybrid architecture combining a Python backend API with a React frontend, designed to provide real-time infrastructure risk assessment by integrating data from Device42 CMDB, Jira ServiceDesk, and manufacturer APIs.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Browser                              │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │           React Frontend (GitHub Pages)                     │ │
│  │  - Dashboard, Visualizations, Asset Lists, Reports          │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS/HTTP
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Backend API Server (Internal Network)               │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                  FastAPI Application                        │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │ │
│  │  │  API Routes  │  │  Services    │  │   Models     │    │ │
│  │  │  /assets     │  │  Risk Engine │  │   Asset      │    │ │
│  │  │  /summary    │  │  Correlator  │  │   Risk       │    │ │
│  │  │  /risk       │  │  Mfg APIs    │  │              │    │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │ │
│  └────────────────────────────────────────────────────────────┘ │
│            │              │              │                       │
│            ▼              ▼              ▼                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  Device42   │  │    Jira     │  │Manufacturer │            │
│  │  Client     │  │   Client    │  │  API Mgr    │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└──────┬──────────────────┬──────────────────┬───────────────────┘
       │                  │                  │
       ▼                  ▼                  ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Device42   │  │    Jira     │  │  Dell API   │
│   Server    │  │ ServiceDesk │  │  Cisco API  │
│   (CMDB)    │  │             │  │  HP API     │
└─────────────┘  └─────────────┘  └─────────────┘
```

## Component Details

### Frontend (React + Material-UI)

**Location:** `frontend/`

**Purpose:** Static web application providing user interface

**Key Features:**
- Dashboard with real-time statistics
- Interactive charts (Recharts)
- Asset filtering and searching
- Risk assessment visualization
- Discrepancy reporting
- Data export capabilities

**Technology Stack:**
- React 18
- Material-UI 5
- Recharts for visualizations
- Axios for API calls
- React Router for navigation

**Deployment:** GitHub Pages (or any static hosting)

### Backend API (Python FastAPI)

**Location:** `backend/`

**Purpose:** REST API service for data aggregation and risk assessment

**Key Components:**

#### 1. API Layer (`main.py`)
- FastAPI application
- RESTful endpoints
- CORS middleware
- Health checks
- Background task support

**Endpoints:**
- `GET /health` - System health check
- `GET /api/assets` - Retrieve assets (with filters)
- `GET /api/summary` - Summary statistics
- `GET /api/assessments` - Risk assessments
- `GET /api/discrepancies` - Data discrepancies
- `POST /api/refresh` - Trigger data refresh

#### 2. Integration Layer (`integrations/`)

**Device42Client:**
- Connects to Device42 API
- Retrieves physical servers, VMs, network devices, storage
- Parses device data into normalized Asset models
- Supports pagination and filtering

**JiraClient:**
- Connects to Jira ServiceDesk API
- Retrieves asset register from Jira
- Fetches incident/ticket history
- Calculates incident statistics

#### 3. Service Layer (`services/`)

**RiskAssessmentEngine:**
- Implements bathtub curve failure rate model
- Calculates age-based risk using industry AFR (Annual Failure Rate)
- Assesses support status risk
- Evaluates incident history patterns
- Combines multiple risk factors with weighted scoring
- Generates actionable recommendations

**Risk Model:**
```python
# Annual Failure Rates by Age
Year 0-1:  5%  AFR (infant mortality)
Year 1-3:  2%  AFR (stable period)
Year 3-5:  5%  AFR (early wear)
Year 5-7:  12% AFR (significant wear)
Year 7+:   20%+ AFR (critical risk)
```

**ManufacturerAPIManager:**
- Dell TechDirect API integration
- HPE Support API integration
- Cisco EoX (End of Life) API integration
- Warranty information retrieval
- EOL/EOS date tracking

**AssetCorrelator:**
- Matches assets between Device42 and Jira
- Fuzzy matching for hostname variations
- Enriches assets with incident data
- Enriches assets with warranty data
- Identifies discrepancies

#### 4. Data Models (`models/`)

**Asset Model:**
- Base asset with common attributes
- Specialized models: Server, NetworkDevice, StorageDevice
- Risk scoring fields
- Jira integration fields
- Support status tracking

**Risk Assessment Model:**
- Risk score (0-100)
- Risk level (low/medium/high/critical)
- Factor breakdown
- Recommendations list

#### 5. Utilities (`utils/`)

**ConfigLoader:**
- Loads JSON configuration
- Handles encrypted credentials
- Provides decryption for sensitive data

## Data Flow

### 1. Initial Data Load

```
Backend Startup
    │
    ├──▶ Load Config (encrypted credentials)
    │
    ├──▶ Connect to Device42
    │    └──▶ Fetch all devices (servers, network, storage)
    │         └──▶ Parse to Asset models
    │
    ├──▶ Connect to Jira
    │    ├──▶ Fetch asset register
    │    └──▶ Fetch incident history for each asset
    │
    ├──▶ Connect to Manufacturer APIs
    │    ├──▶ Batch fetch warranty data
    │    └──▶ Batch fetch EOL data
    │
    ├──▶ Correlate Assets
    │    ├──▶ Match Device42 ↔ Jira by hostname
    │    ├──▶ Enrich with incident data
    │    ├──▶ Enrich with warranty data
    │    └──▶ Enrich with EOL data
    │
    ├──▶ Risk Assessment
    │    └──▶ Calculate risk for each asset
    │         ├──▶ Age-based risk (failure rates)
    │         ├──▶ Support status risk
    │         ├──▶ Incident history risk
    │         └──▶ EOL risk
    │
    └──▶ Cache Results
         └──▶ Store in memory for fast API response
```

### 2. User Interaction

```
User opens Dashboard
    │
    ├──▶ Frontend loads from GitHub Pages
    │
    ├──▶ Calls Backend API /health
    │    └──▶ Displays connection status
    │
    ├──▶ Calls Backend API /api/summary
    │    └──▶ Renders dashboard statistics and charts
    │
    ├──▶ User navigates to Assets page
    │    └──▶ Calls /api/assets?filters
    │         └──▶ Renders filtered asset table
    │
    ├──▶ User navigates to Risk Assessment
    │    └──▶ Calls /api/assessments
    │         └──▶ Displays risk details and recommendations
    │
    └──▶ User views Discrepancies
         └──▶ Calls /api/discrepancies
              └──▶ Shows Device42 ↔ Jira mismatches
```

### 3. Data Refresh

```
Manual or Scheduled Refresh
    │
    ├──▶ POST /api/refresh (force=true)
    │
    └──▶ Background Task
         ├──▶ Re-fetch from Device42
         ├──▶ Re-fetch from Jira
         ├──▶ Re-fetch from Manufacturer APIs
         ├──▶ Re-correlate data
         ├──▶ Re-calculate risk assessments
         └──▶ Update cache
```

## Risk Assessment Algorithm

The risk assessment engine uses a weighted multi-factor model:

```python
Total Risk Score = (
    Age Factor          × 0.4 +
    Support Status      × 0.3 +
    Incident History    × 0.2 +
    Manufacturer EOL    × 0.1
)
```

### Age Factor (40% weight)
- Based on industry-standard bathtub curve
- Uses empirical AFR data from Backblaze, Google studies
- Accounts for infant mortality and wear-out phases
- Exponential increase after 5 years

### Support Status Factor (30% weight)
- Active support: Low risk
- Expiring soon (< 90 days): Medium risk
- Expired: High risk
- EOL announced: Critical risk

### Incident History Factor (20% weight)
- Incident rate per month
- Critical incident count
- Average resolution time
- Pattern recognition for recurring issues

### Manufacturer EOL Factor (10% weight)
- EOL announced: Medium risk
- EOL reached: High risk
- No security patches: Critical risk

## Security Architecture

### Credentials Storage
- Encrypted using Fernet (symmetric encryption)
- Encryption key stored separately from config
- Config and key have restricted file permissions (0600)

### API Security
- Backend should run on internal network only
- CORS configured to allow only specific frontend origins
- No authentication currently (assumes network-level security)
- Supports HTTPS via reverse proxy (nginx)

### Data Privacy
- No sensitive data stored permanently
- In-memory caching only
- API responses don't include credentials
- Manufacturer API keys encrypted at rest

## Scalability Considerations

### Current Design (Single Instance)
- In-memory caching
- Synchronous API calls
- Suitable for up to 10,000 assets

### Future Enhancements for Scale
- Redis for distributed caching
- Async API calls (aiohttp already included)
- Database backend for persistence
- Queue system for background jobs (Celery)
- Horizontal scaling with load balancer

## Configuration Management

### Backend Configuration (`config.json`)
```json
{
  "device42": { ... },
  "jira": { ... },
  "risk_assessment": {
    "max_age_years": 7,
    "age_thresholds": { ... },
    "weight_factors": { ... }
  },
  "manufacturers": { ... },
  "cache": { ... },
  "server": { ... }
}
```

### Frontend Configuration (`config.js`)
```javascript
{
  API_BASE_URL: process.env.REACT_APP_API_URL,
  RISK_COLORS: { ... },
  ASSET_TYPE_LABELS: { ... },
  AUTO_REFRESH_INTERVAL: 300000
}
```

## Error Handling

### Backend
- Try/catch blocks around all external API calls
- Logging via Python logging module
- Graceful degradation (missing manufacturer APIs don't break core functionality)
- Health endpoint reports connection status

### Frontend
- Axios interceptors for global error handling
- User-friendly error messages
- Fallback UI for failed API calls
- Retry logic for transient failures

## Performance Optimization

### Backend
- Batch API calls to external systems
- In-memory caching with configurable TTL
- Pagination for large result sets
- Lazy loading of detailed data

### Frontend
- Code splitting with React Router
- Lazy loading of charts
- Pagination of large tables
- Debounced search inputs

## Monitoring and Observability

### Logs
- Backend: Python logging to stdout (captured by systemd)
- API access logs
- Error tracking with stack traces

### Metrics (Future)
- API response times
- Cache hit rates
- External API latency
- Asset count trends

### Health Checks
- `/health` endpoint
- Device42 connection status
- Jira connection status
- Last successful data refresh timestamp

## Deployment Models

### Recommended: Hybrid
- **Frontend:** GitHub Pages (public)
- **Backend:** Internal server (private network)
- **Benefits:** Easy frontend updates, secure backend

### Alternative: Full Internal
- **Frontend:** Internal web server
- **Backend:** Internal server
- **Benefits:** Maximum security, no external dependencies

### Future: Cloud
- **Frontend:** Cloudflare Pages / Netlify
- **Backend:** AWS Lambda / Azure Functions
- **Benefits:** Scalability, high availability
