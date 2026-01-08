"""
Data models for infrastructure assets.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel
try:
    from pydantic import Field
except ImportError:
    Field = None  # pydantic v1 compatibility


class AssetType(str, Enum):
    """Asset type enumeration."""
    PHYSICAL_SERVER = "physical_server"
    VIRTUAL_SERVER = "virtual_server"
    NETWORK_SWITCH = "network_switch"
    ROUTER = "router"
    FIREWALL = "firewall"
    ACCESS_POINT = "access_point"
    STORAGE_DEVICE = "storage_device"
    HYPERVISOR = "hypervisor"


class RiskLevel(str, Enum):
    """Risk level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SupportStatus(str, Enum):
    """Support status enumeration."""
    ACTIVE = "active"
    EXPIRED = "expired"
    EXPIRING_SOON = "expiring_soon"
    UNKNOWN = "unknown"


class Asset(BaseModel):
    """Base asset model."""
    id: str
    name: str
    hostname: str
    asset_type: AssetType
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    purchase_date: Optional[datetime] = None
    manufacture_date: Optional[datetime] = None
    age_years: Optional[float] = None
    os_name: Optional[str] = None
    os_version: Optional[str] = None
    location: Optional[str] = None
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None

    # Risk assessment fields
    risk_score: float = 0.0
    risk_level: RiskLevel = RiskLevel.LOW
    risk_factors: Dict[str, Any] = {}

    # Support and lifecycle
    support_status: SupportStatus = SupportStatus.UNKNOWN
    support_expiry_date: Optional[datetime] = None
    eol_date: Optional[datetime] = None
    eos_date: Optional[datetime] = None

    # Jira integration
    jira_asset_tag: Optional[str] = None
    jira_matched: bool = False
    jira_ticket_count: int = 0
    jira_critical_tickets: int = 0

    # Device42 specific
    device42_id: Optional[str] = None
    device42_url: Optional[str] = None

    # Additional metadata
    tags: List[str] = []
    custom_fields: Dict[str, Any] = {}
    last_updated: datetime = None

    def __init__(self, **data):
        if 'last_updated' not in data or data['last_updated'] is None:
            data['last_updated'] = datetime.utcnow()
        if 'risk_factors' not in data:
            data['risk_factors'] = {}
        if 'tags' not in data:
            data['tags'] = []
        if 'custom_fields' not in data:
            data['custom_fields'] = {}
        super().__init__(**data)


class NetworkDevice(Asset):
    """Network device specific model."""
    ports_total: Optional[int] = None
    ports_used: Optional[int] = None
    firmware_version: Optional[str] = None
    management_ip: Optional[str] = None


class Server(Asset):
    """Server specific model."""
    cpu_count: Optional[int] = None
    cpu_model: Optional[str] = None
    ram_gb: Optional[int] = None
    storage_gb: Optional[int] = None
    virtual_host: Optional[str] = None
    is_virtual: bool = False


class StorageDevice(Asset):
    """Storage device specific model."""
    capacity_tb: Optional[float] = None
    used_tb: Optional[float] = None
    raid_type: Optional[str] = None
    disk_count: Optional[int] = None


class RiskAssessment(BaseModel):
    """Risk assessment result."""
    asset_id: str
    asset_name: str
    hostname: str
    risk_score: float
    risk_level: RiskLevel
    factors: Dict[str, float]
    recommendations: List[str]
    assessed_at: datetime = None

    def __init__(self, **data):
        if 'assessed_at' not in data or data['assessed_at'] is None:
            data['assessed_at'] = datetime.utcnow()
        super().__init__(**data)


class AssetSummary(BaseModel):
    """Summary statistics for assets."""
    total_assets: int
    by_type: Dict[AssetType, int]
    by_risk_level: Dict[RiskLevel, int]
    avg_age_years: float
    expired_support_count: int
    critical_risk_count: int
    jira_matched_count: int
    jira_unmatched_count: int
