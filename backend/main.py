#!/usr/bin/env python3
"""
Main FastAPI application for d42j infrastructure risk management platform.
"""
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from utils import ConfigLoader
from integrations import Device42Client, JiraClient
from services import RiskAssessmentEngine, ManufacturerAPIManager
from services.asset_correlator import AssetCorrelator
from models import Asset, AssetSummary, RiskAssessment, RiskLevel, AssetType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="d42j - Infrastructure Risk Management API",
    description="Device42 + Jira integration for infrastructure asset management and risk assessment",
    version="1.0.0"
)

# Global state
config_loader = None
asset_cache = {
    "assets": [],
    "assessments": [],
    "summary": None,
    "last_updated": None
}


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    version: str
    connections: Dict[str, bool]


class RefreshRequest(BaseModel):
    """Data refresh request."""
    force: bool = False


class SummaryResponse(BaseModel):
    """Summary statistics response."""
    summary: AssetSummary
    last_updated: datetime


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    global config_loader

    logger.info("Starting d42j API server...")

    # Load configuration
    config_path = Path(__file__).parent / "config.json"
    config_loader = ConfigLoader(str(config_path))

    try:
        config_loader.load()
        logger.info("Configuration loaded successfully")
    except FileNotFoundError as e:
        logger.error(str(e))
        logger.error("Please run 'python configure.py' first")
        raise

    # Configure CORS
    cors_origins = config_loader.get("server.cors_origins", ["*"])
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initial data load
    logger.info("Performing initial data load...")
    await refresh_data(background=False)

    logger.info("d42j API server started successfully")


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "name": "d42j - Infrastructure Risk Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with connection status."""
    connections = {
        "device42": False,
        "jira": False
    }

    # Test Device42 connection
    try:
        d42_config = config_loader.get("device42")
        d42_client = Device42Client(
            host=d42_config["host"],
            username=d42_config["username"],
            password=config_loader.get_decrypted("device42.password"),
            protocol=d42_config.get("protocol", "https"),
            port=d42_config.get("port", 443),
            verify_ssl=d42_config.get("verify_ssl", True)
        )
        connections["device42"] = d42_client.test_connection()
    except Exception as e:
        logger.error(f"Device42 health check failed: {e}")

    # Test Jira connection
    try:
        jira_config = config_loader.get("jira")
        jira_client = JiraClient(
            host=jira_config["host"],
            username=jira_config["username"],
            api_token=config_loader.get_decrypted("jira.api_token"),
            project_key=jira_config.get("project_key", "IT")
        )
        connections["jira"] = jira_client.test_connection()
    except Exception as e:
        logger.error(f"Jira health check failed: {e}")

    return HealthResponse(
        status="healthy" if all(connections.values()) else "degraded",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        connections=connections
    )


@app.post("/api/refresh")
async def refresh_data_endpoint(
    request: RefreshRequest,
    background_tasks: BackgroundTasks
):
    """Trigger data refresh from Device42 and Jira."""
    if request.force or not asset_cache.get("last_updated"):
        background_tasks.add_task(refresh_data, background=True)
        return {
            "status": "refresh_started",
            "message": "Data refresh initiated in background"
        }
    else:
        return {
            "status": "cached",
            "message": "Using cached data. Use force=true to refresh.",
            "last_updated": asset_cache["last_updated"]
        }


@app.get("/api/assets", response_model=List[Asset])
async def get_assets(
    asset_type: Optional[AssetType] = None,
    risk_level: Optional[RiskLevel] = None,
    jira_matched: Optional[bool] = None,
    min_age: Optional[float] = None,
    max_age: Optional[float] = None
):
    """
    Get all assets with optional filters.

    Args:
        asset_type: Filter by asset type
        risk_level: Filter by risk level
        jira_matched: Filter by Jira match status
        min_age: Minimum age in years
        max_age: Maximum age in years
    """
    assets = asset_cache.get("assets", [])

    # Apply filters
    if asset_type:
        assets = [a for a in assets if a.asset_type == asset_type]

    if risk_level:
        assets = [a for a in assets if a.risk_level == risk_level]

    if jira_matched is not None:
        assets = [a for a in assets if a.jira_matched == jira_matched]

    if min_age is not None:
        assets = [a for a in assets if a.age_years and a.age_years >= min_age]

    if max_age is not None:
        assets = [a for a in assets if a.age_years and a.age_years <= max_age]

    return assets


