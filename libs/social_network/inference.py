"""
Relationship Inference Algorithms

This module provides algorithms for inferring relationships that may not be
explicitly stated in the data, including:
- Implicit relationships based on behavioral patterns
- Temporal relationship analysis
- Cross-platform relationship linking
- Relationship strength prediction
"""

from typing import List, Dict, Any, Set, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import math

from .models import SocialGraph, Person, Relationship
from .graph_algorithms import GraphAlgorithms


class RelationshipInference:
    """Advanced relationship inference algorithms"""

    def __init__(self, graph: SocialGraph):
        self.graph = graph
        self.algorithms = GraphAlgorithms(graph)

    def infer_implicit_relationships(self, confidence_threshold: float = 0.6) -> List[Dict[str, Any]]:
        """Infer implicit relationships based on behavioral patterns"""
        inferred_relationships = []

        # Pattern 1: Mutual mentions without direct interaction
        mutual_mentions = self._find_mutual_mentions_pattern()
        for person1, person2, strength in mutual_mentions:
            if strength >= confidence_threshold:
                inferred_relationships.append({
                    "source": person1,
                    "target": person2,
                    "type": "inferred_mutual_interest",
                    "strength": strength,
                    "evidence": "mutual_mentions",
                    "confidence": strength
                })

        # Pattern 2: Shared content networks
        shared_content_networks = self._find_shared_content_networks()
        for person1, person2, strength in shared_content_networks:
            if strength >= confidence_threshold:
                inferred_relationships.append({
                    "source": person1,
                    "target": person2,
                    "type": "inferred_shared_interests",
                    "strength": strength,
                    "evidence": "shared_content_network",
                    "confidence": strength
                })

        # Pattern 3: Temporal co-occurrence
        temporal_patterns = self._find_temporal_cooccurrence_patterns()
        for person1, person2, strength in temporal_patterns:
            if strength >= confidence_threshold:
                inferred_relationships.append({
                    "source": person1,
                    "target": person2,
                    "type": "inferred_temporal_association",
                    "strength": strength,
                    "evidence": "temporal_cooccurrence",
                    "confidence": strength
                })

        return inferred_relationships

    def predict_relationship_strength(self, person1_id: str, person2_id: str) -> Dict[str, Any]:
        """Predict the strength of relationship between two people"""
        if person1_id not in self.graph.people or person2_id not in self.graph.people:
            return {"predicted_strength": 0, "confidence": 0}

        # Get existing relationship if any
        existing_strength = self.graph.get_relationship_strength(person1_id, person2_id)

        # Calculate prediction factors
        factors = {
            "direct_connection": existing_strength,
            "mutual_friends": len(self.graph.get_mutual_connections(person1_id, person2_id)),
            "shared_platforms": self._count_shared_platforms(person1_id, person2_id),
            "interaction_frequency": self._calculate_interaction_frequency(person1_id, person2_id),
            "content_similarity": self._calculate_content_similarity(person1_id, person2_id),
            "temporal_proximity": self._calculate_temporal_proximity(person1_id, person2_id)
        }

        # Weighted prediction model
        weights = {
            "direct_connection": 0.4,
            "mutual_friends": 0.2,
            "shared_platforms": 0.1,
            "interaction_frequency": 0.1,
            "content_similarity": 0.1,
            "temporal_proximity": 0.1
        }

        predicted_strength = sum(factors[key] * weights[key] for key in factors.keys())
        confidence = self._calculate_prediction_confidence(factors)

        return {
            "predicted_strength": min(1.0, predicted_strength),
            "confidence": confidence,
            "factors": factors,
            "existing_strength": existing_strength
        }

    def infer_cross_platform_relationships(self) -> List[Dict[str, Any]]:
        """Infer relationships across different platforms"""
        cross_platform_relationships = []

        # Group people by username/handle across platforms
        username_groups = defaultdict(list)

        for person in self.graph.people.values():
            # Normalize username for matching
            normalized_username = self._normalize_username(person.username or "")
            if normalized_username:
                username_groups[normalized_username].append(person)

        # Find potential cross-platform matches
        for username, people in username_groups.items():
            if len(people) > 1:
                # Calculate similarity between profiles
                for i, person1 in enumerate(people):
                    for person2 in people[i+1:]:
                        similarity = self._calculate_profile_similarity(person1, person2)
                        if similarity > 0.7:  # High confidence threshold
                            cross_platform_relationships.append({
                                "person1": person1.id,
                                "person2": person2.id,
                                "username": username,
                                "similarity_score": similarity,
                                "platforms": [person1.platform, person2.platform],
                                "confidence": similarity
                            })

        return cross_platform_relationships

    def predict_future_interactions(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Predict future interactions between people"""
        predictions = []

        # Analyze historical interaction patterns
        for person1_id in self.graph.people.keys():
            for person2_id in self.graph.people.keys():
                if person1_id != person2_id:
                    prediction = self._predict_pair_interaction(person1_id, person2_id, days_ahead)
                    if prediction["probability"] > 0.3:  # Only include likely interactions
                        predictions.append({
                            "person1": person1_id,
                            "person2": person2_id,
                            "predicted_interaction": prediction["probability"],
                            "timeframe_days": days_ahead,
                            "confidence": prediction["confidence"]
                        })

        return sorted(predictions, key=lambda x: x["predicted_interaction"], reverse=True)[:50]

    def _find_mutual_mentions_pattern(self) -> List[Tuple[str, str, float]]:
        """Find patterns of mutual mentions without direct replies"""
        mutual_patterns = []

        # Create mention graph
        mention_graph = defaultdict(set)

        for rel in self.graph.relationships.values():
            if rel.relationship_type == "mention":
                mention_graph[rel.source_id].add(rel.target_id)

        # Find mutual mentions
        for person1 in mention_graph:
            for person2 in mention_graph:
                if (person1 != person2 and
                    person2 in mention_graph[person1] and
                    person1 in mention_graph[person2]):
                    # Calculate mutual mention strength
                    strength = min(
                        len([r for r in self.graph.relationships.values()
                             if r.source_id == person1 and r.target_id == person2 and r.relationship_type == "mention"]),
                        len([r for r in self.graph.relationships.values()
                             if r.source_id == person2 and r.target_id == person1 and r.relationship_type == "mention"])
                    ) / 10.0  # Normalize

                    mutual_patterns.append((person1, person2, min(1.0, strength)))

        return mutual_patterns

    def _find_shared_content_networks(self) -> List[Tuple[str, str, float]]:
        """Find networks of people who share similar content"""
        shared_content_patterns = []

        # Group people by shared content
        content_sharers = defaultdict(set)

        for rel in self.graph.relationships.values():
            if rel.relationship_type == "shared_content":
                for content_id in rel.shared_content:
                    content_sharers[content_id].add(rel.source_id)

        # Find people who share content with similar groups
        person_similarity = defaultdict(lambda: defaultdict(float))

        for content_id, sharers in content_sharers.items():
            sharers_list = list(sharers)
            for i, person1 in enumerate(sharers_list):
                for person2 in sharers_list[i+1:]:
                    person_similarity[person1][person2] += 1.0 / len(sharers_list)

        # Convert to list
        for person1 in person_similarity:
            for person2, similarity in person_similarity[person1].items():
                if similarity > 0.3:  # Minimum similarity threshold
                    shared_content_patterns.append((person1, person2, min(1.0, similarity)))

        return shared_content_patterns

    def _find_temporal_cooccurrence_patterns(self) -> List[Tuple[str, str, float]]:
        """Find patterns of temporal co-occurrence"""
        temporal_patterns = []

        # Group interactions by time windows
        time_windows = defaultdict(set)

        for rel in self.graph.relationships.values():
            if rel.first_interaction:
                # Create time window (e.g., hourly)
                window = rel.first_interaction.strftime('%Y-%m-%d %H')
                time_windows[window].add(rel.source_id)
                time_windows[window].add(rel.target_id)

        # Find co-occurring people
        cooccurrence_counts = defaultdict(lambda: defaultdict(int))

        for window, people in time_windows.items():
            people_list = list(people)
            for i, person1 in enumerate(people_list):
                for person2 in people_list[i+1:]:
                    cooccurrence_counts[person1][person2] += 1

        # Calculate co-occurrence strength
        max_cooccurrences = max(
            (count for person_counts in cooccurrence_counts.values()
             for count in person_counts.values()),
            default=1
        )

        for person1 in cooccurrence_counts:
            for person2, count in cooccurrence_counts[person1].items():
                strength = count / max_cooccurrences
                if strength > 0.2:  # Minimum threshold
                    temporal_patterns.append((person1, person2, strength))

        return temporal_patterns

    def _count_shared_platforms(self, person1_id: str, person2_id: str) -> float:
        """Count shared platforms between two people"""
        person1 = self.graph.get_person(person1_id)
        person2 = self.graph.get_person(person2_id)

        if not person1 or not person2:
            return 0

        # Get all platforms each person is active on
        person1_platforms = set()
        person2_platforms = set()

        for rel in self.graph.relationships.values():
            if rel.source_id == person1_id:
                person1_platforms.update(rel.platforms)
            elif rel.source_id == person2_id:
                person2_platforms.update(rel.platforms)

        if not person1_platforms or not person2_platforms:
            return 0

        shared = len(person1_platforms.intersection(person2_platforms))
        total = len(person1_platforms.union(person2_platforms))

        return shared / total if total > 0 else 0

    def _calculate_interaction_frequency(self, person1_id: str, person2_id: str) -> float:
        """Calculate interaction frequency between two people"""
        interactions = 0
        total_possible_interactions = 0

        # Count actual interactions
        for rel in self.graph.relationships.values():
            if ((rel.source_id == person1_id and rel.target_id == person2_id) or
                (rel.source_id == person2_id and rel.target_id == person1_id)):
                interactions += rel.interaction_count

        # Estimate total possible interactions (simplified)
        person1_rels = len([r for r in self.graph.relationships.values() if r.source_id == person1_id])
        person2_rels = len([r for r in self.graph.relationships.values() if r.source_id == person2_id])

        if person1_rels > 0 and person2_rels > 0:
            total_possible_interactions = (person1_rels + person2_rels) / 2

        return interactions / total_possible_interactions if total_possible_interactions > 0 else 0

    def _calculate_content_similarity(self, person1_id: str, person2_id: str) -> float:
        """Calculate content similarity between two people"""
        # This would require content analysis - simplified version
        return 0.5  # Placeholder

    def _calculate_temporal_proximity(self, person1_id: str, person2_id: str) -> float:
        """Calculate temporal proximity of interactions"""
        person1_times = []
        person2_times = []

        for rel in self.graph.relationships.values():
            if rel.first_interaction:
                if rel.source_id == person1_id or rel.target_id == person1_id:
                    person1_times.append(rel.first_interaction.timestamp())
                if rel.source_id == person2_id or rel.target_id == person2_id:
                    person2_times.append(rel.first_interaction.timestamp())

        if not person1_times or not person2_times:
            return 0

        # Calculate average time difference
        avg_time_diff = 0
        count = 0

        for t1 in person1_times:
            for t2 in person2_times:
                avg_time_diff += abs(t1 - t2)
                count += 1

        if count > 0:
            avg_time_diff /= count

        # Convert to similarity score (closer in time = higher similarity)
        max_diff = 30 * 24 * 60 * 60  # 30 days in seconds
        return max(0, 1 - (avg_time_diff / max_diff))

    def _calculate_prediction_confidence(self, factors: Dict[str, float]) -> float:
        """Calculate confidence in relationship strength prediction"""
        # Higher confidence when more factors are available
        available_factors = sum(1 for v in factors.values() if v > 0)
        total_factors = len(factors)

        base_confidence = available_factors / total_factors

        # Adjust based on factor consistency
        factor_values = [v for v in factors.values() if v > 0]
        if len(factor_values) > 1:
            consistency = 1 - (max(factor_values) - min(factor_values))
            base_confidence *= (0.5 + 0.5 * consistency)

        return min(1.0, base_confidence)

    def _normalize_username(self, username: str) -> str:
        """Normalize username for cross-platform matching"""
        if not username:
            return ""

        # Keep only alphanumeric characters (tests expect underscores removed)
        normalized = "".join(c for c in username.lower() if c.isalnum())
        return normalized

    def _calculate_profile_similarity(self, person1: Person, person2: Person) -> float:
        """Calculate similarity between two profiles"""
        similarity_score = 0
        factors = 0

        # Name similarity (simplified)
        if person1.name and person2.name:
            name1_words = set(person1.name.lower().split())
            name2_words = set(person2.name.lower().split())
            name_similarity = len(name1_words.intersection(name2_words)) / len(name1_words.union(name2_words))
            similarity_score += name_similarity
            factors += 1

        # Bio similarity (simplified)
        if person1.bio and person2.bio:
            bio1_words = set(person1.bio.lower().split())
            bio2_words = set(person2.bio.lower().split())
            bio_similarity = len(bio1_words.intersection(bio2_words)) / len(bio1_words.union(bio2_words))
            similarity_score += bio_similarity
            factors += 1

        # Location similarity
        if person1.location and person2.location and person1.location == person2.location:
            similarity_score += 1.0
            factors += 1

        return similarity_score / factors if factors > 0 else 0

    def _predict_pair_interaction(self, person1_id: str, person2_id: str, days_ahead: int) -> Dict[str, Any]:
        """Predict future interaction between a pair"""
        # Simplified prediction based on historical patterns
        existing_interactions = [
            rel for rel in self.graph.relationships.values()
            if ((rel.source_id == person1_id and rel.target_id == person2_id) or
                (rel.source_id == person2_id and rel.target_id == person1_id))
        ]

        if not existing_interactions:
            return {"probability": 0, "confidence": 0}

        # Calculate interaction frequency
        total_interactions = sum(rel.interaction_count for rel in existing_interactions)
        time_span_days = 30  # Assume 30 days of history

        daily_frequency = total_interactions / time_span_days

        # Predict future probability
        predicted_probability = min(1.0, daily_frequency * days_ahead)

        # Calculate confidence based on data availability
        confidence = min(1.0, total_interactions / 10)  # More interactions = higher confidence

        return {
            "probability": predicted_probability,
            "confidence": confidence
        }