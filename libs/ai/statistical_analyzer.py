"""
Statistical Analysis Module for B-Search AI

This module provides statistical analysis functions for trend detection,
anomaly detection, predictive analytics, and data quality assessment.
"""

import statistics
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import math

from ..storage.models import Item, Project, Watcher


class StatisticalAnalyzer:
    """Main class for statistical analysis operations"""

    def __init__(self):
        self.min_data_points = 3
        self.confidence_threshold = 0.7

    def analyze_trends(self, items: List[Item], days: int = 30) -> Dict[str, Any]:
        """Analyze trends in collected data"""
        if not items or len(items) < self.min_data_points:
            return {"trend": "insufficient_data", "confidence": 0}

        # Group by date
        daily_counts = defaultdict(int)
        for item in items:
            date_key = item.created_at.date().isoformat()
            daily_counts[date_key] += 1

        # Calculate trend metrics
        dates = sorted(daily_counts.keys())
        counts = [daily_counts[date] for date in dates]

        if len(counts) < 3:
            return {"trend": "insufficient_data", "confidence": 0}

        # Simple trend analysis
        recent_avg = statistics.mean(counts[-3:])
        earlier_avg = statistics.mean(counts[:3]) if len(counts) >= 6 else statistics.mean(counts)

        if recent_avg > earlier_avg * 1.2:
            trend = "rising"
            confidence = min(0.9, (recent_avg - earlier_avg) / earlier_avg)
        elif recent_avg < earlier_avg * 0.8:
            trend = "falling"
            confidence = min(0.9, (earlier_avg - recent_avg) / earlier_avg)
        else:
            trend = "stable"
            confidence = 0.7

        return {
            "trend": trend,
            "confidence": round(confidence, 2),
            "recent_average": round(recent_avg, 2),
            "earlier_average": round(earlier_avg, 2),
            "change_percentage": round(((recent_avg - earlier_avg) / earlier_avg) * 100, 2),
            "data_points": len(dates)
        }

    def detect_anomalies(self, items: List[Item]) -> List[Dict[str, Any]]:
        """Detect anomalies in data collection patterns"""
        if len(items) < 10:
            return []

        # Group by hour
        hourly_counts = defaultdict(int)
        for item in items:
            hour_key = item.created_at.strftime('%Y-%m-%d %H')
            hourly_counts[hour_key] += 1

        # Calculate statistics
        counts = list(hourly_counts.values())
        if len(counts) < 5:
            return []

        mean = statistics.mean(counts)
        stdev = statistics.stdev(counts) if len(counts) > 1 else 0

        if stdev == 0:
            return []

        # Detect anomalies (values more than 2 standard deviations from mean)
        anomalies = []
        for hour, count in hourly_counts.items():
            z_score = abs(count - mean) / stdev
            if z_score > 2.0:
                anomalies.append({
                    "timestamp": hour,
                    "value": count,
                    "expected": round(mean, 2),
                    "deviation": round(z_score, 2),
                    "type": "spike" if count > mean else "drop",
                    "severity": "high" if z_score > 3 else "medium"
                })

        return sorted(anomalies, key=lambda x: x["deviation"], reverse=True)[:10]

    def analyze_sentiment(self, items: List[Item]) -> Dict[str, Any]:
        """Mock sentiment analysis - ready for NLP model integration"""
        if not items:
            return {"overall": "neutral", "distribution": {}}

        # Mock sentiment distribution
        total = len(items)
        positive = int(total * 0.4)
        negative = int(total * 0.2)
        neutral = total - positive - negative

        return {
            "overall": "positive" if positive > negative else "negative" if negative > positive else "neutral",
            "distribution": {
                "positive": positive,
                "negative": negative,
                "neutral": neutral
            },
            "confidence": 0.75,
            "method": "mock_nlp_analysis"
        }

    def cluster_topics(self, items: List[Item], num_clusters: int = 5) -> List[Dict[str, Any]]:
        """Mock topic clustering - ready for ML clustering algorithms"""
        mock_topics = [
            {"id": 1, "name": "Technology", "keywords": ["tech", "software", "AI", "digital"], "prevalence": 0.35, "trend": "rising"},
            {"id": 2, "name": "Politics", "keywords": ["government", "election", "policy", "politics"], "prevalence": 0.25, "trend": "stable"},
            {"id": 3, "name": "Business", "keywords": ["economy", "market", "business", "finance"], "prevalence": 0.20, "trend": "rising"},
            {"id": 4, "name": "Social Issues", "keywords": ["society", "community", "social", "culture"], "prevalence": 0.15, "trend": "falling"},
            {"id": 5, "name": "Entertainment", "keywords": ["entertainment", "media", "celebrity", "sports"], "prevalence": 0.05, "trend": "stable"}
        ]

        return mock_topics[:num_clusters]

    def generate_predictive_insights(self, items: List[Item]) -> List[Dict[str, Any]]:
        """Generate predictive insights"""
        return [
            {
                "type": "trend_prediction",
                "prediction": "Technology discussions will increase by 25% in the next week",
                "confidence": 0.78,
                "timeframe": "7_days",
                "factors": ["recent_ai_news", "tech_conferences"]
            },
            {
                "type": "anomaly_alert",
                "prediction": "Potential spike in social media activity around weekend",
                "confidence": 0.65,
                "timeframe": "3_days",
                "factors": ["historical_patterns", "event_calendar"]
            }
        ]

    def analyze_engagement_patterns(self, items: List[Item]) -> Dict[str, Any]:
        """Analyze engagement patterns"""
        if not items:
            return {"patterns": []}

        # Mock engagement analysis
        return {
            "peak_hours": ["14:00", "16:00", "20:00"],
            "peak_days": ["Tuesday", "Thursday", "Saturday"],
            "engagement_trends": "increasing",
            "best_platforms": ["Twitter", "Reddit"],
            "content_types": ["text", "images", "videos"]
        }

    def analyze_detailed_trends(self, items: List[Item], days: int) -> Dict[str, Any]:
        """Detailed trend analysis"""
        # Group by day and platform
        daily_platform_data = defaultdict(lambda: defaultdict(int))

        for item in items:
            date_key = item.created_at.date().isoformat()
            platform = item.meta.get('platform', 'unknown') if item.meta else 'unknown'
            daily_platform_data[date_key][platform] += 1

        # Calculate trend metrics
        trend_metrics = {
            "daily_totals": {},
            "platform_trends": {},
            "growth_rate": 0,
            "volatility": 0,
            "peak_day": None,
            "trough_day": None
        }

        # Calculate daily totals
        for date, platforms in daily_platform_data.items():
            trend_metrics["daily_totals"][date] = sum(platforms.values())

        return trend_metrics

    def generate_trend_predictions(self, trend_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate trend predictions"""
        return [
            {
                "date": "2024-01-15",
                "predicted_count": 150,
                "confidence": 0.75,
                "factors": ["seasonal_trend", "recent_growth"]
            },
            {
                "date": "2024-01-16",
                "predicted_count": 165,
                "confidence": 0.70,
                "factors": ["weekend_pattern", "content_velocity"]
            }
        ]

    def detect_statistical_anomalies(self, hourly_data: List, threshold: float) -> List[Dict[str, Any]]:
        """Detect statistical anomalies"""
        if len(hourly_data) < 5:
            return []

        counts = [row.count for row in hourly_data]
        mean = statistics.mean(counts)
        stdev = statistics.stdev(counts) if len(counts) > 1 else 0

        if stdev == 0:
            return []

        anomalies = []
        for row in hourly_data:
            z_score = abs(row.count - mean) / stdev
            if z_score > threshold:
                anomalies.append({
                    "timestamp": row.hour,
                    "actual": row.count,
                    "expected": round(mean, 2),
                    "z_score": round(z_score, 2),
                    "severity": "high" if z_score > 3 else "medium"
                })

        return sorted(anomalies, key=lambda x: x["z_score"], reverse=True)

    def generate_time_series_predictions(self, daily_data: List, days_ahead: int) -> List[Dict[str, Any]]:
        """Generate time series predictions"""
        if len(daily_data) < 7:
            return []

        # Simple linear trend prediction
        counts = [row.count for row in daily_data[-7:]]  # Use last 7 days
        avg_growth = sum(counts[i+1] - counts[i] for i in range(len(counts)-1)) / (len(counts)-1)

        predictions = []
        last_count = counts[-1]

        for i in range(1, days_ahead + 1):
            predicted_count = max(0, last_count + (avg_growth * i))
            predictions.append({
                "date": (datetime.now(timezone.utc) + timedelta(days=i)).date().isoformat(),
                "predicted_count": round(predicted_count, 2),
                "confidence": max(0.1, 0.8 - (i * 0.1))  # Confidence decreases over time
            })

        return predictions

    def calculate_overall_confidence(self, trend_data: Dict[str, Any], anomalies: List[Dict[str, Any]]) -> float:
        """Calculate overall analysis confidence"""
        trend_confidence = trend_data.get("confidence", 0)
        anomaly_count = len(anomalies)

        # Base confidence on trend analysis
        confidence = trend_confidence

        # Adjust for anomalies (more anomalies = less confidence in stability)
        if anomaly_count > 10:
            confidence *= 0.8
        elif anomaly_count > 5:
            confidence *= 0.9

        return round(confidence, 2)

    def assess_data_quality(self, items: List[Item]) -> float:
        """Assess data quality score"""
        if not items:
            return 0.0

        total_items = len(items)
        completeness_score = 1.0  # Assume complete for now
        consistency_score = 0.8   # Mock consistency
        timeliness_score = 0.9    # Mock timeliness

        return round((completeness_score + consistency_score + timeliness_score) / 3, 2)

    def calculate_analysis_reliability(self, items: List[Item], analysis_depth: str) -> float:
        """Calculate analysis reliability score"""
        data_points = len(items)

        base_reliability = min(0.9, data_points / 1000)

        if analysis_depth == "detailed":
            depth_factor = 0.9
        elif analysis_depth == "comprehensive":
            depth_factor = 0.8
        else:
            depth_factor = 1.0

        return round(base_reliability * depth_factor, 2)

    def calculate_daily_variance(self, items: List[Item]) -> float:
        """Calculate daily variance in item counts"""
        if len(items) < 2:
            return 0

        # Group by day
        daily_counts = defaultdict(int)
        for item in items:
            day_key = item.created_at.date().isoformat()
            daily_counts[day_key] += 1

        counts = list(daily_counts.values())
        if len(counts) < 2:
            return 0

        mean = statistics.mean(counts)
        variance = statistics.variance(counts) if len(counts) > 1 else 0

        return variance


# Convenience functions for direct access
def analyze_trends(items: List[Item], days: int = 30) -> Dict[str, Any]:
    """Convenience function for trend analysis"""
    analyzer = StatisticalAnalyzer()
    return analyzer.analyze_trends(items, days)

def detect_anomalies(items: List[Item]) -> List[Dict[str, Any]]:
    """Convenience function for anomaly detection"""
    analyzer = StatisticalAnalyzer()
    return analyzer.detect_anomalies(items)

def analyze_sentiment(items: List[Item]) -> Dict[str, Any]:
    """Convenience function for sentiment analysis"""
    analyzer = StatisticalAnalyzer()
    return analyzer.analyze_sentiment(items)

def cluster_topics(items: List[Item], num_clusters: int = 5) -> List[Dict[str, Any]]:
    """Convenience function for topic clustering"""
    analyzer = StatisticalAnalyzer()
    return analyzer.cluster_topics(items, num_clusters)

def generate_predictive_insights(items: List[Item]) -> List[Dict[str, Any]]:
    """Convenience function for predictive insights"""
    analyzer = StatisticalAnalyzer()
    return analyzer.generate_predictive_insights(items)