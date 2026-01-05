"""
Asset correlation service to match assets between Device42 and Jira.
"""
import logging
from typing import List, Dict, Tuple, Set
from difflib import SequenceMatcher

from models import Asset

logger = logging.getLogger(__name__)


class AssetCorrelator:
    """Correlate assets between Device42, Jira, and manufacturer data."""

    def __init__(self, matching_threshold: float = 0.85):
        """
        Initialize asset correlator.

        Args:
            matching_threshold: Similarity threshold for fuzzy matching (0-1)
        """
        self.matching_threshold = matching_threshold

    def correlate_with_jira(
        self,
        device42_assets: List[Asset],
        jira_assets: List[Dict]
    ) -> Tuple[List[Asset], List[str]]:
        """
        Match Device42 assets with Jira asset register.

        Args:
            device42_assets: Assets from Device42
            jira_assets: Assets from Jira

        Returns:
            Tuple of (updated assets with Jira info, list of unmatched hostnames)
        """
        # Create hostname index for Jira assets
        jira_index = {
            asset["hostname"].lower(): asset
            for asset in jira_assets
            if asset.get("hostname")
        }

        matched_count = 0
        unmatched_hostnames = []

        for asset in device42_assets:
            hostname_lower = asset.hostname.lower()

            # Exact hostname match
            if hostname_lower in jira_index:
                jira_asset = jira_index[hostname_lower]
                asset.jira_asset_tag = jira_asset.get("asset_tag")
                asset.jira_matched = True
                matched_count += 1
                logger.debug(f"Matched {asset.hostname} to Jira")
                continue

            # Try fuzzy matching
            best_match = self._find_best_match(hostname_lower, list(jira_index.keys()))
            if best_match:
                jira_asset = jira_index[best_match]
                asset.jira_asset_tag = jira_asset.get("asset_tag")
                asset.jira_matched = True
                matched_count += 1
                logger.debug(f"Fuzzy matched {asset.hostname} to {best_match}")
                continue

            # No match found
            asset.jira_matched = False
            unmatched_hostnames.append(asset.hostname)

        logger.info(
            f"Matched {matched_count}/{len(device42_assets)} assets with Jira. "
            f"{len(unmatched_hostnames)} unmatched."
        )

        return device42_assets, unmatched_hostnames

    def enrich_with_incident_data(
        self,
        assets: List[Asset],
        incident_data: Dict[str, Dict]
    ) -> List[Asset]:
        """
        Enrich assets with Jira incident/ticket statistics.

        Args:
            assets: List of assets to enrich
            incident_data: Dict mapping hostname to incident stats

        Returns:
            Updated assets with incident data
        """
        for asset in assets:
            stats = incident_data.get(asset.hostname, {})

            asset.jira_ticket_count = stats.get("total_incidents", 0)
            asset.jira_critical_tickets = stats.get("critical_incidents", 0)

        return assets

    def enrich_with_warranty_data(
        self,
        assets: List[Asset],
        warranty_data: Dict[str, Dict]
    ) -> List[Asset]:
        """
        Enrich assets with manufacturer warranty information.

        Args:
            assets: List of assets to enrich
            warranty_data: Dict mapping serial_number to warranty info

        Returns:
            Updated assets with warranty data
        """
        from models import SupportStatus
        from datetime import datetime

        for asset in assets:
            if not asset.serial_number:
                continue

            warranty = warranty_data.get(asset.serial_number)
            if not warranty:
                continue

            # Update support status
            if warranty.get("warranty_active"):
                asset.support_status = SupportStatus.ACTIVE

                # Check if expiring soon
                end_date_str = warranty.get("warranty_end_date")
                if end_date_str:
                    try:
                        end_date = datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))
                        days_until_expiry = (end_date - datetime.now()).days

                        if 0 <= days_until_expiry <= 90:
                            asset.support_status = SupportStatus.EXPIRING_SOON

                        asset.support_expiry_date = end_date
                    except (ValueError, AttributeError):
                        pass
            else:
                asset.support_status = SupportStatus.EXPIRED

        return assets

    def enrich_with_eol_data(
        self,
        assets: List[Asset],
        eol_data: Dict[str, Dict]
    ) -> List[Asset]:
        """
        Enrich assets with manufacturer EOL information.

        Args:
            assets: List of assets to enrich
            eol_data: Dict mapping model to EOL info

        Returns:
            Updated assets with EOL data
        """
        from datetime import datetime

        for asset in assets:
            if not asset.model:
                continue

            eol_info = eol_data.get(asset.model)
            if not eol_info:
                continue

            # Update EOL dates
            if eol_info.get("eol_date"):
                try:
                    asset.eol_date = datetime.fromisoformat(
                        eol_info["eol_date"].replace("Z", "+00:00")
                    )
                except (ValueError, AttributeError):
                    pass

            if eol_info.get("eos_date"):
                try:
                    asset.eos_date = datetime.fromisoformat(
                        eol_info["eos_date"].replace("Z", "+00:00")
                    )
                except (ValueError, AttributeError):
                    pass

        return assets

    def _find_best_match(self, target: str, candidates: List[str]) -> str:
        """
        Find the best fuzzy match for a hostname.

        Args:
            target: Target hostname
            candidates: List of candidate hostnames

        Returns:
            Best matching hostname or None
        """
        best_match = None
        best_ratio = 0

        for candidate in candidates:
            ratio = SequenceMatcher(None, target, candidate).ratio()

            if ratio > best_ratio and ratio >= self.matching_threshold:
                best_ratio = ratio
                best_match = candidate

        return best_match

    def find_discrepancies(
        self,
        device42_assets: List[Asset],
        jira_assets: List[Dict]
    ) -> Dict[str, List[str]]:
        """
        Find discrepancies between Device42 and Jira asset registers.

        Returns:
            Dict with categories of discrepancies
        """
        discrepancies = {
            "in_device42_not_jira": [],
            "in_jira_not_device42": [],
            "mismatched_data": []
        }

        # Get hostnames
        d42_hostnames = {asset.hostname.lower() for asset in device42_assets}
        jira_hostnames = {
            asset["hostname"].lower()
            for asset in jira_assets
            if asset.get("hostname")
        }

        # Find assets only in Device42
        discrepancies["in_device42_not_jira"] = sorted(
            d42_hostnames - jira_hostnames
        )

        # Find assets only in Jira
        discrepancies["in_jira_not_device42"] = sorted(
            jira_hostnames - d42_hostnames
        )

        # Find mismatched data (same hostname, different attributes)
        for asset in device42_assets:
            hostname_lower = asset.hostname.lower()

            for jira_asset in jira_assets:
                if jira_asset.get("hostname", "").lower() == hostname_lower:
                    mismatches = []

                    # Compare serial numbers
                    if asset.serial_number and jira_asset.get("serial_number"):
                        if asset.serial_number != jira_asset["serial_number"]:
                            mismatches.append(
                                f"Serial: D42={asset.serial_number} vs "
                                f"Jira={jira_asset['serial_number']}"
                            )

                    # Compare models
                    if asset.model and jira_asset.get("model"):
                        if asset.model != jira_asset["model"]:
                            mismatches.append(
                                f"Model: D42={asset.model} vs "
                                f"Jira={jira_asset['model']}"
                            )

                    if mismatches:
                        discrepancies["mismatched_data"].append(
                            f"{asset.hostname}: {', '.join(mismatches)}"
                        )

        logger.info(
            f"Found {len(discrepancies['in_device42_not_jira'])} assets only in Device42, "
            f"{len(discrepancies['in_jira_not_device42'])} only in Jira, "
            f"{len(discrepancies['mismatched_data'])} with mismatched data"
        )

        return discrepancies