@app.get("/api/assets/{asset_id}", response_model=Asset)
async def get_asset(asset_id: str):
    """Get a specific asset by ID."""
    assets = asset_cache.get("assets", [])

    for asset in assets:
        if asset.id == asset_id:
            return asset

    raise HTTPException(status_code=404, detail="Asset not found")


@app.get("/api/assessments", response_model=List[RiskAssessment])
async def get_assessments(risk_level: Optional[RiskLevel] = None):
    """Get all risk assessments with optional risk level filter."""
    assessments = asset_cache.get("assessments", [])

    if risk_level:
        assessments = [a for a in assessments if a.risk_level == risk_level]

    return assessments


@app.get("/api/summary", response_model=AssetSummary)
async def get_summary():
    """Get summary statistics."""
    summary = asset_cache.get("summary")

    if not summary:
        raise HTTPException(status_code=503, detail="Data not yet loaded")

    return summary


@app.get("/api/critical-assets", response_model=List[Asset])
async def get_critical_assets():
    """Get assets with critical risk level."""
    assets = asset_cache.get("assets", [])
    return [a for a in assets if a.risk_level == RiskLevel.CRITICAL]


@app.get("/api/aging-assets", response_model=List[Asset])
async def get_aging_assets(threshold_years: float = 5.0):
    """Get assets older than specified threshold."""
    assets = asset_cache.get("assets", [])
    return [
        a for a in assets
        if a.age_years and a.age_years >= threshold_years
    ]


@app.get("/api/unsupported-assets", response_model=List[Asset])
async def get_unsupported_assets():
    """Get assets with expired or expiring support."""
    from models import SupportStatus

    assets = asset_cache.get("assets", [])
    return [
        a for a in assets
        if a.support_status in [SupportStatus.EXPIRED, SupportStatus.EXPIRING_SOON]
    ]


@app.get("/api/discrepancies")
async def get_discrepancies():
    """Get discrepancies between Device42 and Jira."""
    return asset_cache.get("discrepancies", {})


