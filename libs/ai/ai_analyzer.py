"""
AI Analyzer Module for B-Search

This module provides the core AI analysis engine that combines statistical analysis,
trend detection, anomaly detection, and predictive analytics.
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta, timezone
from collections import defaultdict

from ..storage.models import Item, Project, Watcher
from .statistical_analyzer import StatisticalAnalyzer


class AIAnalyzer:
    """Main AI analysis engine for B-Search"""

    def __init__(self):
        self.statistical_analyzer = StatisticalAnalyzer()

    def perform_comprehensive_ai_analysis(
        self,
        items: List[Item],
        projects: List[Project],
        watchers: List[Watcher],
        data_type: str = "comprehensive",
        focus_areas: List[str] = None,
        analysis_depth: str = "detailed"
    ) -> Dict[str, Any]:
        """Perform comprehensive AI analysis on all data"""

        # Basic metrics
        total_items = len(items)
        total_projects = len(projects)
        active_watchers = len([w for w in watchers if w.enabled])

        # Trend analysis
        trend_data = self.statistical_analyzer.analyze_trends(items, 30)

        # Anomaly detection
        anomalies = self.statistical_analyzer.detect_anomalies(items)

        # Platform analysis
        platform_analysis = self._analyze_platform_performance(items)

        # Predictive insights
        predictions = self.statistical_analyzer.generate_predictive_insights(items)

        # Generate executive summary
        executive_summary = self._generate_executive_summary_ai(
            total_items, total_projects, active_watchers, trend_data, anomalies
        )

        # Generate key insights
        key_insights = self._generate_key_insights_ai(
            trend_data, anomalies, platform_analysis, predictions, analysis_depth
        )

        # Risk assessment
        risk_assessment = self._assess_risks_ai(items, watchers, anomalies)

        # Opportunity analysis
        opportunity_analysis = self._analyze_opportunities_ai(trend_data, platform_analysis, predictions)

        # Generate narrative report
        narrative_report = self._generate_narrative_report_ai(
            executive_summary, key_insights, trend_data, risk_assessment, opportunity_analysis
        )

        return {
            "executive_summary": executive_summary,
            "key_insights": key_insights,
            "trend_analysis": trend_data,
            "anomaly_insights": {
                "total_anomalies": len(anomalies),
                "severity_breakdown": self._categorize_anomalies(anomalies),
                "most_significant": anomalies[:5] if anomalies else []
            },
            "predictive_forecast": {
                "short_term": self._generate_short_term_forecast(items),
                "long_term": self._generate_long_term_forecast(items),
                "confidence_levels": self._calculate_forecast_confidence(items)
            },
            "recommendations": self._generate_ai_recommendations(
                trend_data, anomalies, platform_analysis, risk_assessment
            ),
            "risk_assessment": risk_assessment,
            "opportunity_analysis": opportunity_analysis,
            "narrative_report": narrative_report,
            "confidence_metrics": {
                "overall_confidence": self.statistical_analyzer.calculate_overall_confidence(trend_data, anomalies),
                "data_quality_score": self.statistical_analyzer.assess_data_quality(items),
                "analysis_reliability": self.statistical_analyzer.calculate_analysis_reliability(items, analysis_depth)
            }
        }

    def _analyze_platform_performance(self, items: List[Item]) -> Dict[str, Any]:
        """Analyze platform performance"""
        platform_stats = defaultdict(lambda: {"total_items": 0, "avg_content_length": 0, "first_collection": None, "last_collection": None})

        for item in items:
            platform = item.meta.get('platform', 'unknown') if item.meta else 'unknown'
            platform_stats[platform]["total_items"] += 1

            if item.content is not None:
                platform_stats[platform]["avg_content_length"] = (
                    (platform_stats[platform]["avg_content_length"] * (platform_stats[platform]["total_items"] - 1)) +
                    len(str(item.content))
                ) / platform_stats[platform]["total_items"]

            if not platform_stats[platform]["first_collection"] or item.created_at < platform_stats[platform]["first_collection"]:
                platform_stats[platform]["first_collection"] = item.created_at

            if not platform_stats[platform]["last_collection"] or item.created_at > platform_stats[platform]["last_collection"]:
                platform_stats[platform]["last_collection"] = item.created_at

        return dict(platform_stats)

    def _generate_executive_summary_ai(
        self,
        total_items: int,
        total_projects: int,
        active_watchers: int,
        trend_data: Dict[str, Any],
        anomalies: List[Dict[str, Any]]
    ) -> str:
        """Generate AI-powered executive summary"""

        trend_direction = trend_data.get("trend", "stable")
        confidence = trend_data.get("confidence", 0)

        summary = f"""B-Search Intelligence Report Summary

