from sentence_transformers import util
from core.processors import PDFProcessor
from groq import Groq
import os

class QueryService:
    def __init__(self):
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
    
    def execute_query(self, pdf_path: str, query: str):
        vectorstore = PDFProcessor.process(pdf_path)
        query_embed = PDFProcessor._embeddings.embed_query(query)
        
        best_doc, best_score = None, -1
        for doc in vectorstore.documents:
            doc_embed = PDFProcessor._embeddings.embed_query(doc.page_content)
            score = util.cos_sim(query_embed, doc_embed)
            if score > best_score:
                best_doc, best_score = doc, score
        
        if not best_doc:
            raise ValueError("No relevant document found")
        
        completion = self.client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": f"Document: {best_doc.page_content}\n\nQuestion: {query}"
            }],
            model="llama3-70b-8192"
        )
        
        return {
            "answer": completion.choices[0].message.content,
            "source": best_doc.metadata,
            "score": float(best_score[0][0])
        }