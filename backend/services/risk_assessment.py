"""
Risk assessment engine using industry-standard failure rate models.

Based on:
- Bathtub curve (infant mortality, useful life, wear-out)
- MTBF (Mean Time Between Failures) industry standards
- Hardware lifecycle research from Backblaze, Google, and academic studies
"""
import math
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from enum import Enum

from models import Asset, RiskLevel, RiskAssessment, SupportStatus


class FailureRateModel:
    """
    Hardware failure rate model based on industry research.

    Research sources:
    - Backblaze Hard Drive Stats (2013-2023)
    - Google's Failure Trends in Large Disk Drive Population
    - IEEE studies on hardware reliability
    - Arrhenius equation for temperature-accelerated aging
    """

    # Annual Failure Rate (AFR) by age - based on bathtub curve
    AFR_BY_AGE = {
        0: 0.05,   # Year 0-1: Infant mortality (5% AFR)
        1: 0.02,   # Year 1-2: Stable period (2% AFR)
        2: 0.02,   # Year 2-3: Stable period (2% AFR)
        3: 0.03,   # Year 3-4: Beginning of wear-out (3% AFR)
        4: 0.05,   # Year 4-5: Increased wear (5% AFR)
        5: 0.08,   # Year 5-6: Significant wear (8% AFR)
        6: 0.12,   # Year 6-7: High wear (12% AFR)
        7: 0.20,   # Year 7-8: Critical wear (20% AFR)
        8: 0.30,   # Year 8+: Severe risk (30%+ AFR)
    }

    @staticmethod
    def get_failure_rate(age_years: float) -> float:
        """
        Get annual failure rate for given age.

        Args:
            age_years: Age in years

        Returns:
            Annual failure rate (0-1)
        """
        age_floor = min(int(age_years), 8)
        return FailureRateModel.AFR_BY_AGE.get(age_floor, 0.35)

    @staticmethod
    def get_mtbf_multiplier(age_years: float) -> float:
        """
        Get MTBF reduction multiplier based on age.

        New hardware typically has MTBF of 300,000-500,000 hours.
        This multiplier shows how MTBF degrades with age.

        Returns:
            Multiplier (1.0 = baseline, <1.0 = reduced MTBF)
        """
        if age_years < 1:
            return 0.95  # Infant mortality period
        elif age_years < 3:
            return 1.0   # Peak reliability
        elif age_years < 5:
            return 0.90  # Slight degradation
        elif age_years < 7:
            return 0.70  # Noticeable degradation
        else:
            return 0.50  # Significant degradation