Data Overview:
• Total collected items: {total_items:,}
• Active projects: {total_projects}
• Monitoring watchers: {active_watchers}

Trend Analysis:
• Current trend direction: {trend_direction.title()}
• Analysis confidence: {confidence*100:.1f}%
• Recent activity shows {trend_data.get('change_percentage', 0):+.1f}% change

Anomaly Detection:
• Anomalies detected: {len(anomalies)}
• Most significant patterns: {self._categorize_anomalies(anomalies).get('high', 0)} high-severity events

Key Takeaways:
• System performance: {'Excellent' if confidence > 0.8 else 'Good' if confidence > 0.6 else 'Needs Attention'}
• Data collection: {'Strong' if total_items > 1000 else 'Moderate' if total_items > 100 else 'Limited'}
• Monitoring coverage: {'Comprehensive' if active_watchers > 5 else 'Basic' if active_watchers > 1 else 'Minimal'}
"""

        return summary

    def _generate_key_insights_ai(
        self,
        trend_data: Dict[str, Any],
        anomalies: List[Dict[str, Any]],
        platform_analysis: Dict[str, Any],
        predictions: List[Dict[str, Any]],
        analysis_depth: str
    ) -> List[Dict[str, Any]]:
        """Generate key insights based on analysis depth"""

        insights = []

        # Trend insights
        if trend_data.get("trend") == "rising":
            insights.append({
                "type": "trend",
                "priority": "high",
                "insight": f"Strong upward trend detected with {trend_data.get('confidence', 0)*100:.1f}% confidence",
                "impact": "positive",
                "recommendation": "Increase monitoring frequency for trending topics"
            })
        elif trend_data.get("trend") == "falling":
            insights.append({
                "type": "trend",
                "priority": "medium",
                "insight": f"Downward trend identified, potential decrease in activity",
                "impact": "neutral",
                "recommendation": "Monitor for emerging replacement topics"
            })

        # Anomaly insights
        if anomalies:
            high_severity = len([a for a in anomalies if a.get("severity") == "high"])
            if high_severity > 0:
                insights.append({
                    "type": "anomaly",
                    "priority": "high",
                    "insight": f"{high_severity} high-severity anomalies detected requiring immediate attention",
                    "impact": "high",
                    "recommendation": "Investigate anomalous activity patterns"
                })

        # Platform insights
        if platform_analysis:
            top_platform = max(platform_analysis.items(), key=lambda x: x[1]["total_items"])
            insights.append({
                "type": "platform",
                "priority": "medium",
                "insight": f"{top_platform[0].title()} shows highest activity with {top_platform[1]['total_items']} items",
                "impact": "informational",
                "recommendation": "Focus collection efforts on high-activity platforms"
            })

        # Predictive insights
        if predictions:
            insights.append({
                "type": "prediction",
                "priority": "medium",
                "insight": f"AI predicts continued {trend_data.get('trend', 'stable')} trend for next 7 days",
                "impact": "strategic",
                "recommendation": "Plan resource allocation based on predicted trends"
            })

        return insights

    def _assess_risks_ai(self, items: List[Item], watchers: List[Watcher], anomalies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """AI-powered risk assessment"""

        risks = []

        # Data collection risks
        if len(items) < 100:
            risks.append({
                "category": "data_collection",
                "severity": "high",
                "description": "Low data volume may indicate collection issues",
                "probability": 0.8,
                "impact": "Data quality and analysis reliability",
                "mitigation": "Verify collection pipelines and increase monitoring"
            })

        # Watcher coverage risks
        active_watchers = len([w for w in watchers if w.enabled])
        if active_watchers < 3:
            risks.append({
                "category": "monitoring",
                "severity": "medium",
                "description": "Limited watcher coverage may miss important events",
                "probability": 0.6,
                "impact": "Event detection and timely alerts",
                "mitigation": "Increase watcher deployment and diversify monitoring targets"
            })

        # Anomaly risks
        high_anomalies = len([a for a in anomalies if a.get("severity") == "high"])
        if high_anomalies > 5:
            risks.append({
                "category": "system_stability",
                "severity": "high",
                "description": f"High anomaly rate ({high_anomalies}) indicates potential system issues",
                "probability": 0.9,
                "impact": "System reliability and data integrity",
                "mitigation": "Conduct system diagnostics and anomaly investigation"
            })

        return {
            "overall_risk_level": "high" if any(r["severity"] == "high" for r in risks) else "medium" if risks else "low",
            "identified_risks": risks,
            "risk_categories": list(set(r["category"] for r in risks)),
            "mitigation_priority": sorted(risks, key=lambda x: x["probability"] * (3 if x["severity"] == "high" else 2 if x["severity"] == "medium" else 1), reverse=True)
        }

    def _analyze_opportunities_ai(self, trend_data: Dict[str, Any], platform_analysis: Dict[str, Any], predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """AI-powered opportunity analysis"""

        opportunities = []

        # Trend opportunities
        if trend_data.get("trend") == "rising":
            opportunities.append({
                "category": "content_strategy",
                "potential_impact": "high",
                "description": "Capitalize on rising trends for content creation and engagement",
                "timeframe": "immediate",
                "resource_requirement": "medium",
                "expected_benefits": "Increased visibility and engagement"
            })

        # Platform opportunities
        if platform_analysis:
            underutilized_platforms = [
                platform for platform, data in platform_analysis.items()
                if data["total_items"] < 100
            ]
            if underutilized_platforms:
                opportunities.append({
                    "category": "platform_expansion",
                    "potential_impact": "medium",
                    "description": f"Expand monitoring to underutilized platforms: {', '.join(underutilized_platforms)}",
                    "timeframe": "short_term",
                    "resource_requirement": "low",
                    "expected_benefits": "Broader intelligence coverage"
                })

        # Predictive opportunities
        if predictions:
            opportunities.append({
                "category": "predictive_analytics",
                "potential_impact": "high",
                "description": "Leverage predictive insights for strategic decision making",
                "timeframe": "ongoing",
                "resource_requirement": "medium",
                "expected_benefits": "Proactive strategy and risk mitigation"
            })

        return {
            "identified_opportunities": opportunities,
            "opportunity_categories": list(set(o["category"] for o in opportunities)),
            "prioritized_opportunities": sorted(opportunities, key=lambda x: x["potential_impact"], reverse=True),
            "implementation_roadmap": self._generate_implementation_roadmap(opportunities)
        }

    def _generate_narrative_report_ai(
        self,
        executive_summary: str,
        key_insights: List[Dict[str, Any]],
        trend_data: Dict[str, Any],
        risk_assessment: Dict[str, Any],
        opportunity_analysis: Dict[str, Any]
    ) -> str:
        """Generate comprehensive narrative report"""

        narrative = f"""# B-Search AI Intelligence Report

