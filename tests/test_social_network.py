"""
Tests for Social Network Analysis Features

This module contains comprehensive tests for all social network analysis components:
- Social network data models
- Graph algorithms
- Relationship extraction
- Inference algorithms
- Database operations
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from libs.social_network.models import Person, Relationship, SocialGraph
from libs.social_network.graph_algorithms import GraphAlgorithms
from libs.social_network.extractor import RelationshipExtractor
from libs.social_network.analyzer import SocialNetworkAnalyzer
from libs.social_network.inference import RelationshipInference


class TestPerson:
    """Test cases for Person model"""

    def test_person_creation(self):
        """Test creating a Person object"""
        person = Person(
            id="test_user_1",
            name="Test User",
            username="testuser",
            platform="twitter",
            bio="Test bio",
            location="Test City",
            follower_count=100,
            following_count=50,
            verified=True
        )

        assert person.id == "test_user_1"
        assert person.name == "Test User"
        assert person.username == "testuser"
        assert person.platform == "twitter"
        assert person.bio == "Test bio"
        assert person.location == "Test City"
        assert person.follower_count == 100
        assert person.following_count == 50
        assert person.verified is True

    def test_person_to_dict(self):
        """Test converting Person to dictionary"""
        person = Person(
            id="test_user_1",
            name="Test User",
            username="testuser",
            platform="twitter"
        )

        person_dict = person.to_dict()

        assert person_dict["id"] == "test_user_1"
        assert person_dict["name"] == "Test User"
        assert person_dict["username"] == "testuser"
        assert person_dict["platform"] == "twitter"
        assert "created_at" in person_dict

    def test_person_from_dict(self):
        """Test creating Person from dictionary"""
        data = {
            "id": "test_user_1",
            "name": "Test User",
            "username": "testuser",
            "platform": "twitter",
            "bio": "Test bio",
            "follower_count": 100
        }

        person = Person.from_dict(data)

        assert person.id == "test_user_1"
        assert person.name == "Test User"
        assert person.bio == "Test bio"
        assert person.follower_count == 100


class TestRelationship:
    """Test cases for Relationship model"""

    def test_relationship_creation(self):
        """Test creating a Relationship object"""
        relationship = Relationship(
            source_id="user1",
            target_id="user2",
            relationship_type="follow",
            strength=0.8,
            platforms=["twitter"],
            interaction_count=5
        )

        assert relationship.source_id == "user1"
        assert relationship.target_id == "user2"
        assert relationship.relationship_type == "follow"
        assert relationship.strength == 0.8
        assert relationship.platforms == ["twitter"]
        assert relationship.interaction_count == 5

    def test_relationship_to_dict(self):
        """Test converting Relationship to dictionary"""
        relationship = Relationship(
            source_id="user1",
            target_id="user2",
            relationship_type="follow",
            strength=0.8
        )

        rel_dict = relationship.to_dict()

        assert rel_dict["source_id"] == "user1"
        assert rel_dict["target_id"] == "user2"
        assert rel_dict["relationship_type"] == "follow"
        assert rel_dict["strength"] == 0.8

    def test_relationship_from_dict(self):
        """Test creating Relationship from dictionary"""
        data = {
            "source_id": "user1",
            "target_id": "user2",
            "relationship_type": "follow",
            "strength": 0.8,
            "platforms": ["twitter"],
            "interaction_count": 5
        }

        relationship = Relationship.from_dict(data)

        assert relationship.source_id == "user1"
        assert relationship.target_id == "user2"
        assert relationship.relationship_type == "follow"
        assert relationship.strength == 0.8


class TestSocialGraph:
    """Test cases for SocialGraph model"""

    def test_social_graph_creation(self):
        """Test creating a SocialGraph object"""
        graph = SocialGraph()

        assert len(graph.people) == 0
        assert len(graph.relationships) == 0
        assert len(graph.adjacency_list) == 0

    def test_add_person(self):
        """Test adding a person to the graph"""
        graph = SocialGraph()
        person = Person(id="user1", name="User 1", platform="twitter")

        graph.add_person(person)

        assert len(graph.people) == 1
        assert "user1" in graph.people
        assert graph.people["user1"].name == "User 1"

    def test_add_relationship(self):
        """Test adding a relationship to the graph"""
        graph = SocialGraph()

        # Add people first
        person1 = Person(id="user1", name="User 1", platform="twitter")
        person2 = Person(id="user2", name="User 2", platform="twitter")
        graph.add_person(person1)
        graph.add_person(person2)

        # Add relationship
        relationship = Relationship(
            source_id="user1",
            target_id="user2",
            relationship_type="follow",
            strength=0.8
        )
        graph.add_relationship(relationship)

        assert len(graph.relationships) == 1
        assert "user1_user2_follow" in graph.relationships
        assert "user1" in graph.adjacency_list
        assert "user2" in graph.adjacency_list["user1"]

    def test_get_connections(self):
        """Test getting connections for a person"""
        graph = SocialGraph()

        # Add people and relationships
        person1 = Person(id="user1", name="User 1", platform="twitter")
        person2 = Person(id="user2", name="User 2", platform="twitter")
        person3 = Person(id="user3", name="User 3", platform="twitter")
        graph.add_person(person1)
        graph.add_person(person2)
        graph.add_person(person3)

        # Add relationships
        rel1 = Relationship(source_id="user1", target_id="user2", relationship_type="follow")
        rel2 = Relationship(source_id="user1", target_id="user3", relationship_type="mention")
        graph.add_relationship(rel1)
        graph.add_relationship(rel2)

        # Test getting all connections
        connections = graph.get_connections("user1")
        assert len(connections) == 2
        assert "user2" in connections
        assert "user3" in connections

        # Test getting connections by type
        follow_connections = graph.get_connections("user1", "follow")
        assert len(follow_connections) == 1
        assert "user2" in follow_connections

    def test_get_relationships(self):
        """Test getting relationships for a person"""
        graph = SocialGraph()

        # Add people and relationships
        person1 = Person(id="user1", name="User 1", platform="twitter")
        person2 = Person(id="user2", name="User 2", platform="twitter")
        graph.add_person(person1)
        graph.add_person(person2)

        relationship = Relationship(
            source_id="user1",
            target_id="user2",
            relationship_type="follow",
            strength=0.8
        )
        graph.add_relationship(relationship)

        # Test getting relationships
        relationships = graph.get_relationships("user1")
        assert len(relationships) == 1
        assert relationships[0].target_id == "user2"

    def test_get_mutual_connections(self):
        """Test getting mutual connections between two people"""
        graph = SocialGraph()

        # Add people
        person1 = Person(id="user1", name="User 1", platform="twitter")
        person2 = Person(id="user2", name="User 2", platform="twitter")
        person3 = Person(id="user3", name="User 3", platform="twitter")
        person4 = Person(id="user4", name="User 4", platform="twitter")
        graph.add_person(person1)
        graph.add_person(person2)
        graph.add_person(person3)
        graph.add_person(person4)

        # Add relationships creating mutual connections
        rel1 = Relationship(source_id="user1", target_id="user3", relationship_type="follow")
        rel2 = Relationship(source_id="user2", target_id="user3", relationship_type="follow")
        rel3 = Relationship(source_id="user1", target_id="user4", relationship_type="follow")
        rel4 = Relationship(source_id="user2", target_id="user4", relationship_type="follow")
        graph.add_relationship(rel1)
        graph.add_relationship(rel2)
        graph.add_relationship(rel3)
        graph.add_relationship(rel4)

        # Test mutual connections
        mutual = graph.get_mutual_connections("user1", "user2")
        assert len(mutual) == 2
        assert "user3" in mutual
        assert "user4" in mutual

    def test_get_network_stats(self):
        """Test getting network statistics"""
        graph = SocialGraph()

        # Add people and relationships
        person1 = Person(id="user1", name="User 1", platform="twitter")
        person2 = Person(id="user2", name="User 2", platform="twitter")
        graph.add_person(person1)
        graph.add_person(person2)

        relationship = Relationship(
            source_id="user1",
            target_id="user2",
            relationship_type="follow",
            strength=0.8
        )
        graph.add_relationship(relationship)

        stats = graph.get_network_stats()

        assert stats["total_nodes"] == 2
        assert stats["total_relationships"] == 1
        assert stats["total_platforms"] == 1
        assert "twitter" in stats["platform_distribution"]


class TestGraphAlgorithms:
    """Test cases for GraphAlgorithms"""

    def setup_method(self):
        """Setup test graph"""
        self.graph = SocialGraph()

        # Create a small test network
        people = [
            Person(id="user1", name="User 1", platform="twitter"),
            Person(id="user2", name="User 2", platform="twitter"),
            Person(id="user3", name="User 3", platform="twitter"),
            Person(id="user4", name="User 4", platform="twitter"),
            Person(id="user5", name="User 5", platform="twitter")
        ]

        for person in people:
            self.graph.add_person(person)

        # Add relationships
        relationships = [
            Relationship(source_id="user1", target_id="user2", relationship_type="follow", strength=0.8),
            Relationship(source_id="user1", target_id="user3", relationship_type="follow", strength=0.7),
            Relationship(source_id="user2", target_id="user3", relationship_type="follow", strength=0.6),
            Relationship(source_id="user2", target_id="user4", relationship_type="follow", strength=0.9),
            Relationship(source_id="user3", target_id="user4", relationship_type="follow", strength=0.5),
            Relationship(source_id="user4", target_id="user5", relationship_type="follow", strength=0.8)
        ]

        for rel in relationships:
            self.graph.add_relationship(rel)

        self.algorithms = GraphAlgorithms(self.graph)

    def test_degree_centrality(self):
        """Test degree centrality calculation"""
        centrality = self.algorithms.degree_centrality()

        assert len(centrality) == 5
        assert all(0 <= score <= 1 for score in centrality.values())

        # user2 should have highest degree centrality (connected to 3 others)
        assert centrality["user2"] > centrality["user1"]
        assert centrality["user5"] < centrality["user2"]  # user5 has only 1 connection

    def test_shortest_path(self):
        """Test shortest path calculation"""
        path = self.algorithms.shortest_path("user1", "user5")

        assert len(path) > 0
        assert path[0] == "user1"
        assert path[-1] == "user5"

        # Path should be user1 -> user2 -> user4 -> user5
        assert path == ["user1", "user2", "user4", "user5"]

    def test_connected_components(self):
        """Test connected components detection"""
        components = self.algorithms.connected_components()

        assert len(components) == 1  # All users are connected
        assert len(components[0]) == 5
        assert set(components[0]) == {"user1", "user2", "user3", "user4", "user5"}

    def test_clustering_coefficient(self):
        """Test clustering coefficient calculation"""
        coefficients = self.algorithms.clustering_coefficient()

        assert len(coefficients) == 5
        assert all(0 <= coeff <= 1 for coeff in coefficients.values())

    def test_network_density(self):
        """Test network density calculation"""
        density = self.algorithms.network_density()

        assert 0 <= density <= 1
        # With 5 nodes and 6 edges, density should be 6 / (5*4/2) = 6/10 = 0.6
        assert abs(density - 0.6) < 0.01

    def test_average_path_length(self):
        """Test average path length calculation"""
        avg_path = self.algorithms.average_path_length()

        assert avg_path > 0
        # Should be a reasonable value for this small network
        assert avg_path < 3.0

    def test_degree_distribution(self):
        """Test degree distribution calculation"""
        distribution = self.algorithms.degree_distribution()

        assert isinstance(distribution, dict)
        assert sum(distribution.values()) == 5  # Total nodes

    def test_get_network_summary(self):
        """Test comprehensive network summary"""
        summary = self.algorithms.get_network_summary()

        required_keys = [
            "nodes", "edges", "density", "average_path_length",
            "diameter", "connected_components", "degree_distribution",
            "centrality_measures", "clustering_coefficient"
        ]

        for key in required_keys:
            assert key in summary

        assert summary["nodes"] == 5
        assert summary["edges"] == 6  # Each relationship is undirected


class TestRelationshipExtractor:
    """Test cases for RelationshipExtractor"""

    def setup_method(self):
        """Setup test data"""
        self.extractor = RelationshipExtractor()

    @patch('libs.storage.models.Item')
    def test_extract_from_items_empty(self, mock_item):
        """Test extraction from empty items"""
        items = []
        graph = self.extractor.extract_from_items(items)

        assert len(graph.people) == 0
        assert len(graph.relationships) == 0

    @patch('libs.storage.models.Item')
    def test_extract_from_items_with_data(self, mock_item):
        """Test extraction from items with social media data"""
        # Mock items with social media data
        mock_items = [
            Mock(
                meta={
                    'platform': 'twitter',
                    'author': {'id': 'user1', 'username': 'user1', 'name': 'User 1'},
                    'mentions': [{'username': 'user2'}, {'username': 'user3'}],
                    'reply_to': {'username': 'user4'}
                }
            ),
            Mock(
                meta={
                    'platform': 'twitter',
                    'author': {'id': 'user2', 'username': 'user2', 'name': 'User 2'},
                    'retweets': [{'username': 'user1'}],
                    'quotes': [{'username': 'user3'}]
                }
            )
        ]

        graph = self.extractor.extract_from_items(mock_items)

        assert len(graph.people) >= 2  # At least user1 and user2
        assert len(graph.relationships) > 0

    def test_extract_mentions(self):
        """Test mention extraction"""
        meta = {
            'platform': 'twitter',
            'author': {'id': 'user1', 'username': 'user1'},
            'mentions': [
                {'username': 'user2', 'id': 'user2'},
                {'username': 'user3', 'id': 'user3'}
            ]
        }

        mentions = self.extractor._extract_mentions(meta)
        assert len(mentions) == 2
        assert 'user2' in mentions
        assert 'user3' in mentions

    def test_extract_replies(self):
        """Test reply extraction"""
        meta = {
            'platform': 'twitter',
            'author': {'id': 'user1', 'username': 'user1'},
            'reply_to': {'username': 'user2', 'id': 'user2'}
        }

        reply_to = self.extractor._extract_reply_to(meta)
        assert reply_to == 'user2'

    def test_extract_retweets(self):
        """Test retweet extraction"""
        meta = {
            'platform': 'twitter',
            'author': {'id': 'user1', 'username': 'user1'},
            'retweets': [
                {'username': 'user2', 'id': 'user2'},
                {'username': 'user3', 'id': 'user3'}
            ]
        }

        retweets = self.extractor._extract_retweets(meta)
        assert len(retweets) == 2
        assert 'user2' in retweets
        assert 'user3' in retweets


class TestSocialNetworkAnalyzer:
    """Test cases for SocialNetworkAnalyzer"""

    def setup_method(self):
        """Setup test graph and analyzer"""
        self.graph = SocialGraph()

        # Create test network
        people = [
            Person(id="user1", name="User 1", platform="twitter"),
            Person(id="user2", name="User 2", platform="twitter"),
            Person(id="user3", name="User 3", platform="twitter")
        ]

        for person in people:
            self.graph.add_person(person)

        # Add relationships
        relationships = [
            Relationship(source_id="user1", target_id="user2", relationship_type="shared_content",
                        shared_content=["content1", "content2"]),
            Relationship(source_id="user2", target_id="user3", relationship_type="shared_content",
                        shared_content=["content1"]),
            Relationship(source_id="user1", target_id="user3", relationship_type="follow")
        ]

        for rel in relationships:
            self.graph.add_relationship(rel)

        self.analyzer = SocialNetworkAnalyzer(self.graph)

    def test_analyze_shared_content(self):
        """Test shared content analysis"""
        analysis = self.analyzer.analyze_shared_content()

        assert "content_clusters" in analysis
        assert "popular_content" in analysis
        assert "content_flow" in analysis
        assert "engagement_patterns" in analysis

    def test_analyze_groups_and_communities(self):
        """Test group and community analysis"""
        analysis = self.analyzer.analyze_groups_and_communities()

        assert "communities" in analysis
        assert "community_stats" in analysis
        assert "group_interactions" in analysis
        assert "community_influence" in analysis

    def test_analyze_relationship_strengths(self):
        """Test relationship strength analysis"""
        analysis = self.analyzer.analyze_relationship_strengths()

        assert "strength_distribution" in analysis
        assert "strongest_connections" in analysis
        assert "weakest_connections" in analysis

    def test_find_strongest_connections(self):
        """Test finding strongest connections"""
        strongest = self.analyzer._find_strongest_connections()

        assert isinstance(strongest, list)
        if len(strongest) > 0:
            assert "source" in strongest[0]
            assert "target" in strongest[0]
            assert "strength" in strongest[0]

    def test_find_weakest_connections(self):
        """Test finding weakest connections"""
        weakest = self.analyzer._find_weakest_connections()

        assert isinstance(weakest, list)
        if len(weakest) > 0:
            assert "source" in weakest[0]
            assert "target" in weakest[0]
            assert "strength" in weakest[0]


class TestRelationshipInference:
    """Test cases for RelationshipInference"""

    def setup_method(self):
        """Setup test graph and inference engine"""
        self.graph = SocialGraph()

        # Create test network
        people = [
            Person(id="user1", name="User 1", platform="twitter"),
            Person(id="user2", name="User 2", platform="twitter"),
            Person(id="user3", name="User 3", platform="twitter")
        ]

        for person in people:
            self.graph.add_person(person)

        # Add some relationships
        relationships = [
            Relationship(source_id="user1", target_id="user2", relationship_type="mention"),
            Relationship(source_id="user2", target_id="user3", relationship_type="mention"),
            Relationship(source_id="user1", target_id="user3", relationship_type="follow")
        ]

        for rel in relationships:
            self.graph.add_relationship(rel)

        self.inference = RelationshipInference(self.graph)

    def test_infer_implicit_relationships(self):
        """Test implicit relationship inference"""
        inferences = self.inference.infer_implicit_relationships()

        assert isinstance(inferences, list)
        for inference in inferences:
            assert "source" in inference
            assert "target" in inference
            assert "type" in inference
            assert "strength" in inference
            assert "confidence" in inference

    def test_predict_relationship_strength(self):
        """Test relationship strength prediction"""
        prediction = self.inference.predict_relationship_strength("user1", "user2")

        assert "predicted_strength" in prediction
        assert "confidence" in prediction
        assert "factors" in prediction
        assert 0 <= prediction["predicted_strength"] <= 1
        assert 0 <= prediction["confidence"] <= 1

    def test_predict_future_interactions(self):
        """Test future interaction prediction"""
        predictions = self.inference.predict_future_interactions(days_ahead=7)

        assert isinstance(predictions, list)
        for prediction in predictions:
            assert "person1" in prediction
            assert "person2" in prediction
            assert "predicted_interaction" in prediction
            assert "confidence" in prediction

    def test_normalize_username(self):
        """Test username normalization"""
        normalized = self.inference._normalize_username("@Test.User_123!")
        assert normalized == "testuser123"

        normalized = self.inference._normalize_username("")
        assert normalized == ""

    def test_calculate_profile_similarity(self):
        """Test profile similarity calculation"""
        person1 = Person(id="user1", name="John Doe", platform="twitter", bio="Tech enthusiast")
        person2 = Person(id="user2", name="Jane Doe", platform="twitter", bio="Tech lover")

        similarity = self.inference._calculate_profile_similarity(person1, person2)
        assert 0 <= similarity <= 1


class TestSocialNetworkIntegration:
    """Integration tests for social network functionality"""

    def test_full_workflow(self):
        """Test complete social network analysis workflow"""
        # Create graph
        graph = SocialGraph()

        # Add people
        people = [
            Person(id="alice", name="Alice", platform="twitter"),
            Person(id="bob", name="Bob", platform="twitter"),
            Person(id="charlie", name="Charlie", platform="twitter"),
            Person(id="diana", name="Diana", platform="twitter")
        ]

        for person in people:
            graph.add_person(person)

        # Add relationships
        relationships = [
            Relationship(source_id="alice", target_id="bob", relationship_type="follow", strength=0.8),
            Relationship(source_id="bob", target_id="charlie", relationship_type="follow", strength=0.7),
            Relationship(source_id="charlie", target_id="diana", relationship_type="follow", strength=0.6),
            Relationship(source_id="alice", target_id="diana", relationship_type="mention", strength=0.5)
        ]

        for rel in relationships:
            graph.add_relationship(rel)

        # Test algorithms
        algorithms = GraphAlgorithms(graph)

        # Test centrality
        degree_centrality = algorithms.degree_centrality()
        assert len(degree_centrality) == 4

        # Test path finding
        path = algorithms.shortest_path("alice", "diana")
        assert len(path) >= 2
        assert path[0] == "alice"
        assert path[-1] == "diana"

        # Test analyzer
        analyzer = SocialNetworkAnalyzer(graph)
        analysis = analyzer.analyze_shared_content()
        assert isinstance(analysis, dict)

        # Test inference
        inference = RelationshipInference(graph)
        prediction = inference.predict_relationship_strength("alice", "bob")
        assert isinstance(prediction, dict)

        print("Full workflow test passed!")


if __name__ == "__main__":
    pytest.main([__file__])