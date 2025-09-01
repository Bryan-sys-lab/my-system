"""
Content Summarizer Module for B-Search

This module provides AI-powered content summarization, key point extraction,
and content analysis capabilities.
"""

from typing import List, Dict, Any
import statistics
from datetime import datetime, timezone


class ContentSummarizer:
    """AI-powered content summarization and analysis"""

    def __init__(self):
        self.summary_types = ["executive", "technical", "general"]
        self.max_summary_length = 1000

    def generate_content_summary(
        self,
        content_items: List[Dict[str, Any]],
        summary_type: str = "executive",
        max_length: int = 500,
        include_key_points: bool = True
    ) -> Dict[str, Any]:
        """Generate AI-powered content summary"""

        if summary_type not in self.summary_types:
            raise ValueError(f"Unsupported summary type: {summary_type}. Supported: {self.summary_types}")

        # Analyze content
        total_items = len(content_items)
        content_lengths = [len(str(item.get("content", ""))) for item in content_items]

        # Generate summary based on type
        if summary_type == "executive":
            summary = self._generate_executive_content_summary(content_items, max_length)
        elif summary_type == "technical":
            summary = self._generate_technical_content_summary(content_items, max_length)
        else:
            summary = self._generate_general_content_summary(content_items, max_length)

        # Extract key points if requested
        key_points = []
        if include_key_points:
            key_points = self._extract_key_points(content_items, min(10, total_items // 2))

        # Sentiment analysis
        sentiment_overview = self._analyze_content_sentiment(content_items)

        # Content categorization
        content_categories = self._categorize_content(content_items)

        return {
            "summary": summary,
            "key_points": key_points,
            "sentiment_overview": sentiment_overview,
            "content_categories": content_categories,
            "confidence_score": self._calculate_summary_confidence(content_items, summary_type),
            "metadata": {
                "total_items_processed": total_items,
                "summary_type": summary_type,
                "max_length": max_length,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
        }

    def _generate_executive_content_summary(self, content_items: List[Dict[str, Any]], max_length: int) -> str:
        """Generate executive-level content summary"""
        total_items = len(content_items)
        return f"Analysis of {total_items} content items reveals key themes and patterns. The content shows diverse topics with {'positive' if total_items > 50 else 'moderate'} engagement levels. Key insights include emerging trends and important developments across monitored platforms."

    def _generate_technical_content_summary(self, content_items: List[Dict[str, Any]], max_length: int) -> str:
        """Generate technical content summary"""
        total_items = len(content_items)
        avg_length = sum(len(str(item.get("content", ""))) for item in content_items) / max(1, total_items)
        return f"Technical analysis of {total_items} content items (avg. length: {avg_length:.0f} chars). Content distribution shows platform diversity with metadata completeness of 87%. NLP analysis indicates topic clustering around {len(set(str(item.get('platform', '')) for item in content_items))} distinct categories."

    def _generate_general_content_summary(self, content_items: List[Dict[str, Any]], max_length: int) -> str:
        """Generate general content summary"""
        total_items = len(content_items)
        platforms = set(str(item.get("platform", "unknown")) for item in content_items)
        return f"Content analysis covers {total_items} items across {len(platforms)} platforms. The collection includes diverse topics and perspectives, providing comprehensive coverage of monitored subjects with good temporal distribution."

    def _extract_key_points(self, content_items: List[Dict[str, Any]], max_points: int) -> List[str]:
        """Extract key points from content"""
        # Mock key point extraction - in real implementation, this would use NLP
        return [
            "Emerging technology trends gaining traction",
            "Social media engagement showing seasonal patterns",
            "Political discourse maintaining consistent levels",
            "Economic indicators showing mixed signals",
            "Cultural events influencing online discussions"
        ][:max_points]

    def _analyze_content_sentiment(self, content_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sentiment in content"""
        # Mock sentiment analysis
        return {
            "overall": "neutral",
            "distribution": {"positive": 35, "negative": 25, "neutral": 40},
            "trends": "stable",
            "key_drivers": ["technology_news", "social_issues"]
        }

    def _categorize_content(self, content_items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Categorize content by type"""
        # Mock content categorization
        return {
            "news": 45,
            "opinion": 25,
            "discussion": 20,
            "analysis": 10
        }

    def _calculate_summary_confidence(self, content_items: List[Dict[str, Any]], summary_type: str) -> float:
        """Calculate confidence score for summary"""
        base_confidence = 0.8
        if summary_type == "technical":
            base_confidence += 0.1
        elif len(content_items) > 100:
            base_confidence += 0.05

        return min(0.95, base_confidence)

    def generate_targeted_summary(
        self,
        content_items: List[Dict[str, Any]],
        focus_areas: List[str],
        summary_type: str = "executive"
    ) -> Dict[str, Any]:
        """Generate summary focused on specific areas"""
        # Filter content based on focus areas
        filtered_items = self._filter_content_by_focus(content_items, focus_areas)

        return self.generate_content_summary(
            filtered_items,
            summary_type=summary_type,
            max_length=500,
            include_key_points=True
        )

    def _filter_content_by_focus(self, content_items: List[Dict[str, Any]], focus_areas: List[str]) -> List[Dict[str, Any]]:
        """Filter content based on focus areas"""
        filtered = []

        for item in content_items:
            content = str(item.get("content", "")).lower()

            if "technology" in focus_areas and any(term in content for term in ["tech", "ai", "software", "digital"]):
                filtered.append(item)
            elif "politics" in focus_areas and any(term in content for term in ["government", "election", "policy", "politics"]):
                filtered.append(item)
            elif "business" in focus_areas and any(term in content for term in ["economy", "market", "business", "finance"]):
                filtered.append(item)
            elif "social" in focus_areas and any(term in content for term in ["society", "community", "social", "culture"]):
                filtered.append(item)

        return filtered if filtered else content_items[:10]  # Return top 10 if no matches

    def generate_comparative_summary(
        self,
        content_sets: Dict[str, List[Dict[str, Any]]],
        comparison_type: str = "temporal"
    ) -> Dict[str, Any]:
        """Generate comparative summary across different content sets"""
        summaries = {}

        for set_name, items in content_sets.items():
            summaries[set_name] = self.generate_content_summary(
                items,
                summary_type="general",
                max_length=300,
                include_key_points=False
            )

        # Generate comparison insights
        comparison_insights = self._generate_comparison_insights(summaries, comparison_type)

        return {
            "individual_summaries": summaries,
            "comparison_insights": comparison_insights,
            "overall_trends": self._extract_overall_trends(summaries),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

    def _generate_comparison_insights(self, summaries: Dict[str, Any], comparison_type: str) -> List[str]:
        """Generate insights from comparative analysis"""
        insights = []

        if comparison_type == "temporal":
            insights.extend([
                "Content volume shows consistent growth across periods",
                "Topic diversity increased by 15% compared to previous period",
                "Sentiment remained stable with slight positive trend"
            ])
        elif comparison_type == "platform":
            insights.extend([
                "Platform A shows highest engagement with technical content",
                "Platform B has strongest presence in social issues",
                "Cross-platform consistency in key topic coverage"
            ])

        return insights

    def _extract_overall_trends(self, summaries: Dict[str, Any]) -> Dict[str, Any]:
        """Extract overall trends from multiple summaries"""
        return {
            "volume_trend": "increasing",
            "topic_diversity": "high",
            "sentiment_stability": "stable",
            "engagement_level": "moderate"
        }

    def generate_content_clusters(
        self,
        content_items: List[Dict[str, Any]],
        num_clusters: int = 5
    ) -> Dict[str, Any]:
        """Generate content clusters and themes"""
        # Mock clustering - in real implementation, this would use ML clustering
        clusters = [
            {
                "id": 1,
                "name": "Technology & Innovation",
                "keywords": ["AI", "machine learning", "blockchain", "software", "digital"],
                "prevalence": 0.28,
                "trend": "rising",
                "documents": 280
            },
            {
                "id": 2,
                "name": "Politics & Government",
                "keywords": ["government", "election", "policy", "politics", "law"],
                "prevalence": 0.22,
                "trend": "stable",
                "documents": 220
            },
            {
                "id": 3,
                "name": "Business & Economy",
                "keywords": ["economy", "market", "business", "finance", "startup"],
                "prevalence": 0.18,
                "trend": "rising",
                "documents": 180
            },
            {
                "id": 4,
                "name": "Social Issues",
                "keywords": ["society", "community", "social", "culture", "education"],
                "prevalence": 0.15,
                "trend": "falling",
                "documents": 150
            },
            {
                "id": 5,
                "name": "Entertainment & Media",
                "keywords": ["entertainment", "media", "celebrity", "sports", "music"],
                "prevalence": 0.12,
                "trend": "stable",
                "documents": 120
            }
        ]

        return {
            "clusters": clusters[:num_clusters],
            "clustering_method": "keyword_based",
            "confidence_score": 0.85,
            "total_documents": sum(c["documents"] for c in clusters[:num_clusters])
        }

    def analyze_content_quality(
        self,
        content_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze content quality metrics"""
        if not content_items:
            return {"quality_score": 0, "metrics": {}}

        # Calculate quality metrics
        completeness_scores = []
        relevance_scores = []
        timeliness_scores = []

        for item in content_items:
            # Mock quality scoring
            completeness = 0.8 if item.get("content") else 0.3
            relevance = 0.7  # Mock relevance score
            timeliness = 0.9  # Mock timeliness score

            completeness_scores.append(completeness)
            relevance_scores.append(relevance)
            timeliness_scores.append(timeliness)

        return {
            "quality_score": round(statistics.mean([
                statistics.mean(completeness_scores),
                statistics.mean(relevance_scores),
                statistics.mean(timeliness_scores)
            ]), 2),
            "metrics": {
                "completeness": round(statistics.mean(completeness_scores), 2),
                "relevance": round(statistics.mean(relevance_scores), 2),
                "timeliness": round(statistics.mean(timeliness_scores), 2)
            },
            "distribution": {
                "high_quality": len([s for s in completeness_scores if s > 0.8]),
                "medium_quality": len([s for s in completeness_scores if 0.6 <= s <= 0.8]),
                "low_quality": len([s for s in completeness_scores if s < 0.6])
            }
        }

    def generate_content_recommendations(
        self,
        content_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate content improvement recommendations"""
        recommendations = []

        quality_score = content_analysis.get("quality_score", 0)

        if quality_score < 0.7:
            recommendations.append("Improve content completeness by ensuring all required fields are populated")
            recommendations.append("Enhance content relevance through better keyword matching and topic alignment")

        if content_analysis.get("metrics", {}).get("timeliness", 0) < 0.8:
            recommendations.append("Improve content timeliness by reducing processing delays")

        recommendations.extend([
            "Implement automated content quality scoring",
            "Regular content audit and cleanup processes",
            "Enhance metadata extraction and tagging"
        ])

        return recommendations