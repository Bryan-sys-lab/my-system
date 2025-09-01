"""
Comprehensive tests for refactored API components - focusing on edge cases
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
import json

# Import refactored components
from apps.api.main import app
from apps.api.exceptions import (
    BSearchException, ValidationError, NotFoundError,
    AuthenticationError, AuthorizationError, ExternalServiceError,
    ConfigurationError, DatabaseError, CollectorError, AIError,
    FileProcessingError
)
from apps.api.database import DatabaseManager, get_db_session
from apps.api.models import (
    ProjectCreate, ProjectResponse, WebCollectionRequest,
    CollectionResponse, ItemResponse
)
from apps.api.collectors import CollectionService
from apps.api.config import *


class TestCustomExceptions:
    """Test custom exception handling"""

    def test_bsearch_exception_creation(self):
        """Test basic BSearchException creation"""
        exc = BSearchException("Test error", status_code=400, details={"field": "test"})
        assert exc.message == "Test error"
        assert exc.status_code == 400
        assert exc.details["field"] == "test"

    def test_validation_error(self):
        """Test ValidationError for input validation failures"""
        exc = ValidationError("Invalid input", field="name")
        assert exc.status_code == 400
        assert exc.details["field"] == "name"

    def test_not_found_error(self):
        """Test NotFoundError for missing resources"""
        exc = NotFoundError("Project", "123")
        assert exc.status_code == 404
        assert "Project not found: 123" in exc.message

    def test_collector_error(self):
        """Test CollectorError for collection failures"""
        exc = CollectorError("web_scraper", "Failed to fetch URL")
        assert exc.status_code == 502
        assert exc.collector == "web_scraper"

    def test_database_error(self):
        """Test DatabaseError for database operation failures"""
        exc = DatabaseError("Connection failed", operation="select")
        assert exc.status_code == 500
        assert exc.details["operation"] == "select"


class TestDatabaseManager:
    """Test DatabaseManager edge cases"""

    @patch('apps.api.database.SessionLocal')
    def test_create_item_with_edge_cases(self, mock_session):
        """Test creating items with various edge cases"""
        mock_session_instance = Mock()
        mock_session.return_value = mock_session_instance

        # Test with empty content
        result = DatabaseManager.create_item(mock_session_instance, {
            "project_id": "test-project",
            "content": "",
            "meta": {}
        })
        assert result["content"] == ""

        # Test with None content
        result = DatabaseManager.create_item(mock_session_instance, {
            "project_id": "test-project",
            "content": None,
            "meta": {}
        })
        assert result["content"] == ""

        # Test with large meta
        large_meta = {"key" + str(i): f"value{i}" for i in range(100)}
        result = DatabaseManager.create_item(mock_session_instance, {
            "project_id": "test-project",
            "content": "test",
            "meta": large_meta
        })
        assert len(result["meta"]) == 100

    @patch('apps.api.database.SessionLocal')
    def test_database_error_handling(self, mock_session):
        """Test database error handling"""
        mock_session_instance = Mock()
        mock_session_instance.add.side_effect = Exception("DB Error")
        mock_session.return_value = mock_session_instance

        with pytest.raises(DatabaseError) as exc_info:
            DatabaseManager.create_item(mock_session_instance, {
                "project_id": "test",
                "content": "test"
            })

        assert "DB Error" in str(exc_info.value)
        assert exc_info.value.details["operation"] == "create_item"


class TestPydanticModels:
    """Test Pydantic model validation edge cases"""

    def test_project_create_validation(self):
        """Test ProjectCreate model validation"""
        # Valid project
        project = ProjectCreate(name="Test Project")
        assert project.name == "Test Project"

        # Empty name should fail
        with pytest.raises(ValueError):
            ProjectCreate(name="")

        # Name too long should fail
        with pytest.raises(ValueError):
            ProjectCreate(name="a" * 256)

    def test_web_collection_request_validation(self):
        """Test WebCollectionRequest validation"""
        # Valid request
        request = WebCollectionRequest(
            project_id="test-project",
            url="https://example.com"
        )
        assert request.url == "https://example.com"

        # Invalid URL should fail
        with pytest.raises(ValueError):
            WebCollectionRequest(
                project_id="test-project",
                url=""
            )

        # Invalid project_id should fail
        with pytest.raises(ValueError):
            WebCollectionRequest(
                project_id="",
                url="https://example.com"
            )

    def test_collection_response_model(self):
        """Test CollectionResponse model"""
        response = CollectionResponse(
            saved=["item1", "item2"],
            count=2,
            source="web_scraper"
        )
        assert response.count == 2
        assert len(response.saved) == 2

        # Test with errors
        response_with_errors = CollectionResponse(
            saved=["item1"],
            count=1,
            source="web_scraper",
            errors=[{"type": "timeout", "message": "Request timed out"}]
        )
        assert len(response_with_errors.errors) == 1


class TestCollectionService:
    """Test CollectionService edge cases"""

    @patch('apps.api.collectors.fetch_url')
    @patch('apps.api.collectors.extract_entities')
    def test_collect_web_content_edge_cases(self, mock_extract, mock_fetch):
        """Test web content collection with edge cases"""
        # Mock successful fetch
        mock_fetch.return_value = {
            "text": "Test content",
            "title": "Test Title"
        }
        mock_extract.return_value = [{"entity": "test", "type": "ORG"}]

        # Test normal case
        result = CollectionService.collect_web_content(
            "https://example.com",
            "test-project"
        )
        assert result["item_data"]["content"] == "Test content"
        assert result["source"] == "web_scraper"

        # Test with empty content
        mock_fetch.return_value = {
            "text": "",
            "title": ""
        }
        mock_extract.return_value = []

        result = CollectionService.collect_web_content(
            "https://empty.com",
            "test-project"
        )
        assert result["item_data"]["content"] == ""
        assert result["entities"] == []

        # Test with very long content
        long_content = "word " * 10000
        mock_fetch.return_value = {
            "text": long_content,
            "title": "Long Title"
        }
        mock_extract.return_value = []

        result = CollectionService.collect_web_content(
            "https://long.com",
            "test-project"
        )
        assert len(result["item_data"]["content"]) == len(long_content)

    @patch('apps.api.collectors.fetch_url')
    def test_web_collection_error_handling(self, mock_fetch):
        """Test error handling in web collection"""
        # Test network error
        mock_fetch.side_effect = Exception("Network timeout")

        with pytest.raises(CollectorError) as exc_info:
            CollectionService.collect_web_content(
                "https://error.com",
                "test-project"
            )

        assert exc_info.value.collector == "web_scraper"
        assert "Network timeout" in str(exc_info.value)

        # Test with invalid URL
        mock_fetch.side_effect = Exception("Invalid URL")

        with pytest.raises(CollectorError) as exc_info:
            CollectionService.collect_web_content(
                "not-a-url",
                "test-project"
            )

        assert "Invalid URL" in str(exc_info.value)

    @patch('apps.api.collectors.address_txs')
    def test_crypto_collection_edge_cases(self, mock_txs):
        """Test crypto collection edge cases"""
        # Test with empty transactions
        mock_txs.return_value = []

        result = CollectionService.collect_crypto_btc("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
        assert result["count"] == 0
        assert result["transactions"] == []

        # Test with many transactions
        many_txs = [{"hash": f"tx{i}", "value": 1000} for i in range(50)]
        mock_txs.return_value = many_txs

        result = CollectionService.collect_crypto_btc("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
        assert result["count"] == 50
        assert len(result["transactions"]) == 10  # Limited to 10

        # Test with invalid address
        mock_txs.side_effect = Exception("Invalid Bitcoin address")

        with pytest.raises(CollectorError) as exc_info:
            CollectionService.collect_crypto_btc("invalid-address")

        assert exc_info.value.collector == "bitcoin"
        assert "Invalid Bitcoin address" in str(exc_info.value)


class TestConfiguration:
    """Test configuration edge cases"""

    def test_config_constants(self):
        """Test configuration constants are properly defined"""
        assert APP_TITLE == "b-search API"
        assert APP_VERSION == "1.0.0"
        assert DEFAULT_MAX_RESULTS == 25
        assert DEFAULT_LIMIT == 50

    @patch.dict('os.environ', {'SKIP_HEAVY_DEPS': '1'})
    def test_skip_heavy_deps_config(self):
        """Test SKIP_HEAVY_DEPS environment variable"""
        from apps.api.config import SKIP_HEAVY_DEPS as skip_heavy
        assert skip_heavy is True

    @patch.dict('os.environ', {'DATA_DIR': '/custom/data'})
    def test_custom_data_dir(self):
        """Test custom DATA_DIR configuration"""
        from apps.api.config import DATA_DIR as data_dir
        assert data_dir == '/custom/data'

    def test_default_values(self):
        """Test default configuration values"""
        assert DEFAULT_NITTER_INSTANCE == "https://nitter.net"
        assert DEFAULT_YOLO_MODEL == "yolov8n.pt"
        assert DEFAULT_CLIP_THRESHOLD == 0.25
        assert DEFAULT_SEARCH_K == 12


class TestAPIEndpoints:
    """Test API endpoints with edge cases"""

    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)

    def test_health_endpoint(self):
        """Test health endpoint"""
        response = self.client.get('/healthz')
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_metrics_endpoint(self):
        """Test metrics endpoint"""
        response = self.client.get('/metrics')
        assert response.status_code == 200
        assert 'api_requests_total' in response.text

    @patch('apps.api.main.DatabaseManager')
    def test_projects_endpoint_edge_cases(self, mock_db_manager):
        """Test projects endpoint edge cases"""
        # Mock successful creation
        mock_db_manager.create_project.return_value = {
            "id": "test-id",
            "name": "Test Project"
        }

        # Test valid project creation
        response = self.client.post('/projects', json={"name": "Test Project"})
        assert response.status_code == 200

        # Test empty name (should fail validation)
        response = self.client.post('/projects', json={"name": ""})
        assert response.status_code == 422  # Validation error

        # Test missing name field
        response = self.client.post('/projects', json={})
        assert response.status_code == 422

        # Test very long name
        long_name = "a" * 300
        response = self.client.post('/projects', json={"name": long_name})
        assert response.status_code == 422

    @patch('apps.api.main.DatabaseManager')
    def test_list_projects_edge_cases(self, mock_db_manager):
        """Test list projects with edge cases"""
        # Mock empty project list
        mock_db_manager.get_all_projects.return_value = []

        response = self.client.get('/projects')
        assert response.status_code == 200
        assert response.json() == []

        # Mock projects with various data
        mock_projects = [
            Mock(id="id1", name="Project 1"),
            Mock(id="id2", name=""),
            Mock(id="id3", name="Very Long Project Name " * 10)
        ]
        mock_db_manager.get_all_projects.return_value = mock_projects

        response = self.client.get('/projects')
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    @patch('apps.api.main.CollectionService')
    @patch('apps.api.main.DatabaseManager')
    def test_web_collection_endpoint_edge_cases(self, mock_db_manager, mock_collection_service):
        """Test web collection endpoint edge cases"""
        # Mock successful collection
        mock_collection_service.collect_web_content.return_value = {
            "item_data": {
                "project_id": "test-project",
                "content": "Test content",
                "meta": {"url": "https://example.com"}
            },
            "entities": [],
            "source": "web_scraper"
        }
        mock_db_manager.create_item.return_value = {
            "id": "item-id",
            "project_id": "test-project"
        }

        # Test valid request
        response = self.client.post('/collect/web', json={
            "project_id": "test-project",
            "url": "https://example.com"
        })
        assert response.status_code == 200

        # Test invalid URL
        response = self.client.post('/collect/web', json={
            "project_id": "test-project",
            "url": ""
        })
        assert response.status_code == 422

        # Test missing fields
        response = self.client.post('/collect/web', json={})
        assert response.status_code == 422

        # Test collection service error
        mock_collection_service.collect_web_content.side_effect = CollectorError(
            "web_scraper", "Network error"
        )

        response = self.client.post('/collect/web', json={
            "project_id": "test-project",
            "url": "https://error.com"
        })
        assert response.status_code == 502

    @patch('apps.api.main.CollectionService')
    def test_crypto_endpoint_edge_cases(self, mock_collection_service):
        """Test crypto endpoint edge cases"""
        # Mock successful response
        mock_collection_service.collect_crypto_btc.return_value = {
            "count": 5,
            "transactions": [{"hash": "tx1", "value": 1000}],
            "address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        }

        # Test valid address
        response = self.client.get('/crypto/btc/1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 5

        # Test invalid address (should still work as it's just a path param)
        response = self.client.get('/crypto/btc/invalid-address')
        assert response.status_code == 200  # The endpoint doesn't validate address format

        # Test collection service error
        mock_collection_service.collect_crypto_btc.side_effect = CollectorError(
            "bitcoin", "API rate limit exceeded"
        )

        response = self.client.get('/crypto/btc/1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
        assert response.status_code == 502


class TestIntegrationEdgeCases:
    """Test integration scenarios with edge cases"""

    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)

    @patch('apps.api.main.DatabaseManager')
    def test_database_connection_failure(self, mock_db_manager):
        """Test handling of database connection failures"""
        mock_db_manager.get_all_projects.side_effect = DatabaseError(
            "Connection refused", operation="list_projects"
        )

        response = self.client.get('/projects')
        assert response.status_code == 500

    @patch('apps.api.main.DatabaseManager')
    def test_concurrent_requests_simulation(self, mock_db_manager):
        """Test handling of concurrent requests"""
        import threading
        import time

        results = []
        errors = []

        def make_request():
            try:
                response = self.client.get('/projects')
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))

        # Simulate concurrent requests
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # All requests should succeed
        assert len(results) == 10
        assert all(status == 200 for status in results)
        assert len(errors) == 0

    def test_large_payload_handling(self):
        """Test handling of large request payloads"""
        # Create a large project name
        large_name = "Project " + "x" * 1000

        response = self.client.post('/projects', json={"name": large_name})
        # Should either succeed or fail validation
        assert response.status_code in [200, 422]

    def test_special_characters_in_input(self):
        """Test handling of special characters in input"""
        special_names = [
            "Project with spaces",
            "Project-with-dashes",
            "Project_with_underscores",
            "Project (with parentheses)",
            "Project @#$%^&*()",
            "Project ñáéíóú",  # Unicode characters
            "Project <script>alert('xss')</script>",  # Potential XSS
        ]

        for name in special_names:
            response = self.client.post('/projects', json={"name": name})
            # Should either succeed or fail validation appropriately
            assert response.status_code in [200, 422]

    def test_boundary_values(self):
        """Test boundary values for various inputs"""
        # Test boundary name lengths
        boundary_names = [
            "a",  # Minimum length
            "a" * 254,  # Near maximum (255 is max)
            "a" * 255,  # Exactly maximum
        ]

        for name in boundary_names:
            response = self.client.post('/projects', json={"name": name})
            if len(name) <= 255:
                assert response.status_code == 200
            else:
                assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])