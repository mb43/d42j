"""
Jira ServiceDesk API client for retrieving asset and ticket information.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from jira import JIRA
from jira.exceptions import JIRAError

logger = logging.getLogger(__name__)


class JiraClient:
    """Client for interacting with Jira ServiceDesk API."""

    def __init__(self, host: str, username: str, api_token: str,
                 project_key: str = "IT"):
        """
        Initialize Jira client.

        Args:
            host: Jira instance URL
            username: Jira username/email
            api_token: Jira API token
            project_key: Project key for infrastructure tickets
        """
        self.host = host
        self.project_key = project_key

        try:
            self.client = JIRA(
                server=host,
                basic_auth=(username, api_token)
            )
            logger.info(f"Connected to Jira at {host}")
        except JIRAError as e:
            logger.error(f"Failed to connect to Jira: {e}")
            raise

    def get_asset_tickets(self, hostname: str) -> List[Dict[str, Any]]:
        """
        Get all tickets related to a specific asset by hostname.

        Args:
            hostname: Asset hostname to search for

        Returns:
            List of ticket information dictionaries
        """
        try:
            # Search for tickets containing the hostname
            jql = f'project = {self.project_key} AND (summary ~ "{hostname}" OR description ~ "{hostname}")'
            issues = self.client.search_issues(jql, maxResults=1000)

            tickets = []
            for issue in issues:
                ticket_info = self._parse_issue(issue)
                tickets.append(ticket_info)

            logger.info(f"Found {len(tickets)} tickets for hostname {hostname}")
            return tickets

        except JIRAError as e:
            logger.error(f"Error searching for tickets for {hostname}: {e}")
            return []

    def get_critical_tickets(self, hostname: str) -> List[Dict[str, Any]]:
        """
        Get critical/high priority tickets for an asset.

        Args:
            hostname: Asset hostname

        Returns:
            List of critical ticket dictionaries
        """
        try:
            jql = (f'project = {self.project_key} AND '
                   f'priority in (Highest, High) AND '
                   f'(summary ~ "{hostname}" OR description ~ "{hostname}")')
            issues = self.client.search_issues(jql, maxResults=1000)

            tickets = [self._parse_issue(issue) for issue in issues]
            logger.info(f"Found {len(tickets)} critical tickets for {hostname}")
            return tickets

        except JIRAError as e:
            logger.error(f"Error searching for critical tickets: {e}")
            return []

    def get_open_tickets(self, hostname: str) -> List[Dict[str, Any]]:
        """Get open tickets for an asset."""
        try:
            jql = (f'project = {self.project_key} AND '
                   f'status not in (Closed, Resolved, Done) AND '
                   f'(summary ~ "{hostname}" OR description ~ "{hostname}")')
            issues = self.client.search_issues(jql, maxResults=1000)

            tickets = [self._parse_issue(issue) for issue in issues]
            logger.info(f"Found {len(tickets)} open tickets for {hostname}")
            return tickets

        except JIRAError as e:
            logger.error(f"Error searching for open tickets: {e}")
            return []

    def get_asset_from_cmdb(self, hostname: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve asset information from Jira Assets/Insight (if configured).

        Args:
            hostname: Asset hostname

        Returns:
            Asset information dictionary or None
        """
        # Note: This requires Jira Assets/Insight plugin
        # Implementation depends on whether the Jira instance has this configured
        try:
            # Search for asset in custom fields or linked assets
            jql = f'project = {self.project_key} AND "Asset" ~ "{hostname}"'
            issues = self.client.search_issues(jql, maxResults=1)

            if issues:
                issue = issues[0]
                # Extract asset information from custom fields
                asset_info = {
                    "hostname": hostname,
                    "jira_key": issue.key,
                    "asset_tag": self._get_custom_field(issue, "Asset Tag"),
                    "serial_number": self._get_custom_field(issue, "Serial Number"),
                    "model": self._get_custom_field(issue, "Model"),
                    "location": self._get_custom_field(issue, "Location"),
                }
                return asset_info

            return None

        except JIRAError as e:
            logger.error(f"Error retrieving asset from Jira CMDB: {e}")
            return None

    def get_incident_history(self, hostname: str,
                           days: int = 365) -> Dict[str, Any]:
        """
        Get incident history statistics for an asset.

        Args:
            hostname: Asset hostname
            days: Number of days to look back

        Returns:
            Dictionary with incident statistics
        """
        try:
            # Search for incidents in the last N days
            jql = (f'project = {self.project_key} AND '
                   f'issuetype = Incident AND '
                   f'created >= -{days}d AND '
                   f'(summary ~ "{hostname}" OR description ~ "{hostname}")')

            issues = self.client.search_issues(jql, maxResults=1000)

            # Calculate statistics
            total_incidents = len(issues)
            critical_incidents = sum(
                1 for issue in issues
                if issue.fields.priority.name in ["Highest", "High"]
            )

            resolved_incidents = sum(
                1 for issue in issues
                if issue.fields.status.name in ["Resolved", "Closed", "Done"]
            )

            avg_resolution_time = self._calculate_avg_resolution_time(issues)

            return {
                "total_incidents": total_incidents,
                "critical_incidents": critical_incidents,
                "resolved_incidents": resolved_incidents,
                "open_incidents": total_incidents - resolved_incidents,
                "avg_resolution_hours": avg_resolution_time,
                "incident_rate": total_incidents / (days / 30)  # per month
            }

        except JIRAError as e:
            logger.error(f"Error getting incident history: {e}")
            return {
                "total_incidents": 0,
                "critical_incidents": 0,
                "resolved_incidents": 0,
                "open_incidents": 0,
                "avg_resolution_hours": 0,
                "incident_rate": 0
            }

    def _parse_issue(self, issue) -> Dict[str, Any]:
        """Parse Jira issue to dictionary."""
        return {
            "key": issue.key,
            "summary": issue.fields.summary,
            "status": issue.fields.status.name,
            "priority": issue.fields.priority.name if issue.fields.priority else "None",
            "created": issue.fields.created,
            "updated": issue.fields.updated,
            "reporter": issue.fields.reporter.displayName if issue.fields.reporter else "Unknown",
            "assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned",
            "issue_type": issue.fields.issuetype.name,
            "url": f"{self.host}/browse/{issue.key}"
        }

    def _get_custom_field(self, issue, field_name: str) -> Optional[str]:
        """Get value of a custom field by name."""
        try:
            # Get all fields
            all_fields = self.client.fields()
            field_map = {field['name']: field['id'] for field in all_fields}

            if field_name in field_map:
                field_id = field_map[field_name]
                value = getattr(issue.fields, field_id, None)
                return str(value) if value else None

            return None

        except Exception as e:
            logger.error(f"Error getting custom field {field_name}: {e}")
            return None

    def _calculate_avg_resolution_time(self, issues) -> float:
        """Calculate average resolution time in hours."""
        resolution_times = []

        for issue in issues:
            if issue.fields.resolutiondate and issue.fields.created:
                try:
                    created = datetime.strptime(
                        issue.fields.created[:19],
                        "%Y-%m-%dT%H:%M:%S"
                    )
                    resolved = datetime.strptime(
                        issue.fields.resolutiondate[:19],
                        "%Y-%m-%dT%H:%M:%S"
                    )
                    delta = (resolved - created).total_seconds() / 3600
                    resolution_times.append(delta)
                except (ValueError, AttributeError):
                    continue

        if resolution_times:
            return sum(resolution_times) / len(resolution_times)
        return 0

    def test_connection(self) -> bool:
        """Test the connection to Jira API."""
        try:
            self.client.myself()
            logger.info("Jira connection successful")
            return True
        except JIRAError as e:
            logger.error(f"Jira connection failed: {e}")
            return False

    def get_all_infrastructure_assets(self) -> List[Dict[str, Any]]:
        """
        Get all infrastructure assets from Jira.

        Returns:
            List of asset dictionaries
        """
        try:
            # This assumes assets are tracked in Jira issues or using Jira Assets plugin
            # Adjust the JQL based on how your Jira instance tracks assets
            jql = f'project = {self.project_key} AND issuetype = "Asset"'
            issues = self.client.search_issues(jql, maxResults=1000)

            assets = []
            for issue in issues:
                asset = {
                    "jira_key": issue.key,
                    "hostname": self._get_custom_field(issue, "Hostname") or issue.fields.summary,
                    "asset_tag": self._get_custom_field(issue, "Asset Tag"),
                    "serial_number": self._get_custom_field(issue, "Serial Number"),
                    "model": self._get_custom_field(issue, "Model"),
                    "manufacturer": self._get_custom_field(issue, "Manufacturer"),
                    "location": self._get_custom_field(issue, "Location"),
                }
                assets.append(asset)

            logger.info(f"Retrieved {len(assets)} assets from Jira")
            return assets

        except JIRAError as e:
            logger.error(f"Error retrieving assets from Jira: {e}")
            return []
