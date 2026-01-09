"""
Data models for infrastructure assets - Simplified for pydantic v1.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel


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
    manufacturer: str = ""
    model: str = ""
    serial_number: str = ""
    purchase_date: Optional[datetime]
    manufacture_date: Optional[datetime]
    age_years: Optional[float]
    os_name: str = ""
    os_version: str = ""
    location: str = ""
    ip_address: str = ""
    mac_address: str = ""

    # Risk assessment fields
    risk_score: float = 0.0
    risk_level: RiskLevel = RiskLevel.LOW
    risk_factors: dict = {}

    # Support and lifecycle
    support_status: SupportStatus = SupportStatus.UNKNOWN
    support_expiry_date: Optional[datetime]
    eol_date: Optional[datetime]
    eos_date: Optional[datetime]

    # Jira integration
    jira_asset_tag: str = ""
    jira_matched: bool = False
    jira_ticket_count: int = 0
    jira_critical_tickets: int = 0

    # Device42 specific
    device42_id: str = ""
    device42_url: str = ""

    # Additional metadata
    tags: list = []
    custom_fields: dict = {}
    last_updated: Optional[datetime]

    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True


class NetworkDevice(Asset):
    """Network device specific model."""
    ports_total: Optional[int]
    ports_used: Optional[int]
    firmware_version: str = ""
    management_ip: str = ""


class Server(Asset):
    """Server specific model."""
    cpu_count: Optional[int]
    cpu_model: str = ""
    ram_gb: Optional[int]
    storage_gb: Optional[int]
    virtual_host: str = ""
    is_virtual: bool = False


class StorageDevice(Asset):
    """Storage device specific model."""
    capacity_tb: Optional[float]
    used_tb: Optional[float]
    raid_type: str = ""
    disk_count: Optional[int]


class RiskAssessment(BaseModel):
    """Risk assessment result."""
    asset_id: str
    asset_name: str
    hostname: str
    risk_score: float
    risk_level: RiskLevel
    factors: dict
    recommendations: list
    assessed_at: Optional[datetime]

    class Config:
        use_enum_values = True


class AssetSummary(BaseModel):
    """Summary statistics for assets."""
    total_assets: int
    by_type: dict
    by_risk_level: dict
    avg_age_years: float
    expired_support_count: int
    critical_risk_count: int
    jira_matched_count: int
    jira_unmatched_count: int

    class Config:
        use_enum_values = True
