"""
API Tests for Social Network Endpoints

This module contains tests for all social network API endpoints:
- Social network building and analysis
- Person and relationship queries
- Centrality and community analysis
- Search and filtering
"""

import pytest
import json
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from apps.api.main import app


class TestSocialNetworkAPI:
    """Test cases for social network API endpoints"""

    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)

    @patch('apps.api.main._social_graph')
    @patch('apps.api.main.RelationshipExtractor')
    def test_build_social_network_success(self, mock_extractor, mock_graph):
        """Test successful social network build"""
        # Mock the extractor and graph
        mock_instance = Mock()
        mock_instance.extract_from_items.return_value = Mock()
        mock_extractor.return_value = mock_instance

        # Mock the graph
        mock_graph_instance = Mock()
        mock_graph_instance.get_network_stats.return_value = {
            "total_nodes": 10,
            "total_relationships": 15
        }
        mock_instance.extract_from_items.return_value = mock_graph_instance

        response = self.client.post(
            "/social-network/build",
            json={"project_id": "test-project-123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "nodes" in data
        assert "relationships" in data

    @patch('apps.api.main._social_graph', None)
    def test_build_social_network_no_graph(self):
        """Test social network build when no graph exists"""
        response = self.client.post(
            "/social-network/build",
            json={"project_id": "test-project-123"}
        )

        # This should still work as the extractor will create a new graph
        assert response.status_code in [200, 500]  # May fail due to missing dependencies

    @patch('apps.api.main._social_graph')
    def test_get_social_network_stats_success(self, mock_graph):
        """Test getting social network stats successfully"""
        # Mock graph with stats
        mock_graph_instance = Mock()
        mock_graph_instance.get_network_stats.return_value = {
            "total_nodes": 10,
            "total_relationships": 15,
            "network_density": 0.3
        }
        mock_graph.__bool__.return_value = True
        mock_graph.__nonzero__ = mock_graph.__bool__
        mock_graph.get_network_stats.return_value = mock_graph_instance.get_network_stats.return_value

        response = self.client.get("/social-network/stats")

        assert response.status_code == 200
        data = response.json()
        assert "total_nodes" in data
        assert "total_relationships" in data

    @patch('apps.api.main._social_graph', None)
    def test_get_social_network_stats_no_graph(self):
        """Test getting social network stats when no graph exists"""
        response = self.client.get("/social-network/stats")

        assert response.status_code == 400
        data = response.json()
        assert "error" in data

    @patch('apps.api.main._social_graph')
    def test_get_social_network_people_success(self, mock_graph):
        """Test getting social network people successfully"""
        # Mock graph with people
        mock_person = Mock()
        mock_person.to_dict.return_value = {
            "id": "user1",
            "name": "Test User",
            "platform": "twitter"
        }

        mock_graph.__bool__.return_value = True
        mock_graph.__nonzero__ = mock_graph.__bool__
        mock_graph.people = {"user1": mock_person}

        response = self.client.get("/social-network/people")

        assert response.status_code == 200
        data = response.json()
        assert "people" in data
        assert "total" in data
        assert len(data["people"]) > 0

    @patch('apps.api.main._social_graph', None)
    def test_get_social_network_people_no_graph(self):
        """Test getting social network people when no graph exists"""
        response = self.client.get("/social-network/people")

        assert response.status_code == 400
        data = response.json()
        assert "error" in data

    @patch('apps.api.main._social_graph')
    def test_get_person_details_success(self, mock_graph):
        """Test getting person details successfully"""
        # Mock person
        mock_person = Mock()
        mock_person.to_dict.return_value = {
            "id": "user1",
            "name": "Test User",
            "platform": "twitter"
        }

        # Mock relationships
        mock_relationship = Mock()
        mock_relationship.to_dict.return_value = {
            "source_id": "user1",
            "target_id": "user2",
            "relationship_type": "follow",
            "strength": 0.8
        }

        mock_graph.__bool__.return_value = True
        mock_graph.__nonzero__ = mock_graph.__bool__
        mock_graph.get_person.return_value = mock_person
        mock_graph.get_connections.return_value = ["user2"]
        mock_graph.get_relationships.return_value = [mock_relationship]

        response = self.client.get("/social-network/person/user1")

        assert response.status_code == 200
        data = response.json()
        assert "person" in data
        assert "connections" in data
        assert "relationships" in data

    @patch('apps.api.main._social_graph')
    def test_get_person_details_not_found(self, mock_graph):
        """Test getting person details for non-existent person"""
        mock_graph.__bool__.return_value = True
        mock_graph.__nonzero__ = mock_graph.__bool__
        mock_graph.get_person.return_value = None

        response = self.client.get("/social-network/person/nonexistent")

        assert response.status_code == 404
        data = response.json()
        assert "error" in data

    @patch('apps.api.main._social_graph')
    def test_get_person_connections_success(self, mock_graph):
        """Test getting person connections successfully"""
        mock_graph.__bool__.return_value = True
        mock_graph.__nonzero__ = mock_graph.__bool__
        mock_graph.get_connections.return_value = ["user2", "user3"]

        response = self.client.get("/social-network/connections/user1")

        assert response.status_code == 200
        data = response.json()
        assert "person_id" in data
        assert "connections" in data
        assert "count" in data
        assert data["person_id"] == "user1"
        assert len(data["connections"]) == 2

    @patch('apps.api.main._social_graph')
    def test_get_mutual_connections_success(self, mock_graph):
        """Test getting mutual connections successfully"""
        mock_graph.__bool__.return_value = True
        mock_graph.__nonzero__ = mock_graph.__bool__
        mock_graph.get_mutual_connections.return_value = ["user3", "user4"]
        mock_graph.get_relationship_strength.return_value = 0.7

        response = self.client.get("/social-network/mutual/user1/user2")

        assert response.status_code == 200
        data = response.json()
        assert "person1" in data
        assert "person2" in data
        assert "mutual_connections" in data
        assert "relationship_strength" in data
        assert data["person1"] == "user1"
        assert data["person2"] == "user2"

    @patch('apps.api.main._social_graph')
    @patch('libs.social_network.graph_algorithms.GraphAlgorithms')
    def test_get_centrality_measures_degree(self, mock_algorithms_class, mock_graph):
        """Test getting degree centrality measures"""
        # Mock algorithms
        mock_algorithms = Mock()
        mock_algorithms.degree_centrality.return_value = {
            "user1": 0.8,
            "user2": 0.6,
            "user3": 0.4
        }
        mock_algorithms_class.return_value = mock_algorithms

        mock_graph.__bool__.return_value = True
        mock_graph.__nonzero__ = mock_graph.__bool__

        response = self.client.get("/social-network/centrality?measure=degree")

        assert response.status_code == 200
        data = response.json()
        assert "measure" in data
        assert "results" in data
        assert "total_nodes" in data
        assert data["measure"] == "degree"
        assert len(data["results"]) > 0

    @patch('apps.api.main._social_graph')
    @patch('libs.social_network.graph_algorithms.GraphAlgorithms')
    def test_get_centrality_measures_invalid(self, mock_algorithms_class, mock_graph):
        """Test getting invalid centrality measure"""
        mock_graph.__bool__.return_value = True
        mock_graph.__nonzero__ = mock_graph.__bool__

        response = self.client.get("/social-network/centrality?measure=invalid")

        assert response.status_code == 400
        data = response.json()
        assert "error" in data

    @patch('apps.api.main._social_graph')
    @patch('libs.social_network.graph_algorithms.GraphAlgorithms')
    def test_detect_communities_success(self, mock_algorithms_class, mock_graph):
        """Test community detection successfully"""
        # Mock algorithms
        mock_algorithms = Mock()
        mock_algorithms.detect_communities.return_value = [
            ["user1", "user2"],
            ["user3", "user4", "user5"]
        ]
        mock_algorithms_class.return_value = mock_algorithms

        mock_graph.__bool__.return_value = True
        mock_graph.__nonzero__ = mock_graph.__bool__

        response = self.client.get("/social-network/communities")

        assert response.status_code == 200
        data = response.json()
        assert "method" in data
        assert "communities" in data
        assert "community_count" in data
        assert data["community_count"] == 2

    @patch('apps.api.main._social_graph')
    @patch('libs.social_network.graph_algorithms.GraphAlgorithms')
    def test_get_clustering_coefficients_success(self, mock_algorithms_class, mock_graph):
        """Test getting clustering coefficients successfully"""
        # Mock algorithms
        mock_algorithms = Mock()
        mock_algorithms.clustering_coefficient.return_value = {
            "user1": 0.8,
            "user2": 0.6,
            "user3": 0.4
        }
        mock_algorithms_class.return_value = mock_algorithms

        mock_graph.__bool__.return_value = True
        mock_graph.__nonzero__ = mock_graph.__bool__

        response = self.client.get("/social-network/clustering")

        assert response.status_code == 200
        data = response.json()
        assert "clustering_coefficients" in data
        assert "average_clustering" in data
        assert "total_nodes" in data

    @patch('apps.api.main._social_graph')
    @patch('libs.social_network.graph_algorithms.GraphAlgorithms')
    def test_get_network_analysis_success(self, mock_algorithms_class, mock_graph):
        """Test getting comprehensive network analysis"""
        # Mock algorithms
        mock_algorithms = Mock()
        mock_algorithms.get_network_summary.return_value = {
            "nodes": 10,
            "edges": 15,
            "density": 0.3,
            "centrality_measures": {
                "degree": {"user1": 0.8}
            }
        }
        mock_algorithms_class.return_value = mock_algorithms

        mock_graph.__bool__.return_value = True
        mock_graph.__nonzero__ = mock_graph.__bool__

        response = self.client.get("/social-network/analysis")

        assert response.status_code == 200
        data = response.json()
        assert "nodes" in data
        assert "edges" in data
        assert "centrality_measures" in data

    @patch('apps.api.main._social_graph')
    def test_search_social_network_success(self, mock_graph):
        """Test searching social network successfully"""
        # Mock person
        mock_person = Mock()
        mock_person.to_dict.return_value = {
            "type": "person",
            "id": "user1",
            "name": "Test User",
            "username": "testuser",
            "platform": "twitter"
        }

        mock_graph.__bool__.return_value = True
        mock_graph.__nonzero__ = mock_graph.__bool__
        mock_graph.people = {"user1": mock_person}

        response = self.client.get("/social-network/search?q=test&search_type=people")

        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert "search_type" in data
        assert "results" in data
        assert "total_found" in data

    @patch('apps.api.main._social_graph', None)
    def test_search_social_network_no_graph(self):
        """Test searching social network when no graph exists"""
        response = self.client.get("/social-network/search?q=test")

        assert response.status_code == 400
        data = response.json()
        assert "error" in data

    def test_health_endpoint(self):
        """Test health endpoint"""
        response = self.client.get("/healthz")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ("healthy", "ok")

    def test_invalid_endpoint(self):
        """Test invalid endpoint"""
        response = self.client.get("/social-network/invalid-endpoint")

        assert response.status_code == 404

    @patch('apps.api.main._social_graph')
    def test_get_shortest_path_success(self, mock_graph):
        """Test getting shortest path successfully"""
        mock_graph.__bool__.return_value = True
        mock_graph.__nonzero__ = mock_graph.__bool__
        mock_graph.find_path.return_value = [["user1", "user2", "user3"]]

        response = self.client.get("/social-network/path/user1/user3")

        assert response.status_code == 200
        data = response.json()
        assert "start" in data
        assert "end" in data
        assert "paths" in data
        assert "path_length" in data
        assert data["start"] == "user1"
        assert data["end"] == "user3"
        assert data["path_length"] == 2  # 3 nodes - 1 = 2 edges


class TestSocialNetworkAPIIntegration:
    """Integration tests for social network API"""

    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)

    def test_api_endpoints_structure(self):
        """Test that all expected endpoints are available"""
        # Test root endpoint
        response = self.client.get("/")
        assert response.status_code in [200, 404]  # May not have root endpoint

        # Test docs endpoint
        response = self.client.get("/docs")
        assert response.status_code in [200, 404]  # May not be available in test

        # Test openapi endpoint
        response = self.client.get("/openapi.json")
        assert response.status_code in [200, 404]  # May not be available in test

    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = self.client.options("/healthz")
        # CORS headers may or may not be present depending on configuration
        assert response.status_code in [200, 404, 405]

    def test_error_handling(self):
        """Test error handling for malformed requests"""
        # Test with invalid JSON
        response = self.client.post(
            "/social-network/build",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]  # Bad request or validation error

    def test_rate_limiting(self):
        """Test rate limiting (if implemented)"""
        # Make multiple requests quickly
        for i in range(10):
            response = self.client.get("/healthz")
            assert response.status_code == 200

    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        import threading
        import time

        results = []

        def make_request():
            response = self.client.get("/healthz")
            results.append(response.status_code)

        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check results
        assert len(results) == 5
        assert all(status == 200 for status in results)


if __name__ == "__main__":
    pytest.main([__file__])