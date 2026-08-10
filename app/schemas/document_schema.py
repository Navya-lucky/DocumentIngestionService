from pydantic import BaseModel


class DocumentUpdate(BaseModel):
    filename: str
    status: str