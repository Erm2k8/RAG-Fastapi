from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str
    pdf_path: str

class ResponseModel(BaseModel):
    answer: str
    source: dict
    score: float