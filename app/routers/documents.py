from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pathlib import Path
import tempfile
import os
import uuid

from app.database import get_db
from app.models.document import Document
from app.services.extraction_service import extract_text
from app.services.minio_service import upload_file, delete_file
from app.schemas.document_schema import DocumentUpdate


router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


# =========================================================
# Upload Document
# =========================================================

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    document_id = str(uuid.uuid4())

    # Get only the filename
    filename = Path(file.filename or "uploaded_file").name

    # MinIO object path
    # Example:
    # 550e8400-e29b-41d4-a716-446655440000/FastAPI.pdf
    object_name = f"{document_id}/{filename}"

    # Temporary file used only for text extraction
    temp_file_path = None

    try:

        # =================================================
        # 1. Save uploaded file temporarily
        # =================================================

        suffix = Path(filename).suffix

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temp_file:

            temp_file_path = temp_file.name

            while True:

                chunk = await file.read(1024 * 1024)

                if not chunk:
                    break

                temp_file.write(chunk)

        # =================================================
        # 2. Extract text
        # =================================================

        extracted = extract_text(temp_file_path)

        # =================================================
        # 3. Upload original file to MinIO
        # =================================================

        upload_file(
            temp_file_path,
            object_name,
            file.content_type or "application/octet-stream"
        )

        # =================================================
        # 4. Save metadata in PostgreSQL
        # =================================================

        new_document = Document(
            filename=filename,
            content_type=file.content_type,
            extracted_text=extracted,
            status="Processed",
            file_path=object_name
        )

        db.add(new_document)
        db.commit()
        db.refresh(new_document)

        # =================================================
        # 5. Return response
        # =================================================

        return {
            "id": new_document.id,
            "filename": new_document.filename,
            "status": new_document.status,
            "saved_path": object_name
        }

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {str(e)}"
        )

    finally:

        # =================================================
        # 6. Delete temporary local file
        # =================================================

        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)


# =========================================================
# Get All Documents
# =========================================================

@router.get("/")
def get_documents(
    db: Session = Depends(get_db)
):

    documents = db.query(Document).all()

    return documents


# =========================================================
# Search Documents
# =========================================================

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


# =========================================================
# Get Document By ID
# =========================================================

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


'''
# =========================================================
# Update Document
# =========================================================

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
'''


# =========================================================
# Delete Document
# =========================================================

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

    try:

        # =================================================
        # 1. Delete file from MinIO
        # =================================================

        if document.file_path:
            delete_file(document.file_path)

        # =================================================
        # 2. Delete database record
        # =================================================

        db.delete(document)
        db.commit()

        return {
            "message": "Document and file deleted successfully"
        }

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Delete failed: {str(e)}"
        )