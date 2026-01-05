"""
Device42 API client for retrieving infrastructure inventory.
"""
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from urllib.parse import urljoin

from models import Asset, AssetType, Server, NetworkDevice, StorageDevice

logger = logging.getLogger(__name__)


class Device42Client:
    """Client for interacting with Device42 API."""

    def __init__(self, host: str, username: str, password: str,
                 protocol: str = "https", port: int = 443,
                 verify_ssl: bool = True):
        """
        Initialize Device42 client.

        Args:
            host: Device42 hostname or IP
            username: API username
            password: API password
            protocol: http or https
            port: API port
            verify_ssl: Whether to verify SSL certificates
        """
        self.base_url = f"{protocol}://{host}:{port}/api/1.0/"
        self.auth = (username, password)
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.session.verify = verify_ssl

        if not verify_ssl:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a GET request to Device42 API."""
        url = urljoin(self.base_url, endpoint)
        try:
            response = self.session.get(url, auth=self.auth, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Device42 API request failed: {e}")
            raise

    def get_all_devices(self) -> List[Dict[str, Any]]:
        """Retrieve all devices from Device42."""
        devices = []
        offset = 0
        limit = 100

        while True:
            params = {"offset": offset, "limit": limit}
            response = self._get("devices/all/", params)

            batch = response.get("Devices", [])
            devices.extend(batch)

            if len(batch) < limit:
                break

            offset += limit

        logger.info(f"Retrieved {len(devices)} devices from Device42")
        return devices

    def get_physical_servers(self) -> List[Dict[str, Any]]:
        """Retrieve physical servers."""
        params = {"type": "physical"}
        response = self._get("devices/all/", params)
        return response.get("Devices", [])

    def get_virtual_machines(self) -> List[Dict[str, Any]]:
        """Retrieve virtual machines."""
        response = self._get("devices/vms/")
        return response.get("vms", [])

    def get_network_devices(self) -> List[Dict[str, Any]]:
        """Retrieve network devices (switches, routers, firewalls)."""
        devices = []

        # Get switches
        response = self._get("assets/switches/")
        devices.extend(response.get("switches", []))

        # Get routers (often categorized as devices with specific types)
        params = {"category": "network"}
        response = self._get("devices/all/", params)
        devices.extend(response.get("Devices", []))

        return devices

    def get_storage_devices(self) -> List[Dict[str, Any]]:
        """Retrieve storage devices."""
        params = {"category": "storage"}
        response = self._get("devices/all/", params)
        return response.get("Devices", [])

    def get_software_in_use(self, device_id: str) -> List[Dict[str, Any]]:
        """Get software installed on a specific device."""
        params = {"device_id": device_id}
        response = self._get("software/", params)
        return response.get("software", [])

    def get_device_lifecycle(self, device_id: str) -> Dict[str, Any]:
        """Get lifecycle information for a device."""
        response = self._get(f"devices/id/{device_id}/")
        return response

    def _parse_device_to_asset(self, device: Dict[str, Any],
                               asset_type: AssetType) -> Asset:
        """Parse Device42 device data to Asset model."""
        # Extract dates
        purchase_date = None
        if device.get("first_added"):
            try:
                purchase_date = datetime.fromisoformat(
                    device["first_added"].replace("Z", "+00:00")
                )
            except (ValueError, AttributeError):
                pass

        # Calculate age
        age_years = None
        if purchase_date:
            age_years = (datetime.now() - purchase_date.replace(tzinfo=None)).days / 365.25

        asset_data = {
            "id": f"d42_{device.get('device_id', device.get('id'))}",
            "name": device.get("name", ""),
            "hostname": device.get("name", ""),
            "asset_type": asset_type,
            "manufacturer": device.get("manufacturer", ""),
            "model": device.get("hw_model", device.get("model", "")),
            "serial_number": device.get("serial_no", ""),
            "purchase_date": purchase_date,
            "age_years": age_years,
            "os_name": device.get("os", {}).get("name") if isinstance(device.get("os"), dict) else device.get("os"),
            "os_version": device.get("os", {}).get("version") if isinstance(device.get("os"), dict) else None,
            "location": device.get("room", device.get("building", "")),
            "ip_address": device.get("ip_address", device.get("primary_ip", "")),
            "mac_address": device.get("mac_address", ""),
            "device42_id": str(device.get("device_id", device.get("id", ""))),
            "tags": device.get("tags", []),
            "custom_fields": device.get("custom_fields", {})
        }

        # Asset type specific parsing
        if asset_type in [AssetType.PHYSICAL_SERVER, AssetType.VIRTUAL_SERVER]:
            asset_data.update({
                "cpu_count": device.get("cpucount"),
                "cpu_model": device.get("cpucore"),
                "ram_gb": device.get("ram") / 1024 if device.get("ram") else None,
                "is_virtual": asset_type == AssetType.VIRTUAL_SERVER,
                "virtual_host": device.get("virtual_host_name")
            })
            return Server(**asset_data)

        elif asset_type in [AssetType.NETWORK_SWITCH, AssetType.ROUTER,
                           AssetType.FIREWALL, AssetType.ACCESS_POINT]:
            asset_data.update({
                "ports_total": device.get("port_count"),
                "firmware_version": device.get("os_version", device.get("version")),
                "management_ip": device.get("ip_address")
            })
            return NetworkDevice(**asset_data)

        elif asset_type == AssetType.STORAGE_DEVICE:
            return StorageDevice(**asset_data)

        return Asset(**asset_data)

    def get_all_assets(self) -> List[Asset]:
        """Retrieve and parse all assets from Device42."""
        assets = []

        logger.info("Fetching physical servers...")
        physical_servers = self.get_physical_servers()
        for device in physical_servers:
            try:
                asset = self._parse_device_to_asset(device, AssetType.PHYSICAL_SERVER)
                assets.append(asset)
            except Exception as e:
                logger.error(f"Error parsing device {device.get('name')}: {e}")

        logger.info("Fetching virtual machines...")
        vms = self.get_virtual_machines()
        for vm in vms:
            try:
                asset = self._parse_device_to_asset(vm, AssetType.VIRTUAL_SERVER)
                assets.append(asset)
            except Exception as e:
                logger.error(f"Error parsing VM {vm.get('name')}: {e}")

        logger.info("Fetching network devices...")
        network_devices = self.get_network_devices()
        for device in network_devices:
            try:
                # Determine specific network device type
                device_type = self._determine_network_device_type(device)
                asset = self._parse_device_to_asset(device, device_type)
                assets.append(asset)
            except Exception as e:
                logger.error(f"Error parsing network device {device.get('name')}: {e}")

        logger.info("Fetching storage devices...")
        storage_devices = self.get_storage_devices()
        for device in storage_devices:
            try:
                asset = self._parse_device_to_asset(device, AssetType.STORAGE_DEVICE)
                assets.append(asset)
            except Exception as e:
                logger.error(f"Error parsing storage device {device.get('name')}: {e}")

        logger.info(f"Total assets retrieved: {len(assets)}")
        return assets

    def _determine_network_device_type(self, device: Dict[str, Any]) -> AssetType:
        """Determine the specific type of network device."""
        device_type = device.get("type", "").lower()
        hw_model = device.get("hw_model", "").lower()
        name = device.get("name", "").lower()

        if "switch" in device_type or "switch" in hw_model:
            return AssetType.NETWORK_SWITCH
        elif "router" in device_type or "router" in hw_model:
            return AssetType.ROUTER
        elif "firewall" in device_type or "firewall" in hw_model or "fw" in name:
            return AssetType.FIREWALL
        elif "ap" in device_type or "access point" in device_type or "wireless" in hw_model:
            return AssetType.ACCESS_POINT
        else:
            return AssetType.NETWORK_SWITCH  # Default to switch

    def test_connection(self) -> bool:
        """Test the connection to Device42 API."""
        try:
            self._get("devices/all/", {"limit": 1})
            logger.info("Device42 connection successful")
            return True
        except Exception as e:
            logger.error(f"Device42 connection failed: {e}")
            return False
