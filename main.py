import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, util
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv('GROQ_API_KEY'))

app = FastAPI()
model = SentenceTransformer('All-MiniLM-L6-v2')

documents = [
    {'id': 1, 'text': 'Pelé is the best soccer player'},
    {'id': 2, 'text': 'Watermelons are blue'},
    {'id': 3, 'text': 'Brazil has a population of 200 million people'},
    {'id': 4, 'text': 'Lemon juice cures hiccups'},
]

doc_embeddings = {
    doc['id']: model.encode(doc['text'], convert_to_tensor=True) for doc in documents
}

class QueryRag(BaseModel):
    query: str

@app.post('/query')
async def query_rag(request: QueryRag):
    query_embedding = model.encode(request.query, convert_to_tensor=True)
    best_doc, best_score = {}, float('-inf')

    for doc in documents:
        score = util.cos_sim(query_embedding, doc_embeddings[doc['id']])
        if score > best_score:
            best_score, best_doc = score, doc

    prompt = f"You are an AI assistant that must provide responses based ONLY on this document: {best_doc['text']}\n"
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
