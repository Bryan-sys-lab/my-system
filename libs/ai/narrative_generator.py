"""
Narrative Generator Module for B-Search

This module provides intelligent narrative generation capabilities
with different styles, audiences, and complexity levels.
"""

from typing import Dict, Any, List
from datetime import datetime, timezone


class NarrativeGenerator:
    """AI-powered narrative generator for intelligence reports"""

    def __init__(self):
        self.styles = ["professional", "executive", "technical", "casual"]
        self.audiences = ["executive", "technical", "operational", "general"]
        self.lengths = ["brief", "standard", "comprehensive"]

    def generate_narrative(
        self,
        analysis_data: Dict[str, Any],
        style: str = "professional",
        audience: str = "executive",
        length: str = "comprehensive"
    ) -> Dict[str, Any]:
        """Generate AI-powered narrative with specified parameters"""

        # Validate parameters
        if style not in self.styles:
            raise ValueError(f"Unsupported style: {style}. Supported: {self.styles}")
        if audience not in self.audiences:
            raise ValueError(f"Unsupported audience: {audience}. Supported: {self.audiences}")
        if length not in self.lengths:
            raise ValueError(f"Unsupported length: {length}. Supported: {self.lengths}")

        # Generate narrative components
        title = self._generate_narrative_title(analysis_data, style, audience)
        executive_summary = self._generate_narrative_executive_summary(analysis_data, style, audience, length)
        main_body = self._generate_narrative_main_body(analysis_data, style, audience, length)
        conclusions = self._generate_narrative_conclusions(analysis_data, style, audience)
        recommendations = self._generate_narrative_recommendations(analysis_data, audience, length)
        confidence_score = self._calculate_narrative_confidence(analysis_data)
        key_takeaways = self._generate_key_takeaways(analysis_data, audience)

        return {
            "title": title,
            "executive_summary": executive_summary,
            "main_body": main_body,
            "conclusions": conclusions,
            "recommendations": recommendations,
            "confidence_score": confidence_score,
            "key_takeaways": key_takeaways,
            "metadata": {
                "style": style,
                "audience": audience,
                "length": length,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "version": "1.0"
            }
        }

    def _generate_narrative_title(self, analysis_data: Dict[str, Any], style: str, audience: str) -> str:
        """Generate appropriate title for narrative"""
        trend = analysis_data.get("trend_analysis", {}).get("trend", "comprehensive")
        confidence = analysis_data.get("confidence_metrics", {}).get("overall_confidence", 0.8)

        if audience == "executive":
            return f"B-Search Intelligence: {trend.title()} Trends & Strategic Insights"
        elif audience == "technical":
            return f"Technical Analysis Report: {trend.title()} Pattern Detection (Confidence: {confidence*100:.0f}%)"
        else:
            return f"B-Search Analytics Report: {trend.title()} Trends & Key Findings"

    def _generate_narrative_executive_summary(
        self,
        analysis_data: Dict[str, Any],
        style: str,
        audience: str,
        length: str
    ) -> str:
        """Generate executive summary for narrative"""
        total_items = analysis_data.get("summary", {}).get("total_items", 0)
        trend = analysis_data.get("trend_analysis", {}).get("trend", "stable")

        if length == "brief":
            return f"This report analyzes {total_items:,} data points, revealing {trend} trends with high confidence. Key insights include emerging patterns and actionable recommendations for strategic decision-making."
        else:
            return f"""Comprehensive analysis of {total_items:,} intelligence data points reveals {trend} activity patterns across multiple platforms. The AI-powered analysis identifies key trends, anomalies, and predictive insights that inform strategic intelligence operations. This report provides actionable recommendations for optimizing data collection, enhancing monitoring capabilities, and maximizing intelligence value."""

    def _generate_narrative_main_body(
        self,
        analysis_data: Dict[str, Any],
        style: str,
        audience: str,
        length: str
    ) -> str:
        """Generate main body of narrative"""
        sections = self._determine_sections(length)
        body_parts = []

        if "detailed_analysis" in sections:
            trend_analysis = analysis_data.get("trend_analysis", {})
            body_parts.append(f"""## Trend Analysis
Current data trends indicate a {trend_analysis.get('trend', 'stable')} pattern with {trend_analysis.get('confidence', 0)*100:.1f}% confidence. This suggests {'increasing' if trend_analysis.get('trend') == 'rising' else 'decreasing' if trend_analysis.get('trend') == 'falling' else 'stable'} activity levels that warrant {'immediate attention' if trend_analysis.get('trend') == 'rising' else 'monitoring' if trend_analysis.get('trend') == 'falling' else 'routine oversight'}.""")

        if "recommendations" in sections:
            recommendations = analysis_data.get("recommendations", [])
            if recommendations:
                body_parts.append("## Strategic Recommendations\n" + "\n".join([f"• {rec['recommendation']} ({rec['priority']} priority)" for rec in recommendations[:5]]))

        return "\n\n".join(body_parts)

    def _generate_narrative_conclusions(self, analysis_data: Dict[str, Any], style: str, audience: str) -> str:
        """Generate conclusions for narrative"""
        confidence = analysis_data.get("confidence_metrics", {}).get("overall_confidence", 0.8)
        risk_level = analysis_data.get("risk_assessment", {}).get("overall_risk_level", "medium")

        return f"""## Conclusions
This AI-powered analysis provides {confidence*100:.0f}% confidence in the identified patterns and trends. The {risk_level} risk assessment indicates {'stable operations with opportunities for optimization' if risk_level == 'low' else 'moderate attention required for key areas' if risk_level == 'medium' else 'immediate action needed to address critical issues'}. Strategic implementation of the recommendations will enhance intelligence capabilities and operational effectiveness."""

    def _generate_narrative_recommendations(self, analysis_data: Dict[str, Any], audience: str, length: str) -> str:
        """Generate recommendations section"""
        recommendations = analysis_data.get("recommendations", [])

        if audience == "executive":
            recs = [rec for rec in recommendations if rec["priority"] == "high"]
        else:
            recs = recommendations[:5] if length == "brief" else recommendations

        return "\n".join([f"**{rec['category'].replace('_', ' ').title()}**: {rec['recommendation']}" for rec in recs])

    def _calculate_narrative_confidence(self, analysis_data: Dict[str, Any]) -> float:
        """Calculate confidence score for narrative"""
        base_confidence = analysis_data.get("confidence_metrics", {}).get("overall_confidence", 0.8)
        data_quality = analysis_data.get("confidence_metrics", {}).get("data_quality_score", 0.8)

        return round((base_confidence + data_quality) / 2, 2)

    def _generate_key_takeaways(self, analysis_data: Dict[str, Any], audience: str) -> List[str]:
        """Generate key takeaways"""
        insights = analysis_data.get("key_insights", [])

        if audience == "executive":
            return [insight["insight"] for insight in insights if insight["priority"] == "high"]
        else:
            return [insight["insight"] for insight in insights[:3]]

    def _determine_sections(self, length: str) -> List[str]:
        """Determine which sections to include based on length"""
        if length == "brief":
            return ["executive_summary", "key_takeaways"]
        elif length == "comprehensive":
            return ["executive_summary", "detailed_analysis", "recommendations", "conclusions"]
        else:  # standard
            return ["executive_summary", "main_body", "conclusions"]

    def generate_targeted_narrative(
        self,
        analysis_data: Dict[str, Any],
        focus_areas: List[str],
        tone: str = "professional"
    ) -> Dict[str, Any]:
        """Generate narrative focused on specific areas"""
        focused_data = self._extract_focused_data(analysis_data, focus_areas)

        return self.generate_narrative(
            focused_data,
            style=tone,
            audience="general",
            length="standard"
        )

    def _extract_focused_data(self, analysis_data: Dict[str, Any], focus_areas: List[str]) -> Dict[str, Any]:
        """Extract data relevant to focus areas"""
        focused_data = analysis_data.copy()

        if "trends" in focus_areas:
            focused_data["key_insights"] = [
                insight for insight in analysis_data.get("key_insights", [])
                if insight.get("type") == "trend"
            ]

        if "anomalies" in focus_areas:
            focused_data["anomaly_insights"] = analysis_data.get("anomaly_insights", {})
            focused_data["key_insights"] = [
                insight for insight in analysis_data.get("key_insights", [])
                if insight.get("type") == "anomaly"
            ]

        if "predictions" in focus_areas:
            focused_data["predictive_forecast"] = analysis_data.get("predictive_forecast", {})

        return focused_data

    def generate_executive_brief(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive brief (short, high-level summary)"""
        return self.generate_narrative(
            analysis_data,
            style="executive",
            audience="executive",
            length="brief"
        )

    def generate_technical_report(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate technical report (detailed, data-driven)"""
        return self.generate_narrative(
            analysis_data,
            style="technical",
            audience="technical",
            length="comprehensive"
        )

    def generate_operational_summary(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate operational summary (action-oriented)"""
        return self.generate_narrative(
            analysis_data,
            style="professional",
            audience="operational",
            length="standard"
        )

    def customize_narrative(
        self,
        base_narrative: Dict[str, Any],
        customizations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Customize existing narrative with specific requirements"""
        customized = base_narrative.copy()

        # Apply customizations
        if "additional_sections" in customizations:
            for section in customizations["additional_sections"]:
                customized[section["name"]] = section["content"]

        if "emphasis_areas" in customizations:
            # Add emphasis to specific areas
            for area in customizations["emphasis_areas"]:
                if area in customized:
                    customized[area] = f"**EMPHASIS:** {customized[area]}"

        if "custom_title" in customizations:
            customized["title"] = customizations["custom_title"]

        return customized

    def generate_narrative_variants(
        self,
        analysis_data: Dict[str, Any],
        base_style: str = "professional"
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Generate multiple narrative variants for comparison"""
        variants = {
            "styles": [],
            "audiences": [],
            "lengths": []
        }

        # Generate style variants
        for style in self.styles:
            variants["styles"].append(self.generate_narrative(
                analysis_data, style=style, audience="general", length="standard"
            ))

        # Generate audience variants
        for audience in self.audiences:
            variants["audiences"].append(self.generate_narrative(
                analysis_data, style=base_style, audience=audience, length="standard"
            ))

        # Generate length variants
        for length in self.lengths:
            variants["lengths"].append(self.generate_narrative(
                analysis_data, style=base_style, audience="general", length=length
            ))

        return variants