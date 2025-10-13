from fastapi import APIRouter, Depends, UploadFile, File
from ..auth import get_current_user
from ..models import User, SourceDocument
from ..services import DocumentService

router = APIRouter()


@router.post("/upload", response_model=SourceDocument)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(),
):
    return await document_service.create_upload_document(file=file, current_user=current_user)