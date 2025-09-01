"""
Edge Cases and Boundary Tests for Social Network Analysis

This module contains tests for edge cases, error conditions, and boundary scenarios
in the social network analysis system.
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import math

from libs.social_network.models import Person, Relationship, SocialGraph
from libs.social_network.graph_algorithms import GraphAlgorithms
from libs.social_network.extractor import RelationshipExtractor
from libs.social_network.analyzer import SocialNetworkAnalyzer
from libs.social_network.inference import RelationshipInference


class TestEdgeCasesPerson:
    """Edge cases for Person model"""

    def test_person_with_empty_strings(self):
        """Test Person with empty string fields"""
        person = Person(
            id="",
            name="",
            username="",
            platform="",
            bio="",
            location=""
        )

        assert person.id == ""
        assert person.name == ""
        assert person.username == ""
        assert person.platform == ""

    def test_person_with_none_values(self):
        """Test Person with None values"""
        person = Person(
            id="test",
            name=None,
            username=None,
            platform="twitter"
        )

        assert person.name is None
        assert person.username is None
        assert person.platform == "twitter"

    def test_person_with_extremely_long_fields(self):
        """Test Person with extremely long field values"""
        long_string = "a" * 10000
        person = Person(
            id="test",
            name=long_string,
            username=long_string,
            platform="twitter",
            bio=long_string,
            location=long_string
        )

        assert len(person.name) == 10000
        assert len(person.bio) == 10000

    def test_person_to_dict_with_none_values(self):
        """Test to_dict with None values"""
        person = Person(
            id="test",
            name=None,
            platform="twitter"
        )

        person_dict = person.to_dict()

        assert person_dict["name"] is None
        assert person_dict["id"] == "test"
        assert "created_at" in person_dict

    def test_person_from_dict_with_missing_keys(self):
        """Test from_dict with missing keys"""
        data = {"id": "test", "platform": "twitter"}

        person = Person.from_dict(data)

        assert person.id == "test"
        assert person.platform == "twitter"
        assert person.name == ""  # Default value

    def test_person_from_dict_with_invalid_data_types(self):
        """Test from_dict with invalid data types"""
        data = {
            "id": 123,  # Should be string
            "name": ["invalid"],  # Should be string
            "platform": "twitter",
            "follower_count": "invalid"  # Should be int
        }

        person = Person.from_dict(data)

        assert person.id == "123"  # Converted to string
        assert person.name == "['invalid']"  # Converted to string
        assert person.follower_count == 0  # Default value for invalid int


class TestEdgeCasesRelationship:
    """Edge cases for Relationship model"""

    def test_relationship_with_zero_strength(self):
        """Test Relationship with zero strength"""
        relationship = Relationship(
            source_id="user1",
            target_id="user2",
            relationship_type="follow",
            strength=0.0
        )

        assert relationship.strength == 0.0

    def test_relationship_with_max_strength(self):
        """Test Relationship with maximum strength"""
        relationship = Relationship(
            source_id="user1",
            target_id="user2",
            relationship_type="follow",
            strength=float('inf')
        )

        assert relationship.strength == float('inf')

    def test_relationship_with_negative_strength(self):
        """Test Relationship with negative strength"""
        relationship = Relationship(
            source_id="user1",
            target_id="user2",
            relationship_type="follow",
            strength=-1.0
        )

        assert relationship.strength == -1.0

    def test_relationship_with_empty_platforms(self):
        """Test Relationship with empty platforms list"""
        relationship = Relationship(
            source_id="user1",
            target_id="user2",
            relationship_type="follow",
            platforms=[]
        )

        assert relationship.platforms == []

    def test_relationship_with_duplicate_platforms(self):
        """Test Relationship with duplicate platforms"""
        relationship = Relationship(
            source_id="user1",
            target_id="user2",
            relationship_type="follow",
            platforms=["twitter", "twitter", "facebook"]
        )

        assert relationship.platforms == ["twitter", "twitter", "facebook"]

    def test_relationship_with_extremely_long_content_ids(self):
        """Test Relationship with extremely long shared content IDs"""
        long_content_ids = ["content_" + "a" * 1000 for _ in range(100)]
        relationship = Relationship(
            source_id="user1",
            target_id="user2",
            relationship_type="shared_content",
            shared_content=long_content_ids
        )

        assert len(relationship.shared_content) == 100
        assert len(relationship.shared_content[0]) == 1007  # "content_" + 1000 "a"s

    def test_relationship_to_dict_with_circular_reference(self):
        """Test to_dict with potential circular references"""
        # This tests the robustness of the to_dict method
        relationship = Relationship(
            source_id="user1",
            target_id="user2",
            relationship_type="follow"
        )

        # Add a self-reference in metadata (edge case)
        relationship.metadata_json = {"self": relationship}

        # Should not crash
        rel_dict = relationship.to_dict()
        assert rel_dict["source_id"] == "user1"
        assert rel_dict["target_id"] == "user2"


class TestEdgeCasesSocialGraph:
    """Edge cases for SocialGraph model"""

    def test_empty_graph_operations(self):
        """Test operations on empty graph"""
        graph = SocialGraph()

        assert len(graph.people) == 0
        assert len(graph.relationships) == 0
        assert len(graph.adjacency_list) == 0

        # Test getting non-existent person
        person = graph.get_person("nonexistent")
        assert person is None

        # Test getting connections for non-existent person
        connections = graph.get_connections("nonexistent")
        assert connections == []

        # Test getting relationships for non-existent person
        relationships = graph.get_relationships("nonexistent")
        assert relationships == []

    def test_graph_with_single_node(self):
        """Test graph with only one node"""
        graph = SocialGraph()
        person = Person(id="user1", name="User 1", platform="twitter")
        graph.add_person(person)

        assert len(graph.people) == 1
        assert len(graph.relationships) == 0

        # Test network stats
        stats = graph.get_network_stats()
        assert stats["total_nodes"] == 1
        assert stats["total_relationships"] == 0
        assert stats["network_density"] == 0.0

    def test_graph_with_isolated_nodes(self):
        """Test graph with multiple isolated nodes"""
        graph = SocialGraph()

        # Add multiple people with no relationships
        for i in range(10):
            person = Person(id=f"user{i}", name=f"User {i}", platform="twitter")
            graph.add_person(person)

        assert len(graph.people) == 10
        assert len(graph.relationships) == 0

        # Test network stats
        stats = graph.get_network_stats()
        assert stats["total_nodes"] == 10
        assert stats["total_relationships"] == 0
        assert stats["network_density"] == 0.0

    def test_graph_with_self_loops(self):
        """Test graph with self-referencing relationships"""
        graph = SocialGraph()

        person = Person(id="user1", name="User 1", platform="twitter")
        graph.add_person(person)

        # Add self-loop relationship
        relationship = Relationship(
            source_id="user1",
            target_id="user1",
            relationship_type="self_follow"
        )
        graph.add_relationship(relationship)

        assert len(graph.relationships) == 1
        assert "user1" in graph.adjacency_list["user1"]

    def test_graph_with_duplicate_relationships(self):
        """Test graph with duplicate relationships"""
        graph = SocialGraph()

        person1 = Person(id="user1", name="User 1", platform="twitter")
        person2 = Person(id="user2", name="User 2", platform="twitter")
        graph.add_person(person1)
        graph.add_person(person2)

        # Add duplicate relationships
        for i in range(3):
            relationship = Relationship(
                source_id="user1",
                target_id="user2",
                relationship_type="follow",
                strength=0.5
            )
            graph.add_relationship(relationship)

        # Should have 3 relationships with same key
        assert len(graph.relationships) == 3

    def test_graph_with_maximum_nodes(self):
        """Test graph with large number of nodes"""
        graph = SocialGraph()

        # Add many nodes
        num_nodes = 10000
        for i in range(num_nodes):
            person = Person(id=f"user{i}", name=f"User {i}", platform="twitter")
            graph.add_person(person)

        assert len(graph.people) == num_nodes

        # Test network stats with many nodes
        stats = graph.get_network_stats()
        assert stats["total_nodes"] == num_nodes
        assert stats["total_relationships"] == 0

    def test_graph_memory_usage_with_large_adjacency_list(self):
        """Test memory usage with large adjacency lists"""
        graph = SocialGraph()

        # Create a star network (one central node connected to many others)
        central_person = Person(id="central", name="Central User", platform="twitter")
        graph.add_person(central_person)

        num_leaves = 1000
        for i in range(num_leaves):
            leaf_person = Person(id=f"leaf{i}", name=f"Leaf {i}", platform="twitter")
            graph.add_person(leaf_person)

            relationship = Relationship(
                source_id="central",
                target_id=f"leaf{i}",
                relationship_type="follow"
            )
            graph.add_relationship(relationship)

        assert len(graph.people) == num_leaves + 1
        assert len(graph.relationships) == num_leaves
        assert len(graph.adjacency_list["central"]) == num_leaves

    def test_graph_with_unicode_characters(self):
        """Test graph with Unicode characters in names and content"""
        graph = SocialGraph()

        # Add people with Unicode names
        unicode_names = [
            "José María",
            "李小明",
            "محمد علي",
            "Александр",
            "François",
            "São Paulo",
            "東京"
        ]

        for i, name in enumerate(unicode_names):
            person = Person(id=f"user{i}", name=name, platform="twitter")
            graph.add_person(person)

        assert len(graph.people) == len(unicode_names)

        # Test that all names are preserved
        for i, expected_name in enumerate(unicode_names):
            assert graph.people[f"user{i}"].name == expected_name


class TestEdgeCasesGraphAlgorithms:
    """Edge cases for GraphAlgorithms"""

    def test_algorithms_with_empty_graph(self):
        """Test algorithms on empty graph"""
        graph = SocialGraph()
        algorithms = GraphAlgorithms(graph)

        # Should not crash
        centrality = algorithms.degree_centrality()
        assert centrality == {}

        density = algorithms.network_density()
        assert density == 0.0

        components = algorithms.connected_components()
        assert components == []

    def test_algorithms_with_single_node(self):
        """Test algorithms on single node graph"""
        graph = SocialGraph()
        person = Person(id="user1", name="User 1", platform="twitter")
        graph.add_person(person)

        algorithms = GraphAlgorithms(graph)

        centrality = algorithms.degree_centrality()
        assert centrality == {"user1": 0.0}

        density = algorithms.network_density()
        assert density == 0.0

        components = algorithms.connected_components()
        assert len(components) == 1
        assert components[0] == ["user1"]

    def test_shortest_path_with_no_path(self):
        """Test shortest path when no path exists"""
        graph = SocialGraph()

        # Create disconnected components
        person1 = Person(id="user1", name="User 1", platform="twitter")
        person2 = Person(id="user2", name="User 2", platform="twitter")
        person3 = Person(id="user3", name="User 3", platform="twitter")
        person4 = Person(id="user4", name="User 4", platform="twitter")

        graph.add_person(person1)
        graph.add_person(person2)
        graph.add_person(person3)
        graph.add_person(person4)

        # Connect user1-user2 and user3-user4
        rel1 = Relationship(source_id="user1", target_id="user2", relationship_type="follow")
        rel2 = Relationship(source_id="user3", target_id="user4", relationship_type="follow")
        graph.add_relationship(rel1)
        graph.add_relationship(rel2)

        algorithms = GraphAlgorithms(graph)

        # No path between user1 and user3
        path = algorithms.shortest_path("user1", "user3")
        assert path == []  # No path exists

    def test_shortest_path_same_node(self):
        """Test shortest path from node to itself"""
        graph = SocialGraph()
        person = Person(id="user1", name="User 1", platform="twitter")
        graph.add_person(person)

        algorithms = GraphAlgorithms(graph)

        path = algorithms.shortest_path("user1", "user1")
        assert path == ["user1"]

    def test_centrality_with_isolated_nodes(self):
        """Test centrality measures with isolated nodes"""
        graph = SocialGraph()

        # Add isolated nodes
        for i in range(5):
            person = Person(id=f"user{i}", name=f"User {i}", platform="twitter")
            graph.add_person(person)

        algorithms = GraphAlgorithms(graph)

        centrality = algorithms.degree_centrality()
        assert len(centrality) == 5
        assert all(score == 0.0 for score in centrality.values())

    def test_network_density_with_few_connections(self):
        """Test network density with minimal connections"""
        graph = SocialGraph()

        # Add 3 nodes with only 1 connection
        person1 = Person(id="user1", name="User 1", platform="twitter")
        person2 = Person(id="user2", name="User 2", platform="twitter")
        person3 = Person(id="user3", name="User 3", platform="twitter")

        graph.add_person(person1)
        graph.add_person(person2)
        graph.add_person(person3)

        relationship = Relationship(source_id="user1", target_id="user2", relationship_type="follow")
        graph.add_relationship(relationship)

        algorithms = GraphAlgorithms(graph)

        density = algorithms.network_density()
        # With 3 nodes and 1 edge, density should be 1 / ((3*2)/2) = 1/3 ≈ 0.333
        assert abs(density - (1.0/3.0)) < 0.01

    def test_clustering_coefficient_with_triangles(self):
        """Test clustering coefficient with triangular relationships"""
        graph = SocialGraph()

        # Create a triangle: user1-user2-user3-user1
        person1 = Person(id="user1", name="User 1", platform="twitter")
        person2 = Person(id="user2", name="User 2", platform="twitter")
        person3 = Person(id="user3", name="User 3", platform="twitter")

        graph.add_person(person1)
        graph.add_person(person2)
        graph.add_person(person3)

        relationships = [
            Relationship(source_id="user1", target_id="user2", relationship_type="follow"),
            Relationship(source_id="user2", target_id="user3", relationship_type="follow"),
            Relationship(source_id="user3", target_id="user1", relationship_type="follow")
        ]

        for rel in relationships:
            graph.add_relationship(rel)

        algorithms = GraphAlgorithms(graph)

        coefficients = algorithms.clustering_coefficient()

        # In a complete triangle, clustering coefficient should be 1.0
        assert all(abs(coeff - 1.0) < 0.01 for coeff in coefficients.values())


class TestEdgeCasesRelationshipExtractor:
    """Edge cases for RelationshipExtractor"""

    def setup_method(self):
        """Setup test extractor"""
        self.extractor = RelationshipExtractor()

    @patch('libs.storage.models.Item')
    def test_extract_from_malformed_items(self, mock_item):
        """Test extraction from malformed items"""
        # Mock items with missing or malformed data
        malformed_items = [
            Mock(meta=None),  # No meta
            Mock(meta={}),  # Empty meta
            Mock(meta={'platform': None}),  # None platform
            Mock(meta={'platform': 'twitter', 'author': None}),  # None author
            Mock(meta={'platform': 'twitter', 'author': {}}),  # Empty author
        ]

        graph = self.extractor.extract_from_items(malformed_items)

        # Should not crash and return empty graph
        assert len(graph.people) == 0
        assert len(graph.relationships) == 0

    @patch('libs.storage.models.Item')
    def test_extract_from_items_with_invalid_relationships(self, mock_item):
        """Test extraction with invalid relationship data"""
        invalid_items = [
            Mock(meta={
                'platform': 'twitter',
                'author': {'id': 'user1', 'username': 'user1'},
                'mentions': [{'username': None}],  # None username
                'reply_to': {'username': ''},  # Empty username
            })
        ]

        graph = self.extractor.extract_from_items(invalid_items)

        # Should handle gracefully
        assert len(graph.people) >= 1  # At least the author

    def test_extract_mentions_with_nested_structures(self):
        """Test mention extraction with deeply nested structures"""
        meta = {
            'platform': 'twitter',
            'author': {'id': 'user1', 'username': 'user1'},
            'mentions': [
                {'username': 'user2', 'nested': {'deep': {'value': 'test'}}},
                {'username': 'user3', 'array': [1, 2, 3]},
                {'username': 'user4', 'object': {'key': 'value'}}
            ]
        }

        mentions = self.extractor._extract_mentions(meta)
        assert len(mentions) == 3
        assert 'user2' in mentions
        assert 'user3' in mentions
        assert 'user4' in mentions

    def test_extract_with_extremely_large_data(self):
        """Test extraction with extremely large data structures"""
        # Create meta with many mentions
        many_mentions = [{'username': f'user{i}'} for i in range(10000)]

        meta = {
            'platform': 'twitter',
            'author': {'id': 'user1', 'username': 'user1'},
            'mentions': many_mentions
        }

        mentions = self.extractor._extract_mentions(meta)
        assert len(mentions) == 10000


class TestEdgeCasesSocialNetworkAnalyzer:
    """Edge cases for SocialNetworkAnalyzer"""

    def setup_method(self):
        """Setup test analyzer"""
        self.graph = SocialGraph()
        self.analyzer = SocialNetworkAnalyzer(self.graph)

    def test_analyze_empty_graph(self):
        """Test analysis of empty graph"""
        analysis = self.analyzer.analyze_shared_content()

        # Should return empty analysis
        assert isinstance(analysis, dict)
        assert "content_clusters" in analysis
        assert "popular_content" in analysis

    def test_analyze_single_node_graph(self):
        """Test analysis of single node graph"""
        person = Person(id="user1", name="User 1", platform="twitter")
        self.graph.add_person(person)

        analysis = self.analyzer.analyze_shared_content()

        # Should handle single node gracefully
        assert isinstance(analysis, dict)

    def test_analyze_with_zero_strength_relationships(self):
        """Test analysis with zero-strength relationships"""
        person1 = Person(id="user1", name="User 1", platform="twitter")
        person2 = Person(id="user2", name="User 2", platform="twitter")
        self.graph.add_person(person1)
        self.graph.add_person(person2)

        relationship = Relationship(
            source_id="user1",
            target_id="user2",
            relationship_type="follow",
            strength=0.0
        )
        self.graph.add_relationship(relationship)

        analysis = self.analyzer.analyze_relationship_strengths()

        # Should handle zero strength relationships
        assert isinstance(analysis, dict)

    def test_analyze_with_maximum_strength_relationships(self):
        """Test analysis with maximum strength relationships"""
        person1 = Person(id="user1", name="User 1", platform="twitter")
        person2 = Person(id="user2", name="User 2", platform="twitter")
        self.graph.add_person(person1)
        self.graph.add_person(person2)

        relationship = Relationship(
            source_id="user1",
            target_id="user2",
            relationship_type="follow",
            strength=float('inf')
        )
        self.graph.add_relationship(relationship)

        analysis = self.analyzer.analyze_relationship_strengths()

        # Should handle infinite strength relationships
        assert isinstance(analysis, dict)


class TestEdgeCasesRelationshipInference:
    """Edge cases for RelationshipInference"""

    def setup_method(self):
        """Setup test inference engine"""
        self.graph = SocialGraph()
        self.inference = RelationshipInference(self.graph)

    def test_infer_with_empty_graph(self):
        """Test inference on empty graph"""
        inferences = self.inference.infer_implicit_relationships()

        assert inferences == []

    def test_predict_strength_with_nonexistent_people(self):
        """Test strength prediction with nonexistent people"""
        prediction = self.inference.predict_relationship_strength("nonexistent1", "nonexistent2")

        assert prediction["predicted_strength"] == 0
        assert prediction["confidence"] == 0

    def test_predict_future_interactions_with_no_data(self):
        """Test future interaction prediction with no historical data"""
        predictions = self.inference.predict_future_interactions(days_ahead=7)

        assert predictions == []

    def test_normalize_username_edge_cases(self):
        """Test username normalization with edge cases"""
        # Test with None
        normalized = self.inference._normalize_username(None)
        assert normalized == ""

        # Test with special characters only
        normalized = self.inference._normalize_username("@#$%^&*()")
        assert normalized == ""

        # Test with very long username
        long_username = "@" + "a" * 1000
        normalized = self.inference._normalize_username(long_username)
        assert len(normalized) == 1000

    def test_calculate_profile_similarity_with_missing_data(self):
        """Test profile similarity with missing data"""
        person1 = Person(id="user1", name=None, platform="twitter")
        person2 = Person(id="user2", name=None, platform="twitter")

        similarity = self.inference._calculate_profile_similarity(person1, person2)
        assert similarity == 0.0

    def test_calculate_profile_similarity_with_empty_data(self):
        """Test profile similarity with empty data"""
        person1 = Person(id="user1", name="", platform="twitter", bio="")
        person2 = Person(id="user2", name="", platform="twitter", bio="")

        similarity = self.inference._calculate_profile_similarity(person1, person2)
        assert similarity == 0.0


class TestPerformanceEdgeCases:
    """Performance-related edge cases"""

    def test_large_graph_operations(self):
        """Test operations on very large graphs"""
        graph = SocialGraph()

        # Create a large graph
        num_nodes = 1000
        num_edges = 5000

        # Add nodes
        for i in range(num_nodes):
            person = Person(id=f"user{i}", name=f"User {i}", platform="twitter")
            graph.add_person(person)

        # Add random edges
        import random
        random.seed(42)  # For reproducible tests

        for _ in range(num_edges):
            source = random.randint(0, num_nodes - 1)
            target = random.randint(0, num_nodes - 1)
            if source != target:
                relationship = Relationship(
                    source_id=f"user{source}",
                    target_id=f"user{target}",
                    relationship_type="follow"
                )
                graph.add_relationship(relationship)

        assert len(graph.people) == num_nodes
        assert len(graph.relationships) <= num_edges  # May have duplicates

        # Test that basic operations don't crash
        stats = graph.get_network_stats()
        assert stats["total_nodes"] == num_nodes

    def test_memory_usage_with_many_relationships(self):
        """Test memory usage with many relationships per node"""
        graph = SocialGraph()

        # Create a node with many connections (star pattern)
        central_person = Person(id="central", name="Central User", platform="twitter")
        graph.add_person(central_person)

        num_connections = 10000

        for i in range(num_connections):
            leaf_person = Person(id=f"leaf{i}", name=f"Leaf {i}", platform="twitter")
            graph.add_person(leaf_person)

            relationship = Relationship(
                source_id="central",
                target_id=f"leaf{i}",
                relationship_type="follow"
            )
            graph.add_relationship(relationship)

        assert len(graph.people) == num_connections + 1
        assert len(graph.relationships) == num_connections
        assert len(graph.adjacency_list["central"]) == num_connections

    def test_concurrent_operations(self):
        """Test concurrent operations on the graph"""
        import threading
        import time

        graph = SocialGraph()
        results = []

        def add_people(start_id, count):
            for i in range(start_id, start_id + count):
                person = Person(id=f"user{i}", name=f"User {i}", platform="twitter")
                graph.add_person(person)
            results.append(f"Added {count} people from {start_id}")

        # Start multiple threads
        threads = []
        num_threads = 10
        people_per_thread = 100

        for i in range(num_threads):
            start_id = i * people_per_thread
            thread = threading.Thread(target=add_people, args=(start_id, people_per_thread))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        assert len(results) == num_threads
        assert len(graph.people) == num_threads * people_per_thread


if __name__ == "__main__":
    pytest.main([__file__])