async def refresh_data(background: bool = False):
    """
    Refresh data from Device42, Jira, and manufacturer APIs.

    Args:
        background: Whether running in background
    """
    try:
        logger.info("Starting data refresh...")

        # Initialize clients
        d42_config = config_loader.get("device42")
        d42_client = Device42Client(
            host=d42_config["host"],
            username=d42_config["username"],
            password=config_loader.get_decrypted("device42.password"),
            protocol=d42_config.get("protocol", "https"),
            port=d42_config.get("port", 443),
            verify_ssl=d42_config.get("verify_ssl", True)
        )

        jira_config = config_loader.get("jira")
        jira_client = JiraClient(
            host=jira_config["host"],
            username=jira_config["username"],
            api_token=config_loader.get_decrypted("jira.api_token"),
            project_key=jira_config.get("project_key", "IT")
        )

        # Decrypt manufacturer API keys
        mfg_config = config_loader.get("manufacturers", {})
        decrypted_mfg_config = {}
        for vendor, cfg in mfg_config.items():
            if cfg.get("api_key"):
                decrypted_mfg_config[vendor] = {
                    "enabled": cfg.get("enabled", False),
                    "api_key": config_loader.get_decrypted(f"manufacturers.{vendor}.api_key")
                }
            else:
                decrypted_mfg_config[vendor] = cfg

        mfg_manager = ManufacturerAPIManager(decrypted_mfg_config)

        # Fetch assets from Device42
        logger.info("Fetching assets from Device42...")
        assets = d42_client.get_all_assets()
        logger.info(f"Retrieved {len(assets)} assets from Device42")

        # Fetch Jira asset register
        logger.info("Fetching assets from Jira...")
        jira_assets = jira_client.get_all_infrastructure_assets()
        logger.info(f"Retrieved {len(jira_assets)} assets from Jira")

        # Correlate assets
        logger.info("Correlating assets between Device42 and Jira...")
        correlator = AssetCorrelator()
        assets, unmatched = correlator.correlate_with_jira(assets, jira_assets)

        # Find discrepancies
        discrepancies = correlator.find_discrepancies(assets, jira_assets)
        asset_cache["discrepancies"] = discrepancies

        # Fetch incident data from Jira
        logger.info("Fetching incident history from Jira...")
        incident_data = {}
        for asset in assets:
            if asset.jira_matched:
                stats = jira_client.get_incident_history(asset.hostname)
                incident_data[asset.hostname] = stats

        assets = correlator.enrich_with_incident_data(assets, incident_data)

        # Fetch warranty data from manufacturers
        logger.info("Fetching warranty data from manufacturers...")
        warranty_data = mfg_manager.batch_get_warranty_info(assets)
        assets = correlator.enrich_with_warranty_data(assets, warranty_data)

        # Fetch EOL data from manufacturers
        logger.info("Fetching EOL data from manufacturers...")
        eol_data = mfg_manager.batch_get_eol_info(assets)
        assets = correlator.enrich_with_eol_data(assets, eol_data)

        # Perform risk assessment
        logger.info("Performing risk assessment...")
        risk_config = config_loader.get("risk_assessment", {})
        risk_engine = RiskAssessmentEngine(risk_config)

        # Build incident data dict for risk assessment
        incident_dict = {
            asset.hostname: incident_data.get(asset.hostname, {})
            for asset in assets
        }

        assessments = risk_engine.batch_assess_assets(
            assets,
            incident_data=incident_dict,
            eol_data=eol_data
        )

        # Calculate summary statistics
        summary = calculate_summary(assets)

        # Update cache
        asset_cache["assets"] = assets
        asset_cache["assessments"] = assessments
        asset_cache["summary"] = summary
        asset_cache["last_updated"] = datetime.utcnow()

        logger.info(
            f"Data refresh completed. "
            f"{len(assets)} assets, {len(assessments)} assessments"
        )

    except Exception as e:
        logger.error(f"Data refresh failed: {e}", exc_info=True)
        if not background:
            raise


def calculate_summary(assets: List[Asset]) -> AssetSummary:
    """Calculate summary statistics from assets."""
    by_type = {}
    for asset_type in AssetType:
        count = sum(1 for a in assets if a.asset_type == asset_type)
        if count > 0:
            by_type[asset_type] = count

    by_risk = {}
    for risk_level in RiskLevel:
        count = sum(1 for a in assets if a.risk_level == risk_level)
        if count > 0:
            by_risk[risk_level] = count

    ages = [a.age_years for a in assets if a.age_years is not None]
    avg_age = sum(ages) / len(ages) if ages else 0

    from models import SupportStatus

    expired_support = sum(
        1 for a in assets
        if a.support_status == SupportStatus.EXPIRED
    )

    critical_risk = sum(
        1 for a in assets
        if a.risk_level == RiskLevel.CRITICAL
    )

    jira_matched = sum(1 for a in assets if a.jira_matched)
    jira_unmatched = len(assets) - jira_matched

    return AssetSummary(
        total_assets=len(assets),
        by_type=by_type,
        by_risk_level=by_risk,
        avg_age_years=round(avg_age, 2),
        expired_support_count=expired_support,
        critical_risk_count=critical_risk,
        jira_matched_count=jira_matched,
        jira_unmatched_count=jira_unmatched
    )


if __name__ == "__main__":
    import uvicorn

    # Load server config
    config_loader = ConfigLoader("config.json")
    config_loader.load()

    server_config = config_loader.get("server", {})
    host = server_config.get("host", "0.0.0.0")
    port = server_config.get("port", 8000)

    logger.info(f"Starting server on {host}:{port}")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )
