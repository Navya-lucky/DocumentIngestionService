from fastapi import FastAPI

from app.database import Base, engine
from app.models.document import Document
from app.routers.documents import router as document_router

app = FastAPI(
    title="Document Ingestion Service",
    description="Training Project for Qentelli",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

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