"""
Manufacturer API integrations for warranty, EOL, and support information.
"""
import requests
import logging
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class ManufacturerAPIBase(ABC):
    """Base class for manufacturer API integrations."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.session = requests.Session()

    @abstractmethod
    def get_warranty_info(self, serial_number: str) -> Optional[Dict[str, Any]]:
        """Get warranty information for a device."""
        pass

    @abstractmethod
    def get_eol_info(self, model: str) -> Optional[Dict[str, Any]]:
        """Get End of Life information for a model."""
        pass


class DellAPI(ManufacturerAPIBase):
    """
    Dell TechDirect API integration.
    API Documentation: https://techdirect.dell.com/portal/AboutAPIs.aspx
    """

    BASE_URL = "https://apigtwb2c.us.dell.com/PROD/sbil/eapi/v5"

    def get_warranty_info(self, serial_number: str) -> Optional[Dict[str, Any]]:
        """Get Dell warranty information by service tag."""
        if not self.api_key:
            logger.warning("Dell API key not configured")
            return None

        try:
            url = f"{self.BASE_URL}/asset-entitlements"
            headers = {
                "Accept": "application/json",
                "apikey": self.api_key
            }
            params = {"servicetags": serial_number}

            response = self.session.get(url, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()

            if not data:
                return None

            # Parse warranty data
            entitlements = data[0].get("entitlements", [])

            warranty_info = {
                "serial_number": serial_number,
                "manufacturer": "Dell",
                "ship_date": data[0].get("shipDate"),
                "warranty_active": any(e.get("entitlementType") == "ACTIVE" for e in entitlements),
                "warranty_end_date": None,
                "support_type": None
            }

            # Find latest warranty end date
            for entitlement in entitlements:
                end_date = entitlement.get("endDate")
                if end_date:
                    if not warranty_info["warranty_end_date"] or end_date > warranty_info["warranty_end_date"]:
                        warranty_info["warranty_end_date"] = end_date
                        warranty_info["support_type"] = entitlement.get("serviceLevelDescription")

            logger.info(f"Retrieved Dell warranty info for {serial_number}")
            return warranty_info

        except requests.exceptions.RequestException as e:
            logger.error(f"Dell API request failed: {e}")
            return None

    def get_eol_info(self, model: str) -> Optional[Dict[str, Any]]:
        """
        Get EOL information for Dell model.
        Note: Dell doesn't have a public EOL API, this would need to be
        maintained manually or scraped from Dell's EOL pages.
        """
        # Placeholder - would need manual database or web scraping
        logger.info(f"Dell EOL info for {model} - manual database required")
        return None


class HPEAPI(ManufacturerAPIBase):
    """
    HPE Support API integration.
    Note: HPE requires OAuth authentication
    """

    BASE_URL = "https://api.hpe.com/support"

    def get_warranty_info(self, serial_number: str) -> Optional[Dict[str, Any]]:
        """Get HPE warranty information."""
        if not self.api_key:
            logger.warning("HPE API key not configured")
            return None

        try:
            # Note: Actual implementation would require OAuth flow
            # This is a simplified version
            url = f"{self.BASE_URL}/warranty/v1/serial/{serial_number}"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json"
            }

            response = self.session.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()

            warranty_info = {
                "serial_number": serial_number,
                "manufacturer": "HPE",
                "warranty_active": data.get("warrantyStatus") == "Active",
                "warranty_end_date": data.get("warrantyEndDate"),
                "support_type": data.get("serviceLevel")
            }

            logger.info(f"Retrieved HPE warranty info for {serial_number}")
            return warranty_info

        except requests.exceptions.RequestException as e:
            logger.error(f"HPE API request failed: {e}")
            return None

    def get_eol_info(self, model: str) -> Optional[Dict[str, Any]]:
        """Get HPE EOL information."""
        # Placeholder - would need manual database
        logger.info(f"HPE EOL info for {model} - manual database required")
        return None


class CiscoAPI(ManufacturerAPIBase):
    """
    Cisco Support API integration.
    API Documentation: https://developer.cisco.com/docs/support-apis/
    """

    BASE_URL = "https://api.cisco.com/supporttools/eox/rest/5"

    def get_warranty_info(self, serial_number: str) -> Optional[Dict[str, Any]]:
        """Get Cisco warranty/coverage information."""
        if not self.api_key:
            logger.warning("Cisco API key not configured")
            return None

        try:
            # Cisco uses serial number coverage check
            url = f"{self.BASE_URL}/coverage/status/serial_numbers/{serial_number}"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json"
            }

            response = self.session.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()

            # Parse response
            coverage = data.get("serial_numbers", [{}])[0]

            warranty_info = {
                "serial_number": serial_number,
                "manufacturer": "Cisco",
                "warranty_active": coverage.get("is_covered", False),
                "warranty_end_date": coverage.get("warranty_end_date"),
                "support_type": coverage.get("service_contract_number")
            }

            logger.info(f"Retrieved Cisco warranty info for {serial_number}")
            return warranty_info

        except requests.exceptions.RequestException as e:
            logger.error(f"Cisco API request failed: {e}")
            return None

    def get_eol_info(self, model: str) -> Optional[Dict[str, Any]]:
        """Get Cisco End of Life information."""
        if not self.api_key:
            logger.warning("Cisco API key not configured")
            return None

        try:
            # Cisco EOL API endpoint
            url = f"{self.BASE_URL}/EOXByProductID/1/{model}"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json"
            }

            response = self.session.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()

            eox_records = data.get("EOXRecord", [])
            if not eox_records:
                return None

            eox = eox_records[0]

            # Parse EOL dates
            eol_date = eox.get("EndOfSaleDate", {}).get("value")
            eos_date = eox.get("EndOfSWMaintenanceReleases", {}).get("value")
            eol_support = eox.get("LastDateOfSupport", {}).get("value")

            eol_info = {
                "model": model,
                "manufacturer": "Cisco",
                "is_eol": bool(eol_date),
                "eol_date": eol_date,
                "eos_date": eos_date,
                "end_of_support_date": eol_support,
                "eol_announced": bool(eox.get("EOLProductID")),
                "replacement_product": eox.get("MigrationProductId")
            }

            # Calculate months until EOL
            if eol_support:
                try:
                    eol_dt = datetime.strptime(eol_support, "%Y-%m-%d")
                    months_until = (eol_dt - datetime.now()).days / 30
                    eol_info["months_until_eol"] = max(0, int(months_until))
                except ValueError:
                    pass

            logger.info(f"Retrieved Cisco EOL info for {model}")
            return eol_info

        except requests.exceptions.RequestException as e:
            logger.error(f"Cisco API request failed: {e}")
            return None


class ManufacturerAPIManager:
    """Manager for all manufacturer API integrations."""

    def __init__(self, config: Dict[str, Dict]):
        """
        Initialize manufacturer API manager.

        Args:
            config: Dictionary of manufacturer configs with api_key and enabled status
        """
        self.apis = {}

        # Initialize configured APIs
        if config.get("dell", {}).get("enabled"):
            self.apis["dell"] = DellAPI(config["dell"].get("api_key"))

        if config.get("hp", {}).get("enabled") or config.get("hpe", {}).get("enabled"):
            api_key = config.get("hp", {}).get("api_key") or config.get("hpe", {}).get("api_key")
            self.apis["hpe"] = HPEAPI(api_key)
            self.apis["hp"] = self.apis["hpe"]  # Alias

        if config.get("cisco", {}).get("enabled"):
            self.apis["cisco"] = CiscoAPI(config["cisco"].get("api_key"))

        logger.info(f"Initialized manufacturer APIs: {list(self.apis.keys())}")

    def get_warranty_info(self, manufacturer: str,
                         serial_number: str) -> Optional[Dict[str, Any]]:
        """Get warranty information from appropriate manufacturer API."""
        manufacturer_key = manufacturer.lower()

        if manufacturer_key not in self.apis:
            logger.debug(f"No API configured for manufacturer: {manufacturer}")
            return None

        return self.apis[manufacturer_key].get_warranty_info(serial_number)

    def get_eol_info(self, manufacturer: str, model: str) -> Optional[Dict[str, Any]]:
        """Get EOL information from appropriate manufacturer API."""
        manufacturer_key = manufacturer.lower()

        if manufacturer_key not in self.apis:
            logger.debug(f"No API configured for manufacturer: {manufacturer}")
            return None

        return self.apis[manufacturer_key].get_eol_info(model)

    def batch_get_warranty_info(self, assets: list) -> Dict[str, Dict]:
        """
        Get warranty information for multiple assets.

        Returns:
            Dict mapping serial_number to warranty info
        """
        warranty_data = {}

        for asset in assets:
            if not asset.manufacturer or not asset.serial_number:
                continue

            info = self.get_warranty_info(asset.manufacturer, asset.serial_number)
            if info:
                warranty_data[asset.serial_number] = info

        return warranty_data

    def batch_get_eol_info(self, assets: list) -> Dict[str, Dict]:
        """
        Get EOL information for multiple assets.

        Returns:
            Dict mapping model to EOL info
        """
        eol_data = {}
        models_checked = set()

        for asset in assets:
            if not asset.manufacturer or not asset.model:
                continue

            # Avoid duplicate API calls for same model
            if asset.model in models_checked:
                continue

            info = self.get_eol_info(asset.manufacturer, asset.model)
            if info:
                eol_data[asset.model] = info
                models_checked.add(asset.model)

        return eol_data
