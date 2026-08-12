from fastapi import FastAPI

from app.database import Base, engine
from app.models.document import Document
from app.routers.documents import router as document_router
from app.services.minio_service import create_bucket

app = FastAPI(
    title="Document Ingestion Service",
    description="Training Project for Qentelli",
    version="1.0.0"
)
@app.on_event("startup")
def startup_event():
    create_bucket()

Base.metadata.create_all(bind=engine)

# Add this line
app.include_router(document_router)

@app.get("/")
def home():
    return {
        "message": "Welcome to Document Ingestion Service"
    }

@app.get("/health")
def health():
    return {
        "status": "ok"
    }