from fastapi import APIRouter, HTTPException, UploadFile, File, Query, Depends
from fastapi.responses import StreamingResponse
from app.models import (
    ContractUploadResponse, 
    ContractStatusResponse, 
    ContractResponse,
    ContractListResponse,
    ContractStatus
)
from app.database import get_database
from app.services.contract_service import ContractService
from typing import Optional
import io

router = APIRouter()

def get_contract_service():
    return ContractService(get_database())

@router.post("/upload", response_model=ContractUploadResponse)
async def upload_contract(
    file: UploadFile = File(...),
    service: ContractService = Depends(get_contract_service)
):
    """Upload a contract file for processing"""
    # Validate file type
    if not file.content_type == "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )
    
    # Validate file size (50MB limit)
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    if file_size > 50 * 1024 * 1024:  # 50MB
        raise HTTPException(
            status_code=400,
            detail="File size exceeds 50MB limit"
        )
    
    # Reset file pointer
    await file.seek(0)
    
    try:
        contract_id = await service.upload_contract(file, file_size)
        return ContractUploadResponse(
            contract_id=contract_id,
            message="Contract uploaded successfully. Processing started.",
            status=ContractStatus.PENDING
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{contract_id}/status", response_model=ContractStatusResponse)
async def get_contract_status(
    contract_id: str,
    service: ContractService = Depends(get_contract_service)
):
    """Get contract processing status"""
    try:
        status_info = await service.get_contract_status(contract_id)
        if not status_info:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        return ContractStatusResponse(
            contract_id=contract_id,
            status=status_info["status"],
            progress_percentage=status_info.get("progress_percentage", 0),
            error_message=status_info.get("error_message")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract_data(
    contract_id: str,
    service: ContractService = Depends(get_contract_service)
):
    """Get contract data (only available when processing is complete)"""
    try:
        contract_data = await service.get_contract_data(contract_id)
        if not contract_data:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        if contract_data["status"] != ContractStatus.COMPLETED:
            raise HTTPException(
                status_code=400, 
                detail=f"Contract data not available. Status: {contract_data['status']}"
            )
        
        return ContractResponse(**contract_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=ContractListResponse)
async def list_contracts(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[ContractStatus] = None,
    service: ContractService = Depends(get_contract_service)
):
    """Get paginated list of contracts with optional filtering"""
    try:
        contracts_data = await service.list_contracts(
            page=page,
            page_size=page_size,
            status=status
        )
        return ContractListResponse(**contracts_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{contract_id}/download")
async def download_contract(
    contract_id: str,
    service: ContractService = Depends(get_contract_service)
):
    """Download original contract file"""
    try:
        file_data = await service.download_contract(contract_id)
        if not file_data:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        file_content, filename = file_data
        
        return StreamingResponse(
            io.BytesIO(file_content),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))