from sentence_transformers import util
from utils.pdf_processor import PDFProcessor
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
                "content": f"""
                    INSTRUCTIONS:
                    1. Base your answer STRICTLY on this document: "{best_doc.page_content}"
                    2. Respond in the SAME LANGUAGE as the question: '{query}'
                    3. If the document doesn't contain relevant information, say: "I cannot answer as this information is not in the provided document."
                    
                    QUESTION: {query}
                    
                    IMPORTANT:
                    - Prioritize direct quotes from the document when possible
                    - Keep answers concise yet complete
                    - Do not extrapolate or add information not in the document
                """
            }],
            model="llama3-70b-8192"
        )
                
        return {
            "answer": completion.choices[0].message.content,
            "source": best_doc.metadata,
            "score": float(best_score[0][0])
        }