import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq
from embedding import PDFProcessor
from sentence_transformers import util

app = FastAPI()
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

class QueryRequest(BaseModel):
    query: str
    pdf_path: str

class ResponseModel(BaseModel):
    answer: str
    source: dict
    score: float

@app.post('/query', response_model=ResponseModel)
async def handle_query(request: QueryRequest):
    try:
        vectorstore = PDFProcessor.process(request.pdf_path)
        query_embed = PDFProcessor._embeddings.embed_query(request.query)
        
        best_score = -1
        best_doc = None
        for doc in vectorstore.documents:
            doc_embed = PDFProcessor._embeddings.embed_query(doc.page_content)
            score = util.cos_sim(query_embed, doc_embed)
            if score > best_score:
                best_score = score
                best_doc = doc
        
        if not best_doc:
            raise HTTPException(status_code=404, detail="No relevant document found")
        
        completion = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": f"Document: {best_doc.page_content}\n\nQuestion: {request.query}"
            }],
            model="llama3-70b-8192"
        )
        
        return ResponseModel(
            answer=completion.choices[0].message.content,
            source=best_doc.metadata,
            score=float(best_score[0][0])
        )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
