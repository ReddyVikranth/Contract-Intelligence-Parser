import uuid
import os
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from fastapi import UploadFile
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models import ContractStatus
from app.tasks.contract_tasks import process_contract
import logging

logger = logging.getLogger(__name__)

class ContractService:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.contracts_collection = database.contracts
        self.files_collection = database.files
    
    async def upload_contract(self, file: UploadFile, file_size: int) -> str:
        """Upload contract file and initiate processing"""
        contract_id = str(uuid.uuid4())
        
        # Read file content
        content = await file.read()
        
        # Store file in database
        file_doc = {
            "contract_id": contract_id,
            "filename": file.filename,
            "content": content,
            "content_type": file.content_type,
            "size": file_size,
            "created_at": datetime.utcnow()
        }
        
        await self.files_collection.insert_one(file_doc)
        
        # Create contract record
        contract_doc = {
            "contract_id": contract_id,
            "filename": file.filename,
            "file_size": file_size,
            "status": ContractStatus.PENDING,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "progress_percentage": 0,
            "error_message": None,
            "extracted_data": None,
            "confidence_scores": None,
            "gap_analysis": None
        }
        
        await self.contracts_collection.insert_one(contract_doc)
        
        # Trigger async processing task
        process_contract.delay(contract_id)
        logger.info(f"Contract {contract_id} uploaded successfully")
        
        return contract_id
    
    async def get_contract_status(self, contract_id: str) -> Optional[Dict[str, Any]]:
        """Get contract processing status"""
        contract = await self.contracts_collection.find_one(
            {"contract_id": contract_id},
            {
                "status": 1,
                "progress_percentage": 1,
                "error_message": 1,
                "_id": 0
            }
        )
        return contract
    
    async def get_contract_data(self, contract_id: str) -> Optional[Dict[str, Any]]:
        """Get complete contract data"""
        contract = await self.contracts_collection.find_one(
            {"contract_id": contract_id},
            {"_id": 0}
        )
        return contract
    
    async def list_contracts(
        self, 
        page: int = 1, 
        page_size: int = 10,
        status: Optional[ContractStatus] = None
    ) -> Dict[str, Any]:
        """Get paginated list of contracts"""
        skip = (page - 1) * page_size
        
        # Build query filter
        query_filter = {}
        if status:
            query_filter["status"] = status
        
        # Get total count
        total = await self.contracts_collection.count_documents(query_filter)
        
        # Get contracts
        cursor = self.contracts_collection.find(
            query_filter,
            {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(page_size)
        
        contracts = await cursor.to_list(length=page_size)
        
        total_pages = (total + page_size - 1) // page_size
        
        return {
            "contracts": contracts,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    
    async def download_contract(self, contract_id: str) -> Optional[Tuple[bytes, str]]:
        """Download original contract file"""
        file_doc = await self.files_collection.find_one(
            {"contract_id": contract_id},
            {"content": 1, "filename": 1, "_id": 0}
        )
        
        if file_doc:
            return file_doc["content"], file_doc["filename"]
        
        return None
    
    async def update_contract_status(
        self,
        contract_id: str,
        status: ContractStatus,
        progress_percentage: int = 0,
        error_message: Optional[str] = None,
        extracted_data: Optional[Dict[str, Any]] = None,
        confidence_scores: Optional[Dict[str, Any]] = None,
        gap_analysis: Optional[Dict[str, Any]] = None
    ):
        """Update contract processing status and data"""
        update_doc = {
            "status": status,
            "updated_at": datetime.utcnow(),
            "progress_percentage": progress_percentage
        }
        
        if error_message:
            update_doc["error_message"] = error_message
        
        if extracted_data:
            update_doc["extracted_data"] = extracted_data
            
        if confidence_scores:
            update_doc["confidence_scores"] = confidence_scores
            
        if gap_analysis:
            update_doc["gap_analysis"] = gap_analysis
        
        await self.contracts_collection.update_one(
            {"contract_id": contract_id},
            {"$set": update_doc}
        )