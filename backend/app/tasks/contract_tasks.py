import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from celery import current_task
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import pdfplumber
import re
from app.celery_app import celery_app
from app.models import ContractStatus
from app.services.contract_parser import ContractParser

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def process_contract(self, contract_id: str):
    """Process contract file asynchronously"""
    try:
        # Update status to processing
        asyncio.run(update_contract_status(
            contract_id, 
            ContractStatus.PROCESSING, 
            progress_percentage=10
        ))
        
        # Get file content from database
        file_content = asyncio.run(get_file_content(contract_id))
        if not file_content:
            raise Exception("File content not found")
        
        # Update progress
        current_task.update_state(
            state='PROGRESS',
            meta={'progress': 30, 'status': 'Extracting text from PDF'}
        )
        
        # Extract text from PDF
        text_content = extract_pdf_text(file_content)
        
        # Update progress
        asyncio.run(update_contract_status(
            contract_id, 
            ContractStatus.PROCESSING, 
            progress_percentage=50
        ))
        
        # Parse contract data
        parser = ContractParser()
        extracted_data = parser.parse_contract(text_content)
        
        # Update progress
        asyncio.run(update_contract_status(
            contract_id, 
            ContractStatus.PROCESSING, 
            progress_percentage=70
        ))
        
        # Calculate confidence scores
        confidence_scores = parser.calculate_confidence_scores(extracted_data)
        
        # Perform gap analysis
        gap_analysis = parser.perform_gap_analysis(extracted_data)
        
        # Update progress
        asyncio.run(update_contract_status(
            contract_id, 
            ContractStatus.PROCESSING, 
            progress_percentage=90
        ))
        
        # Save results to database
        asyncio.run(update_contract_status(
            contract_id,
            ContractStatus.COMPLETED,
            progress_percentage=100,
            extracted_data=extracted_data,
            confidence_scores=confidence_scores,
            gap_analysis=gap_analysis
        ))
        
        logger.info(f"Contract {contract_id} processed successfully")
        return {"status": "completed", "contract_id": contract_id}
        
    except Exception as e:
        logger.error(f"Error processing contract {contract_id}: {str(e)}")
        
        # Update status to failed
        asyncio.run(update_contract_status(
            contract_id,
            ContractStatus.FAILED,
            error_message=str(e)
        ))
        
        raise

async def get_database():
    """Get database connection"""
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    db_name = os.getenv("DATABASE_NAME", "contract_parser")
    client = AsyncIOMotorClient(mongodb_url)
    return client[db_name]

async def get_file_content(contract_id: str) -> Optional[bytes]:
    """Get file content from database"""
    db = await get_database()
    file_doc = await db.files.find_one(
        {"contract_id": contract_id},
        {"content": 1, "_id": 0}
    )
    return file_doc["content"] if file_doc else None

async def update_contract_status(
    contract_id: str,
    status: ContractStatus,
    progress_percentage: int = 0,
    error_message: Optional[str] = None,
    extracted_data: Optional[Dict[str, Any]] = None,
    confidence_scores: Optional[Dict[str, Any]] = None,
    gap_analysis: Optional[Dict[str, Any]] = None
):
    """Update contract status in database"""
    db = await get_database()
    
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
    
    await db.contracts.update_one(
        {"contract_id": contract_id},
        {"$set": update_doc}
    )

def extract_pdf_text(file_content: bytes) -> str:
    """Extract text from PDF file"""
    import io
    
    text_content = ""
    try:
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content += page_text + "\n"
    except Exception as e:
        logger.error(f"Error extracting PDF text: {str(e)}")
        raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    return text_content