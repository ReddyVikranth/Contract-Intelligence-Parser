import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import UploadFile
from app.services.contract_service import ContractService
from app.models import ContractStatus
import io

@pytest.fixture
def mock_database():
    """Mock database fixture"""
    db = MagicMock()
    db.contracts = AsyncMock()
    db.files = AsyncMock()
    return db

@pytest.fixture
def contract_service(mock_database):
    """Contract service fixture"""
    return ContractService(mock_database)

@pytest.fixture
def mock_upload_file():
    """Mock upload file fixture"""
    file_content = b"Mock PDF content"
    file = MagicMock(spec=UploadFile)
    file.filename = "test_contract.pdf"
    file.content_type = "application/pdf"
    file.read = AsyncMock(return_value=file_content)
    return file

class TestContractService:
    
    @pytest.mark.asyncio
    async def test_upload_contract_success(self, contract_service, mock_upload_file, mock_database):
        """Test successful contract upload"""
        # Mock database operations
        mock_database.files.insert_one = AsyncMock()
        mock_database.contracts.insert_one = AsyncMock()
        
        # Mock Celery task
        with patch('app.services.contract_service.process_contract') as mock_task:
            mock_task.delay = MagicMock()
            
            # Execute
            contract_id = await contract_service.upload_contract(mock_upload_file, 1024)
            
            # Assertions
            assert contract_id is not None
            assert len(contract_id) == 36  # UUID length
            mock_database.files.insert_one.assert_called_once()
            mock_database.contracts.insert_one.assert_called_once()
            mock_task.delay.assert_called_once_with(contract_id)

    @pytest.mark.asyncio
    async def test_get_contract_status_found(self, contract_service, mock_database):
        """Test getting contract status when contract exists"""
        # Mock data
        contract_id = "test-contract-id"
        expected_status = {
            "status": ContractStatus.PROCESSING,
            "progress_percentage": 50,
            "error_message": None
        }
        
        mock_database.contracts.find_one = AsyncMock(return_value=expected_status)
        
        # Execute
        result = await contract_service.get_contract_status(contract_id)
        
        # Assertions
        assert result == expected_status
        mock_database.contracts.find_one.assert_called_once_with(
            {"contract_id": contract_id},
            {
                "status": 1,
                "progress_percentage": 1,
                "error_message": 1,
                "_id": 0
            }
        )

    @pytest.mark.asyncio
    async def test_get_contract_status_not_found(self, contract_service, mock_database):
        """Test getting contract status when contract doesn't exist"""
        contract_id = "non-existent-id"
        mock_database.contracts.find_one = AsyncMock(return_value=None)
        
        # Execute
        result = await contract_service.get_contract_status(contract_id)
        
        # Assertions
        assert result is None

    @pytest.mark.asyncio
    async def test_get_contract_data_success(self, contract_service, mock_database):
        """Test getting complete contract data"""
        contract_id = "test-contract-id"
        expected_data = {
            "contract_id": contract_id,
            "filename": "test.pdf",
            "status": ContractStatus.COMPLETED,
            "extracted_data": {"test": "data"}
        }
        
        mock_database.contracts.find_one = AsyncMock(return_value=expected_data)
        
        # Execute
        result = await contract_service.get_contract_data(contract_id)
        
        # Assertions
        assert result == expected_data
        mock_database.contracts.find_one.assert_called_once_with(
            {"contract_id": contract_id},
            {"_id": 0}
        )

    @pytest.mark.asyncio
    async def test_list_contracts_with_pagination(self, contract_service, mock_database):
        """Test listing contracts with pagination"""
        # Mock data
        mock_contracts = [
            {"contract_id": "1", "filename": "contract1.pdf"},
            {"contract_id": "2", "filename": "contract2.pdf"}
        ]
        
        mock_database.contracts.count_documents = AsyncMock(return_value=10)
        
        # Mock cursor
        mock_cursor = AsyncMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.to_list = AsyncMock(return_value=mock_contracts)
        
        mock_database.contracts.find.return_value = mock_cursor
        
        # Execute
        result = await contract_service.list_contracts(page=1, page_size=2)
        
        # Assertions
        assert result["contracts"] == mock_contracts
        assert result["total"] == 10
        assert result["page"] == 1
        assert result["page_size"] == 2
        assert result["total_pages"] == 5

    @pytest.mark.asyncio
    async def test_list_contracts_with_status_filter(self, contract_service, mock_database):
        """Test listing contracts with status filter"""
        status_filter = ContractStatus.COMPLETED
        
        mock_database.contracts.count_documents = AsyncMock(return_value=5)
        
        # Mock cursor
        mock_cursor = AsyncMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.to_list = AsyncMock(return_value=[])
        
        mock_database.contracts.find.return_value = mock_cursor
        
        # Execute
        await contract_service.list_contracts(status=status_filter)
        
        # Assertions
        mock_database.contracts.count_documents.assert_called_once_with({"status": status_filter})
        mock_database.contracts.find.assert_called_once_with({"status": status_filter}, {"_id": 0})

    @pytest.mark.asyncio
    async def test_download_contract_success(self, contract_service, mock_database):
        """Test successful contract download"""
        contract_id = "test-contract-id"
        file_content = b"PDF content"
        filename = "test.pdf"
        
        mock_database.files.find_one = AsyncMock(return_value={
            "content": file_content,
            "filename": filename
        })
        
        # Execute
        result = await contract_service.download_contract(contract_id)
        
        # Assertions
        assert result == (file_content, filename)
        mock_database.files.find_one.assert_called_once_with(
            {"contract_id": contract_id},
            {"content": 1, "filename": 1, "_id": 0}
        )

    @pytest.mark.asyncio
    async def test_download_contract_not_found(self, contract_service, mock_database):
        """Test contract download when file not found"""
        contract_id = "non-existent-id"
        mock_database.files.find_one = AsyncMock(return_value=None)
        
        # Execute
        result = await contract_service.download_contract(contract_id)
        
        # Assertions
        assert result is None

    @pytest.mark.asyncio
    async def test_update_contract_status(self, contract_service, mock_database):
        """Test updating contract status"""
        contract_id = "test-contract-id"
        status = ContractStatus.COMPLETED
        progress = 100
        extracted_data = {"test": "data"}
        
        mock_database.contracts.update_one = AsyncMock()
        
        # Execute
        await contract_service.update_contract_status(
            contract_id=contract_id,
            status=status,
            progress_percentage=progress,
            extracted_data=extracted_data
        )
        
        # Assertions
        mock_database.contracts.update_one.assert_called_once()
        call_args = mock_database.contracts.update_one.call_args
        
        # Check filter
        assert call_args[0][0] == {"contract_id": contract_id}
        
        # Check update document
        update_doc = call_args[0][1]["$set"]
        assert update_doc["status"] == status
        assert update_doc["progress_percentage"] == progress
        assert update_doc["extracted_data"] == extracted_data
        assert "updated_at" in update_doc