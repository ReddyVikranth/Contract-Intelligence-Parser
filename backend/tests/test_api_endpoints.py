import pytest
import asyncio
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app
from app.models import ContractStatus
import io

@pytest.fixture
def mock_contract_service():
    """Mock contract service fixture"""
    service = MagicMock()
    service.upload_contract = AsyncMock()
    service.get_contract_status = AsyncMock()
    service.get_contract_data = AsyncMock()
    service.list_contracts = AsyncMock()
    service.download_contract = AsyncMock()
    return service

@pytest.mark.asyncio
class TestContractEndpoints:
    
    async def test_upload_contract_success(self, mock_contract_service):
        """Test successful contract upload"""
        # Mock service response
        contract_id = "test-contract-id"
        mock_contract_service.upload_contract.return_value = contract_id
        
        # Create test file
        file_content = b"Mock PDF content"
        files = {"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")}
        
        with patch('app.routers.contracts.get_contract_service', return_value=mock_contract_service):
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post("/api/contracts/upload", files=files)
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["contract_id"] == contract_id
        assert data["status"] == "pending"
        assert "successfully" in data["message"]
    
    async def test_upload_contract_invalid_file_type(self):
        """Test upload with invalid file type"""
        file_content = b"Not a PDF"
        files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/contracts/upload", files=files)
        
        assert response.status_code == 400
        assert "PDF files" in response.json()["detail"]
    
    async def test_upload_contract_file_too_large(self):
        """Test upload with file too large"""
        # Create a file larger than 50MB
        large_content = b"x" * (51 * 1024 * 1024)
        files = {"file": ("large.pdf", io.BytesIO(large_content), "application/pdf")}
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/contracts/upload", files=files)
        
        assert response.status_code == 400
        assert "50MB" in response.json()["detail"]
    
    async def test_get_contract_status_success(self, mock_contract_service):
        """Test successful status retrieval"""
        contract_id = "test-contract-id"
        expected_status = {
            "status": ContractStatus.PROCESSING,
            "progress_percentage": 75,
            "error_message": None
        }
        mock_contract_service.get_contract_status.return_value = expected_status
        
        with patch('app.routers.contracts.get_contract_service', return_value=mock_contract_service):
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get(f"/api/contracts/{contract_id}/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["contract_id"] == contract_id
        assert data["status"] == "processing"
        assert data["progress_percentage"] == 75
    
    async def test_get_contract_status_not_found(self, mock_contract_service):
        """Test status retrieval for non-existent contract"""
        contract_id = "non-existent-id"
        mock_contract_service.get_contract_status.return_value = None
        
        with patch('app.routers.contracts.get_contract_service', return_value=mock_contract_service):
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get(f"/api/contracts/{contract_id}/status")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    async def test_get_contract_data_success(self, mock_contract_service):
        """Test successful contract data retrieval"""
        contract_id = "test-contract-id"
        expected_data = {
            "contract_id": contract_id,
            "filename": "test.pdf",
            "file_size": 1024,
            "status": ContractStatus.COMPLETED,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T01:00:00",
            "progress_percentage": 100,
            "extracted_data": {"test": "data"},
            "confidence_scores": {"overall_score": 85},
            "gap_analysis": {"missing_fields": []}
        }
        mock_contract_service.get_contract_data.return_value = expected_data
        
        with patch('app.routers.contracts.get_contract_service', return_value=mock_contract_service):
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get(f"/api/contracts/{contract_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["contract_id"] == contract_id
        assert data["status"] == "completed"
    
    async def test_get_contract_data_not_ready(self, mock_contract_service):
        """Test contract data retrieval when not ready"""
        contract_id = "test-contract-id"
        contract_data = {
            "contract_id": contract_id,
            "status": ContractStatus.PROCESSING
        }
        mock_contract_service.get_contract_data.return_value = contract_data
        
        with patch('app.routers.contracts.get_contract_service', return_value=mock_contract_service):
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get(f"/api/contracts/{contract_id}")
        
        assert response.status_code == 400
        assert "not available" in response.json()["detail"]
    
    async def test_list_contracts_success(self, mock_contract_service):
        """Test successful contract listing"""
        expected_response = {
            "contracts": [
                {
                    "contract_id": "1",
                    "filename": "contract1.pdf",
                    "status": "completed"
                }
            ],
            "total": 1,
            "page": 1,
            "page_size": 10,
            "total_pages": 1
        }
        mock_contract_service.list_contracts.return_value = expected_response
        
        with patch('app.routers.contracts.get_contract_service', return_value=mock_contract_service):
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get("/api/contracts")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["contracts"]) == 1
    
    async def test_list_contracts_with_filters(self, mock_contract_service):
        """Test contract listing with filters"""
        mock_contract_service.list_contracts.return_value = {
            "contracts": [],
            "total": 0,
            "page": 1,
            "page_size": 10,
            "total_pages": 0
        }
        
        with patch('app.routers.contracts.get_contract_service', return_value=mock_contract_service):
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get("/api/contracts?status=completed&page=2&page_size=5")
        
        assert response.status_code == 200
        
        # Verify service was called with correct parameters
        mock_contract_service.list_contracts.assert_called_once_with(
            page=2,
            page_size=5,
            status=ContractStatus.COMPLETED
        )
    
    async def test_download_contract_success(self, mock_contract_service):
        """Test successful contract download"""
        contract_id = "test-contract-id"
        file_content = b"PDF content"
        filename = "test.pdf"
        
        mock_contract_service.download_contract.return_value = (file_content, filename)
        
        with patch('app.routers.contracts.get_contract_service', return_value=mock_contract_service):
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get(f"/api/contracts/{contract_id}/download")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert f"filename={filename}" in response.headers["content-disposition"]
        assert response.content == file_content
    
    async def test_download_contract_not_found(self, mock_contract_service):
        """Test download for non-existent contract"""
        contract_id = "non-existent-id"
        mock_contract_service.download_contract.return_value = None
        
        with patch('app.routers.contracts.get_contract_service', return_value=mock_contract_service):
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.get(f"/api/contracts/{contract_id}/download")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    async def test_health_check(self):
        """Test health check endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    async def test_root_endpoint(self):
        """Test root endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "Contract Intelligence Parser" in data["message"]
        assert "version" in data