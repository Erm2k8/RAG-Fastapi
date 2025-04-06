from pydantic import BaseModel
from typing import List

class QueryRequest(BaseModel):
    query: str
    pdf_path: str

class ResponseModel(BaseModel):
    answer: str
    sources: List[dict]
    scores: List[float]