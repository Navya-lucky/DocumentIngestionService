from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
import os
import shutil
import uuid

from app.database import get_db
from app.models.document import Document
from app.services.extraction_service import extract_text
from app.schemas.document_schema import DocumentUpdate

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

STORAGE_PATH = "storage"


# -------------------------------
# Upload Document
# -------------------------------

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    document_id = str(uuid.uuid4())

    folder_path = os.path.join(STORAGE_PATH, document_id)
    os.makedirs(folder_path, exist_ok=True)

    file_path = os.path.join(folder_path, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_document = Document(
        filename=file.filename,
        content_type=file.content_type,
        extracted_text="",
        status="Uploaded"
    )

    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    try:
        extracted = extract_text(file_path)
        new_document.extracted_text = extracted
        new_document.status = "Processed"

    except Exception as e:
        new_document.status = "Failed"
        new_document.extracted_text = str(e)

    db.commit()

    return {
        "id": new_document.id,
        "filename": new_document.filename,
        "status": new_document.status,
        "saved_path": file_path
    }


# -------------------------------
# Get All Documents
# -------------------------------

@router.get("/")
def get_documents(db: Session = Depends(get_db)):
    documents = db.query(Document).all()
    return documents


# -------------------------------
# Search Documents
# -------------------------------

@router.get("/search/")
def search_documents(
    q: str,
    db: Session = Depends(get_db)
):
    documents = (
        db.query(Document)
        .filter(
            or_(
                Document.filename.ilike(f"%{q}%"),
                Document.extracted_text.ilike(f"%{q}%")
            )
        )
        .all()
    )

    return documents


# -------------------------------
# Get Document By ID
# -------------------------------

@router.get("/{document_id}")
def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return document


# -------------------------------
# Update Document
# -------------------------------

@router.put("/{document_id}")
def update_document(
    document_id: int,
    data: DocumentUpdate,
    db: Session = Depends(get_db)
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    document.filename = data.filename
    document.status = data.status

    db.commit()
    db.refresh(document)

    return document


# -------------------------------
# Delete Document
# -------------------------------

@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    db.delete(document)
    db.commit()

    return {
        "message": "Document deleted successfully"
    }