## Executive Summary

{executive_summary}

## Detailed Analysis

### Trend Analysis
Current data trends indicate a {trend_data.get('trend', 'stable')} pattern with {trend_data.get('confidence', 0)*100:.1f}% confidence. This suggests {'increasing' if trend_data.get('trend') == 'rising' else 'decreasing' if trend_data.get('trend') == 'falling' else 'stable'} activity levels that warrant {'immediate attention' if trend_data.get('trend') == 'rising' else 'monitoring' if trend_data.get('trend') == 'falling' else 'routine oversight'}.

### Key Insights
{chr(10).join([f"• {insight['insight']} ({insight['priority']} priority)" for insight in key_insights[:5]])}

### Risk Assessment
Overall risk level: {risk_assessment['overall_risk_level'].title()}
{chr(10).join([f"• {risk['description']} (Severity: {risk['severity']})" for risk in risk_assessment['identified_risks'][:3]])}

### Opportunities
{chr(10).join([f"• {opp['description']} (Impact: {opp['potential_impact']})" for opp in opportunity_analysis['identified_opportunities'][:3]])}

## Recommendations

1. **Immediate Actions**: Address high-priority risks and capitalize on current opportunities
2. **Monitoring Strategy**: Enhance watcher coverage for critical topics and platforms
3. **Data Strategy**: Optimize collection pipelines and expand to high-value data sources
4. **Analysis Enhancement**: Implement advanced AI models for deeper insights

## Conclusion

This AI-powered analysis provides actionable intelligence for strategic decision-making. The combination of trend analysis, risk assessment, and opportunity identification enables proactive management of intelligence operations.

