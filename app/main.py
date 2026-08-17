from fastapi import FastAPI

app = FastAPI(
    title="Document Ingestion Service",
    description="Training Project for Qentelli",
    version="1.0.0"
)


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