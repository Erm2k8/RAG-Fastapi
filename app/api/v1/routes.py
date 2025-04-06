from fastapi import APIRouter, HTTPException, File, UploadFile, Depends
from typing import List
import os
from services.query import QueryService
from .schemas import QueryRequest, ResponseModel
from .dependencies import get_query_service
from services.pdf import PDFService
from core.database import DatabaseManager, Document

router = APIRouter()

@router.get("/")
async def index():
    return {"message": "Hello, world!"}

@router.post("/query/", response_model=ResponseModel)
async def handle_query(
    request: QueryRequest,
    query_service: QueryService = Depends(get_query_service)
):
    try:
        file_path = os.path.join("data", "documents", request.pdf_path)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        return query_service.execute_query(
            pdf_path=file_path,
            query=request.query
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload/")
async def upload_file(files: list[UploadFile]):
    try:
        for file in files:
            os.makedirs("data/documents", exist_ok=True)
            file_path = os.path.join("data", "documents", file.filename)
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            processor = PDFService()
            processor.process(file_path)
        return {
            "filename": [file.filename for file in files],
            "saved_path": file_path,
            "status": "processed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/repair/")
async def repair_document(pdf_path: str):
    try:
        processor = PDFService()
        abs_path = os.path.join("data", "documents", pdf_path)
        if not os.path.exists(abs_path):
            raise HTTPException(status_code=404, detail="File not found")
        chunks, collection_name = processor.process(abs_path)
        return {
            "status": "repaired",
            "collection": collection_name,
            "chunks_processed": len(chunks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/")
async def list_documents():
    session = DatabaseManager().get_session()
    try:
        docs = session.query(Document).all()
        return {
            "documents": [
                {
                    "id": doc.id,
                    "filename": os.path.basename(doc.file_path),
                    "hash": doc.file_hash,
                    "chunks": len(doc.chunks) if doc.chunks else 0
                }
                for doc in docs
            ]
        }
    finally:
        session.close()