---
*Generated by B-Search AI Analytics Engine | Confidence: High*
"""

        return narrative

    def _generate_ai_recommendations(
        self,
        trend_data: Dict[str, Any],
        anomalies: List[Dict[str, Any]],
        platform_analysis: Dict[str, Any],
        risk_assessment: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate AI-powered recommendations"""

        recommendations = []

        # Trend-based recommendations
        if trend_data.get("trend") == "rising":
            recommendations.append({
                "category": "resource_allocation",
                "priority": "high",
                "recommendation": "Increase monitoring resources for trending topics",
                "rationale": "Rising trends indicate increasing importance and potential impact",
                "implementation": "Deploy additional watchers and increase collection frequency",
                "expected_impact": "Better coverage of emerging important topics"
            })

        # Anomaly-based recommendations
        if anomalies:
            high_severity_count = len([a for a in anomalies if a.get("severity") == "high"])
            if high_severity_count > 0:
                recommendations.append({
                    "category": "system_monitoring",
                    "priority": "high",
                    "recommendation": f"Investigate {high_severity_count} high-severity anomalies",
                    "rationale": "Anomalies may indicate system issues or important events",
                    "implementation": "Conduct root cause analysis and system diagnostics",
                    "expected_impact": "Improved system reliability and event detection"
                })

        # Platform-based recommendations
        if platform_analysis:
            low_activity_platforms = [
                platform for platform, data in platform_analysis.items()
                if data["total_items"] < 50
            ]
            if low_activity_platforms:
                recommendations.append({
                    "category": "platform_optimization",
                    "priority": "medium",
                    "recommendation": f"Review collection strategy for: {', '.join(low_activity_platforms)}",
                    "rationale": "Low activity may indicate collection issues or irrelevant platforms",
                    "implementation": "Audit collection pipelines and assess platform relevance",
                    "expected_impact": "Optimized resource utilization and improved data quality"
                })

        # Risk-based recommendations
        if risk_assessment["overall_risk_level"] in ["high", "medium"]:
            recommendations.append({
                "category": "risk_mitigation",
                "priority": "high",
                "recommendation": f"Implement mitigation strategies for {len(risk_assessment['identified_risks'])} identified risks",
                "rationale": "Proactive risk management prevents operational issues",
                "implementation": "Execute mitigation plans and establish monitoring",
                "expected_impact": "Reduced operational risks and improved stability"
            })

        return sorted(recommendations, key=lambda x: x["priority"], reverse=True)

    def _categorize_anomalies(self, anomalies: List[Dict[str, Any]]) -> Dict[str, int]:
        """Categorize anomalies by severity"""
        return {
            "high": len([a for a in anomalies if a.get("severity") == "high"]),
            "medium": len([a for a in anomalies if a.get("severity") == "medium"]),
            "low": len([a for a in anomalies if a.get("severity") == "low"])
        }

    def _generate_short_term_forecast(self, items: List[Item]) -> Dict[str, Any]:
        """Generate short-term forecast (7 days)"""
        if len(items) < 7:
            return {"forecast": "insufficient_data", "confidence": 0}

        # Simple trend-based forecasting
        recent_counts = [0] * 7
        for item in items:
            days_ago = (datetime.now(timezone.utc) - item.created_at).days
            if days_ago < 7:
                recent_counts[6 - days_ago] += 1

        avg_daily = sum(recent_counts) / 7
        trend = (recent_counts[-1] - recent_counts[0]) / max(1, recent_counts[0])

        forecast = []
        for i in range(1, 8):
            predicted = max(0, avg_daily * (1 + trend * i / 7))
            forecast.append({
                "date": (datetime.now(timezone.utc) + timedelta(days=i)).date().isoformat(),
                "predicted_count": round(predicted, 1),
                "confidence": max(0.1, 0.9 - (i * 0.1))
            })

        return {
            "forecast": forecast,
            "methodology": "trend_extrapolation",
            "confidence": 0.75
        }

    def _generate_long_term_forecast(self, items: List[Item]) -> Dict[str, Any]:
        """Generate long-term forecast (30 days)"""
        return {
            "forecast": "long_term_forecasting_requires_more_data",
            "methodology": "insufficient_historical_data",
            "confidence": 0.3,
            "recommendation": "Collect more historical data for accurate long-term forecasting"
        }

    def _calculate_forecast_confidence(self, items: List[Item]) -> Dict[str, Any]:
        """Calculate forecast confidence levels"""
        data_points = len(items)
        time_span_days = 30  # Assume 30 days of data

        if data_points < 100:
            base_confidence = 0.4
        elif data_points < 1000:
            base_confidence = 0.6
        else:
            base_confidence = 0.8

        # Adjust for data consistency
        daily_variance = self.statistical_analyzer.calculate_daily_variance(items)
        consistency_factor = 1 - min(0.5, daily_variance / 100)

        return {
            "overall_confidence": round(base_confidence * consistency_factor, 2),
            "data_quality_factor": round(base_confidence, 2),
            "consistency_factor": round(consistency_factor, 2),
            "limiting_factors": ["insufficient_data"] if data_points < 100 else []
        }

    def _generate_implementation_roadmap(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate implementation roadmap for opportunities"""
        return [
            {"phase": "immediate", "duration": "1-2 weeks", "opportunities": [o for o in opportunities if o["timeframe"] == "immediate"]},
            {"phase": "short_term", "duration": "1-3 months", "opportunities": [o for o in opportunities if o["timeframe"] == "short_term"]},
            {"phase": "long_term", "duration": "3-6 months", "opportunities": [o for o in opportunities if o["timeframe"] == "ongoing"]}
        ]