class RiskAssessmentEngine:
    """Engine for calculating infrastructure risk scores."""

    def __init__(self, config: Dict):
        """
        Initialize risk assessment engine.

        Args:
            config: Risk assessment configuration
        """
        self.config = config
        self.max_age_years = config.get("max_age_years", 7)
        self.thresholds = config.get("age_thresholds", {
            "low": 3,
            "medium": 5,
            "high": 7
        })
        self.weights = config.get("weight_factors", {
            "age": 0.4,
            "support_status": 0.3,
            "incident_history": 0.2,
            "manufacturer_eol": 0.1
        })

    def assess_asset(self, asset: Asset,
                    incident_stats: Dict = None,
                    eol_info: Dict = None) -> RiskAssessment:
        """
        Perform comprehensive risk assessment on an asset.

        Args:
            asset: Asset to assess
            incident_stats: Jira incident statistics
            eol_info: Manufacturer EOL information

        Returns:
            RiskAssessment object with score and recommendations
        """
        factors = {}
        recommendations = []

        # Factor 1: Age-based risk using industry failure rates
        age_score, age_recs = self._assess_age_risk(asset)
        factors["age"] = age_score
        recommendations.extend(age_recs)

        # Factor 2: Support status risk
        support_score, support_recs = self._assess_support_status(asset, eol_info)
        factors["support_status"] = support_score
        recommendations.extend(support_recs)

        # Factor 3: Incident history risk
        incident_score, incident_recs = self._assess_incident_history(
            asset, incident_stats
        )
        factors["incident_history"] = incident_score
        recommendations.extend(incident_recs)

        # Factor 4: Manufacturer EOL risk
        eol_score, eol_recs = self._assess_eol_status(asset, eol_info)
        factors["manufacturer_eol"] = eol_score
        recommendations.extend(eol_recs)

        # Calculate weighted total score (0-100)
        total_score = sum(
            factors[factor] * self.weights.get(factor, 0)
            for factor in factors
        )

        # Determine risk level
        risk_level = self._score_to_risk_level(total_score)

        # Update asset with risk information
        asset.risk_score = total_score
        asset.risk_level = risk_level
        asset.risk_factors = factors

        return RiskAssessment(
            asset_id=asset.id,
            asset_name=asset.name,
            hostname=asset.hostname,
            risk_score=total_score,
            risk_level=risk_level,
            factors=factors,
            recommendations=sorted(set(recommendations))
        )

    def _assess_age_risk(self, asset: Asset) -> Tuple[float, List[str]]:
        """
        Assess risk based on age using industry failure rate models.

        Returns:
            Tuple of (risk_score 0-100, recommendations)
        """
        recommendations = []

        if not asset.age_years:
            return 0, ["Unable to determine asset age - verify purchase date"]

        age = asset.age_years

        # Get failure rate for this age
        afr = FailureRateModel.get_failure_rate(age)
        mtbf_mult = FailureRateModel.get_mtbf_multiplier(age)

        # Convert AFR to risk score (0-100)
        # AFR of 0.30 (30%) = 100 risk score
        age_score = min(afr / 0.30 * 100, 100)

        # Generate recommendations based on age
        if age > self.max_age_years:
            recommendations.append(
                f"⚠️ CRITICAL: Asset is {age:.1f} years old, exceeds {self.max_age_years} year policy. "
                f"Annual failure rate: {afr*100:.1f}%. Replacement URGENT."
            )
        elif age > self.thresholds["high"]:
            recommendations.append(
                f"⚠️ HIGH RISK: Asset is {age:.1f} years old. "
                f"Annual failure rate: {afr*100:.1f}%. Plan replacement within 6 months."
            )
        elif age > self.thresholds["medium"]:
            recommendations.append(
                f"⚠️ MODERATE: Asset is {age:.1f} years old. "
                f"Annual failure rate: {afr*100:.1f}%. Plan replacement within 12-18 months."
            )
        elif age > self.thresholds["low"]:
            recommendations.append(
                f"Age {age:.1f} years - entering wear period. "
                f"Annual failure rate: {afr*100:.1f}%. Monitor closely."
            )

        # Add MTBF information
        if mtbf_mult < 0.8:
            recommendations.append(
                f"MTBF degraded to {mtbf_mult*100:.0f}% of baseline. "
                "Increased probability of unplanned downtime."
            )

        return age_score, recommendations

    def _assess_support_status(self, asset: Asset,
                              eol_info: Dict = None) -> Tuple[float, List[str]]:
        """Assess risk based on support and EOL status."""
        recommendations = []
        score = 0

        if asset.support_status == SupportStatus.EXPIRED:
            score = 100
            recommendations.append(
                "🔴 CRITICAL: Support contract expired. No vendor assistance available."
            )
        elif asset.support_status == SupportStatus.EXPIRING_SOON:
            score = 70
            if asset.support_expiry_date:
                days_left = (asset.support_expiry_date - datetime.now()).days
                recommendations.append(
                    f"⚠️ Support expires in {days_left} days. Renew or plan replacement."
                )
        elif asset.support_status == SupportStatus.ACTIVE:
            score = 10
        else:
            score = 50
            recommendations.append(
                "⚠️ Support status unknown. Verify warranty and support coverage."
            )

        # Check EOL status
        if eol_info:
            if eol_info.get("is_eol"):
                score = max(score, 90)
                recommendations.append(
                    f"🔴 End of Life reached. No further updates or support from manufacturer."
                )
            elif eol_info.get("eos_date"):
                score = max(score, 60)
                recommendations.append(
                    "⚠️ End of Service announced. Limited support window remaining."
                )

        return score, recommendations

    def _assess_incident_history(self, asset: Asset,
                                incident_stats: Dict = None) -> Tuple[float, List[str]]:
        """Assess risk based on incident/ticket history."""
        recommendations = []

        if not incident_stats:
            return 0, []

        total_incidents = incident_stats.get("total_incidents", 0)
        critical_incidents = incident_stats.get("critical_incidents", 0)
        incident_rate = incident_stats.get("incident_rate", 0)  # per month

        # Calculate score based on incident frequency
        # More than 2 incidents per month = high risk
        score = min(incident_rate / 2.0 * 100, 100)

        # Increase score for critical incidents
        if critical_incidents > 0:
            score = min(score + (critical_incidents * 10), 100)

        if incident_rate > 2:
            recommendations.append(
                f"🔴 HIGH incident rate: {incident_rate:.1f} incidents/month. "
                "Asset showing signs of instability."
            )
        elif incident_rate > 1:
            recommendations.append(
                f"⚠️ ELEVATED incident rate: {incident_rate:.1f} incidents/month. "
                "Monitor for recurring issues."
            )

        if critical_incidents > 0:
            recommendations.append(
                f"⚠️ {critical_incidents} critical incidents in last 12 months. "
                "Review for persistent problems."
            )

        return score, recommendations

    def _assess_eol_status(self, asset: Asset,
                          eol_info: Dict = None) -> Tuple[float, List[str]]:
        """Assess risk based on manufacturer EOL announcements."""
        recommendations = []

        if not eol_info:
            return 0, []

        score = 0

        if eol_info.get("is_eol"):
            score = 100
            eol_date = eol_info.get("eol_date")
            recommendations.append(
                f"🔴 Product EOL: {eol_date}. No security patches or updates available."
            )
        elif eol_info.get("eol_announced"):
            months_until_eol = eol_info.get("months_until_eol", 0)
            if months_until_eol < 12:
                score = 80
                recommendations.append(
                    f"⚠️ EOL in {months_until_eol} months. Plan migration urgently."
                )
            else:
                score = 50
                recommendations.append(
                    f"EOL announced for {months_until_eol} months from now. Begin planning replacement."
                )

        return score, recommendations

    def _score_to_risk_level(self, score: float) -> RiskLevel:
        """Convert numeric score to risk level."""
        if score >= 75:
            return RiskLevel.CRITICAL
        elif score >= 50:
            return RiskLevel.HIGH
        elif score >= 25:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def batch_assess_assets(self, assets: List[Asset],
                          incident_data: Dict[str, Dict] = None,
                          eol_data: Dict[str, Dict] = None) -> List[RiskAssessment]:
        """
        Perform risk assessment on multiple assets.

        Args:
            assets: List of assets to assess
            incident_data: Dict mapping hostname to incident stats
            eol_data: Dict mapping model to EOL info

        Returns:
            List of RiskAssessment results
        """
        assessments = []
        incident_data = incident_data or {}
        eol_data = eol_data or {}

        for asset in assets:
            incidents = incident_data.get(asset.hostname, {})
            eol_info = eol_data.get(asset.model, {})

            assessment = self.assess_asset(asset, incidents, eol_info)
            assessments.append(assessment)

        return assessments
