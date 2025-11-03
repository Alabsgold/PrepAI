from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from ..auth import get_current_user
from ..models import User
from ..services import DocumentService
from ..schemas import DocumentRead, QuizRead

router = APIRouter()


@router.post("/upload", response_model=DocumentRead)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(),
):
    return await document_service.create_upload_document(file=file, current_user=current_user)


@router.get("/", response_model=List[DocumentRead])
def get_documents(
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(),
):
    return document_service.get_all_documents_for_user(user_id=current_user.id)


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(),
):
    document = document_service.get_document_by_id(document_id=document_id, user_id=current_user.id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


@router.get("/{document_id}/quiz", response_model=QuizRead)
def get_quiz(
    document_id: int,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(),
):
    quiz = document_service.get_quiz_for_document(document_id=document_id, user_id=current_user.id)
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found for this document")
    return quiz


@router.delete("/{document_id}", status_code=status.HTTP_200_OK)
def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(),
):
    success = document_service.delete_document_by_id(document_id=document_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return {"message": "Document deleted successfully"}