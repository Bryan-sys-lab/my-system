"""
Social Network Analyzer Module

This module provides advanced analysis capabilities for social networks including:
- Shared content analysis (photos, posts, media)
- Group and community analysis
- Mutual connection analysis
- Relationship strength analysis
- Influence and engagement analysis
"""

from typing import List, Dict, Any, Set, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import re

from .models import SocialGraph, Person, Relationship
from .graph_algorithms import GraphAlgorithms
from ..storage.models import Item


class SocialNetworkAnalyzer:
    """Advanced social network analyzer"""

    def __init__(self, graph: SocialGraph):
        self.graph = graph
        self.algorithms = GraphAlgorithms(graph)

    def analyze_shared_content(self, content_type: str = "all") -> Dict[str, Any]:
        """Analyze shared content patterns in the network"""
        shared_content_analysis = {
            "content_clusters": self._cluster_shared_content(),
            "popular_content": self._find_popular_content(),
            "content_flow": self._analyze_content_flow(),
            "engagement_patterns": self._analyze_engagement_patterns()
        }

        if content_type != "all":
            # Filter by content type
            pass

        return shared_content_analysis

    def analyze_groups_and_communities(self) -> Dict[str, Any]:
        """Analyze groups and communities in the network"""
        communities = self.algorithms.detect_communities()

        return {
            "communities": communities,
            "community_stats": self._analyze_community_stats(communities),
            "group_interactions": self._analyze_group_interactions(),
            "community_influence": self._analyze_community_influence(communities)
        }

    def analyze_mutual_connections(self) -> Dict[str, Any]:
        """Analyze mutual connection patterns"""
        mutual_analysis = {
            "mutual_connection_stats": self._calculate_mutual_connection_stats(),
            "triangles": self._find_triangles(),
            "bridges": self._find_bridges(),
            "cliques": self._find_cliques()
        }

        return mutual_analysis

    def analyze_relationship_strengths(self) -> Dict[str, Any]:
        """Analyze relationship strengths and patterns"""
        return {
            "strength_distribution": self._analyze_strength_distribution(),
            "relationship_evolution": self._analyze_relationship_evolution(),
            "strongest_connections": self._find_strongest_connections(),
            "weakest_connections": self._find_weakest_connections()
        }

    def analyze_influence_and_engagement(self) -> Dict[str, Any]:
        """Analyze influence and engagement patterns"""
        return {
            "influence_scores": self._calculate_influence_scores(),
            "engagement_metrics": self._calculate_engagement_metrics(),
            "content_virality": self._analyze_content_virality(),
            "network_influencers": self._identify_network_influencers()
        }

    def _cluster_shared_content(self) -> List[Dict[str, Any]]:
        """Cluster content based on shared patterns"""
        content_clusters = []

        # Group relationships by shared content
        content_groups = defaultdict(list)

        for rel in self.graph.relationships.values():
            if rel.relationship_type == "shared_content":
                for content_id in rel.shared_content:
                    content_groups[content_id].append(rel)

        # Analyze each content cluster
        for content_id, relationships in content_groups.items():
            if len(relationships) > 1:  # Only consider content shared by multiple people
                # platforms should be a set of strings
                platforms = set()
                for rel in relationships:
                    if isinstance(rel.platforms, (set, list)):
                        platforms.update(list(rel.platforms))

                cluster = {
                    "content_id": content_id,
                    "shared_by": [rel.source_id for rel in relationships],
                    "relationship_count": len(relationships),
                    "platforms": list(platforms),
                    "avg_strength": sum(rel.strength for rel in relationships) / len(relationships)
                }
                content_clusters.append(cluster)

        return sorted(content_clusters, key=lambda x: x["relationship_count"], reverse=True)

    def _find_popular_content(self) -> List[Dict[str, Any]]:
        """Find most popular content in the network"""
        content_popularity = defaultdict(lambda: {"shares": 0, "unique_shares": set(), "platforms": set()})

        for rel in self.graph.relationships.values():
            if rel.relationship_type == "shared_content":
                for content_id in rel.shared_content:
                    content_popularity[content_id]["shares"] += 1
                    content_popularity[content_id]["unique_shares"].add(rel.source_id)
                    content_popularity[content_id]["platforms"].update(rel.platforms)

        # Convert to list and sort by popularity
        popular_content = []
        for content_id, stats in content_popularity.items():
            popular_content.append({
                "content_id": content_id,
                "total_shares": stats["shares"],
                "unique_shares": len(stats["unique_shares"]),
                "platforms": list(stats["platforms"])
            })

        return sorted(popular_content, key=lambda x: x["total_shares"], reverse=True)[:50]

    def _analyze_content_flow(self) -> Dict[str, Any]:
        """Analyze how content flows through the network"""
        content_flow = {
            "content_cascades": self._find_content_cascades(),
            "sharing_patterns": self._analyze_sharing_patterns(),
            "content_velocity": self._calculate_content_velocity()
        }

        return content_flow

    def _analyze_engagement_patterns(self) -> Dict[str, Any]:
        """Analyze engagement patterns in the network"""
        engagement_stats = defaultdict(int)

        for rel in self.graph.relationships.values():
            engagement_stats[rel.relationship_type] += rel.interaction_count

        return {
            "total_interactions": sum(engagement_stats.values()),
            "interaction_types": dict(engagement_stats),
            "most_engaged_relationships": self._find_most_engaged_relationships()
        }

    def _analyze_community_stats(self, communities: List[List[str]]) -> Dict[str, Any]:
        """Analyze statistics of detected communities"""
        if not communities:
            return {}

        community_sizes = [len(community) for community in communities]

        return {
            "total_communities": len(communities),
            "average_size": sum(community_sizes) / len(community_sizes),
            "largest_community": max(community_sizes),
            "smallest_community": min(community_sizes),
            "community_size_distribution": self._calculate_size_distribution(community_sizes)
        }

    def _analyze_group_interactions(self) -> List[Dict[str, Any]]:
        """Analyze interactions within groups"""
        group_interactions = []

        # Find relationships within the same community
        communities = self.algorithms.detect_communities()

        for i, community in enumerate(communities):
            internal_relationships = []
            for person1 in community:
                for person2 in community:
                    if person1 != person2:
                        strength = self.graph.get_relationship_strength(person1, person2)
                        if strength > 0:
                            internal_relationships.append({
                                "person1": person1,
                                "person2": person2,
                                "strength": strength
                            })

            if internal_relationships:
                group_interactions.append({
                    "community_id": i,
                    "size": len(community),
                    "internal_relationships": len(internal_relationships),
                    "avg_relationship_strength": sum(r["strength"] for r in internal_relationships) / len(internal_relationships)
                })

        return group_interactions

    def _analyze_community_influence(self, communities: List[List[str]]) -> Dict[str, Any]:
        """Analyze influence patterns within communities"""
        community_influence = {}

        for i, community in enumerate(communities):
            # Calculate influence scores for community members
            member_scores = {}
            for member in community:
                # Use eigenvector centrality as influence measure
                centrality_scores = self.algorithms.eigenvector_centrality()
                member_scores[member] = centrality_scores.get(member, 0)

            # Sort by influence
            sorted_members = sorted(member_scores.items(), key=lambda x: x[1], reverse=True)

            community_influence[f"community_{i}"] = {
                "size": len(community),
                "top_influencers": sorted_members[:5],  # Top 5 influencers
                "avg_influence": sum(member_scores.values()) / len(member_scores)
            }

        return community_influence

    def _calculate_mutual_connection_stats(self) -> Dict[str, Any]:
        """Calculate statistics about mutual connections"""
        mutual_stats = {
            "total_possible_mutual": 0,
            "actual_mutual": 0,
            "mutual_percentage": 0.0,
            "most_mutual_person": None,
            "mutual_distribution": defaultdict(int)
        }

        # Calculate mutual connections for each pair
        people_list = list(self.graph.people.keys())

        for i, person1 in enumerate(people_list):
            for person2 in people_list[i+1:]:
                mutual = self.graph.get_mutual_connections(person1, person2)
                if mutual:
                    mutual_stats["actual_mutual"] += 1
                    mutual_stats["mutual_distribution"][len(mutual)] += 1

        mutual_stats["total_possible_mutual"] = len(people_list) * (len(people_list) - 1) // 2

        if mutual_stats["total_possible_mutual"] > 0:
            mutual_stats["mutual_percentage"] = (mutual_stats["actual_mutual"] /
                                                mutual_stats["total_possible_mutual"]) * 100

        return dict(mutual_stats)

    def _find_triangles(self) -> List[List[str]]:
        """Find triangular relationships in the network"""
        triangles = []

        # Simple triangle detection
        people_list = list(self.graph.people.keys())

        for i, person1 in enumerate(people_list):
            for j, person2 in enumerate(people_list[i+1:], i+1):
                if self.graph.get_relationship_strength(person1, person2) > 0:
                    for person3 in people_list[j+1:]:
                        if (self.graph.get_relationship_strength(person1, person3) > 0 and
                            self.graph.get_relationship_strength(person2, person3) > 0):
                            triangles.append([person1, person2, person3])

        return triangles

    def _find_bridges(self) -> List[Tuple[str, str]]:
        """Find bridge relationships in the network"""
        bridges = []

        # Simple bridge detection using betweenness centrality
        betweenness = self.algorithms.betweenness_centrality()

        # Relationships with high betweenness are potential bridges
        high_betweenness_threshold = 0.1  # Adjust as needed

        for rel_key, rel in self.relationships.items():
            # Calculate betweenness for this relationship
            # This is a simplified approach
            if betweenness.get(rel.source_id, 0) > high_betweenness_threshold:
                bridges.append((rel.source_id, rel.target_id))

        return bridges

    def _find_cliques(self) -> List[List[str]]:
        """Find cliques in the network"""
        # Simplified clique detection - find fully connected subgraphs
        cliques = []

        # This is a basic implementation - in practice you'd use more sophisticated algorithms
        people_list = list(self.graph.people.keys())

        for person in people_list:
            neighbors = set(self.graph.get_connections(person))
            if len(neighbors) >= 2:
                # Check if neighbors form a clique
                is_clique = True
                neighbor_list = list(neighbors)

                for i, n1 in enumerate(neighbor_list):
                    for n2 in neighbor_list[i+1:]:
                        if self.graph.get_relationship_strength(n1, n2) == 0:
                            is_clique = False
                            break
                    if not is_clique:
                        break

                if is_clique:
                    clique = [person] + neighbor_list
                    if clique not in cliques:
                        cliques.append(clique)

        return cliques

    def _analyze_strength_distribution(self) -> Dict[str, Any]:
        """Analyze distribution of relationship strengths"""
        strengths = [rel.strength for rel in self.graph.relationships.values()]

        if not strengths:
            return {"distribution": {}, "stats": {}}

        return {
            "distribution": {
                "weak": len([s for s in strengths if s < 0.3]),
                "moderate": len([s for s in strengths if 0.3 <= s < 0.7]),
                "strong": len([s for s in strengths if s >= 0.7])
            },
            "stats": {
                "average": sum(strengths) / len(strengths),
                "median": sorted(strengths)[len(strengths) // 2],
                "min": min(strengths),
                "max": max(strengths)
            }
        }

    def _analyze_relationship_evolution(self) -> Dict[str, Any]:
        """Analyze how relationships evolve over time"""
        # Group relationships by time periods
        time_periods = defaultdict(list)

        for rel in self.graph.relationships.values():
            if rel.first_interaction:
                period = rel.first_interaction.strftime('%Y-%m')
                time_periods[period].append(rel)

        evolution = {}
        for period, relationships in sorted(time_periods.items()):
            evolution[period] = {
                "new_relationships": len(relationships),
                "avg_strength": sum(r.strength for r in relationships) / len(relationships) if relationships else 0
            }

        return evolution

    def _find_strongest_connections(self) -> List[Dict[str, Any]]:
        """Find the strongest connections in the network"""
        relationships = list(self.graph.relationships.values())
        sorted_rels = sorted(relationships, key=lambda x: x.strength, reverse=True)

        return [{
            "source": rel.source_id,
            "target": rel.target_id,
            "strength": rel.strength,
            "type": rel.relationship_type
        } for rel in sorted_rels[:20]]

    def _find_weakest_connections(self) -> List[Dict[str, Any]]:
        """Find the weakest connections in the network"""
        relationships = list(self.graph.relationships.values())
        sorted_rels = sorted(relationships, key=lambda x: x.strength)

        return [{
            "source": rel.source_id,
            "target": rel.target_id,
            "strength": rel.strength,
            "type": rel.relationship_type
        } for rel in sorted_rels[:20]]

    def _calculate_influence_scores(self) -> Dict[str, float]:
        """Calculate influence scores for network members"""
        # Use PageRank as influence measure
        return self.algorithms.page_rank()

    def _calculate_engagement_metrics(self) -> Dict[str, Any]:
        """Calculate engagement metrics for the network"""
        total_interactions = sum(rel.interaction_count for rel in self.graph.relationships.values())
        total_relationships = len(self.graph.relationships)

        return {
            "total_interactions": total_interactions,
            "avg_interactions_per_relationship": total_interactions / total_relationships if total_relationships > 0 else 0,
            "most_active_relationships": self._find_most_engaged_relationships()
        }

    def _analyze_content_virality(self) -> Dict[str, Any]:
        """Analyze content virality patterns"""
        viral_content = []

        for rel in self.graph.relationships.values():
            if rel.relationship_type == "shared_content" and len(rel.shared_content) > 3:
                viral_content.append({
                    "content_ids": rel.shared_content,
                    "share_count": len(rel.shared_content),
                    "participants": [rel.source_id, rel.target_id]
                })

        return {
            "viral_content_count": len(viral_content),
            "most_viral_content": sorted(viral_content, key=lambda x: x["share_count"], reverse=True)[:10]
        }

    def _identify_network_influencers(self) -> List[Dict[str, Any]]:
        """Identify key influencers in the network"""
        influence_scores = self._calculate_influence_scores()

        influencers = []
        for person_id, score in sorted(influence_scores.items(), key=lambda x: x[1], reverse=True)[:20]:
            person = self.graph.get_person(person_id)
            if person:
                influencers.append({
                    "person_id": person_id,
                    "name": person.name,
                    "influence_score": score,
                    "connections": len(self.graph.get_connections(person_id))
                })

        return influencers

    def _find_content_cascades(self) -> List[Dict[str, Any]]:
        """Find content sharing cascades"""
        cascades = []

        # Group relationships by shared content
        content_shares = defaultdict(list)

        for rel in self.graph.relationships.values():
            if rel.relationship_type == "shared_content":
                for content_id in rel.shared_content:
                    content_shares[content_id].append(rel)

        # Analyze cascades
        for content_id, shares in content_shares.items():
            if len(shares) > 2:  # Minimum cascade size
                cascade = {
                    "content_id": content_id,
                    "participants": list(set(rel.source_id for rel in shares)),
                    "total_shares": len(shares),
                    "cascade_depth": self._calculate_cascade_depth(shares)
                }
                cascades.append(cascade)

        return sorted(cascades, key=lambda x: x["total_shares"], reverse=True)

    def _analyze_sharing_patterns(self) -> Dict[str, Any]:
        """Analyze content sharing patterns"""
        sharing_patterns = defaultdict(int)

        for rel in self.graph.relationships.values():
            if rel.relationship_type == "shared_content":
                sharing_patterns[len(rel.shared_content)] += 1

        return {
            "sharing_frequency": dict(sharing_patterns),
            "avg_shares_per_content": sum(k * v for k, v in sharing_patterns.items()) / sum(sharing_patterns.values()) if sharing_patterns else 0
        }

    def _calculate_content_velocity(self) -> Dict[str, Any]:
        """Calculate content sharing velocity"""
        # This would analyze how quickly content spreads
        return {
            "avg_sharing_speed": "not_implemented",  # Would need timestamp analysis
            "viral_threshold": 5  # Minimum shares for viral content
        }

    def _find_most_engaged_relationships(self) -> List[Dict[str, Any]]:
        """Find relationships with highest engagement"""
        relationships = list(self.graph.relationships.values())
        sorted_rels = sorted(relationships, key=lambda x: x.interaction_count, reverse=True)

        return [{
            "source": rel.source_id,
            "target": rel.target_id,
            "interactions": rel.interaction_count,
            "type": rel.relationship_type
        } for rel in sorted_rels[:20]]

    def _calculate_size_distribution(self, sizes: List[int]) -> Dict[str, int]:
        """Calculate distribution of community sizes"""
        return {
            "small": len([s for s in sizes if s <= 3]),
            "medium": len([s for s in sizes if 4 <= s <= 10]),
            "large": len([s for s in sizes if s > 10])
        }

    def _calculate_cascade_depth(self, shares: List[Relationship]) -> int:
        """Calculate the depth of a sharing cascade"""
        # Simplified cascade depth calculation
        if not shares:
            return 0

        # Sort by interaction time
        sorted_shares = sorted(shares, key=lambda x: x.first_interaction or datetime.now())

        # Calculate depth based on branching
        depth = 1
        current_level = {sorted_shares[0].source_id}

        for share in sorted_shares[1:]:
            if share.source_id not in current_level:
                depth += 1
                current_level = {share.source_id}

        return depth