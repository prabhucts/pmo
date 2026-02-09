"""
File upload API endpoints
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import shutil

from app.db.database import get_db
from app.core.config import settings
from app.schemas.schemas import FileUploadResponse
from app.services.data_processor import DataProcessor

router = APIRouter()


@router.post("/user-stories", response_model=FileUploadResponse)
async def upload_user_stories(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload user stories CSV from Rally"""
    return await _process_upload(file, "user_stories", db)


@router.post("/features", response_model=FileUploadResponse)
async def upload_features(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload features CSV from Rally"""
    return await _process_upload(file, "features", db)


@router.post("/epics", response_model=FileUploadResponse)
async def upload_epics(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload epics CSV from Rally"""
    return await _process_upload(file, "epics", db)


@router.post("/clarity-timesheet", response_model=FileUploadResponse)
async def upload_clarity_timesheet(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload Clarity timesheet CSV"""
    return await _process_upload(file, "clarity_timesheet", db)


async def _process_upload(file: UploadFile, file_type: str, db: Session) -> FileUploadResponse:
    """Process uploaded file"""
    
    # Validate file extension
    if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")
    
    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
        )
    
    # Save file temporarily
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process file
        processor = DataProcessor(db)
        
        if file_type == "user_stories":
            result = processor.process_user_stories(file_path)
        elif file_type == "features":
            result = processor.process_features(file_path)
        elif file_type == "epics":
            result = processor.process_epics(file_path)
        elif file_type == "clarity_timesheet":
            result = processor.process_clarity_timesheet(file_path)
        else:
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Processing failed"))
        
        return FileUploadResponse(
            filename=file.filename,
            file_type=file_type,
            rows_processed=result.get("rows_processed", 0),
            status="success",
            message=f"Successfully processed {result.get('rows_processed', 0)} rows"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up temporary file
        if os.path.exists(file_path):
            os.remove(file_path)
