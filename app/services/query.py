import os
from typing import List, Dict
import numpy as np
from sentence_transformers import util
from services.pdf_processor import PDFProcessor
from core.database import DatabaseManager, QueryCache, Document
from groq import Groq

class QueryService:
    def __init__(self):
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.pdf_processor = PDFProcessor()
        self.db_manager = DatabaseManager()

    def _get_cached_response(self, query: str, pdf_hash: str) -> Dict:
        query_hash = self.db_manager.generate_hash(query + pdf_hash)
        session = self.db_manager.get_session()
        try:
            cached = session.query(QueryCache).filter_by(query_hash=query_hash).first()
            return cached.response if cached else None
        finally:
            session.close()

    def _cache_response(self, query: str, pdf_hash: str, response: Dict):
        query_hash = self.db_manager.generate_hash(query + pdf_hash)
        session = self.db_manager.get_session()
        try:
            new_cache = QueryCache(
                query_hash=query_hash,
                pdf_hash=pdf_hash,
                response=response,
            )
            session.add(new_cache)
            session.commit()
        finally:
            session.close()

    def _get_relevant_chunks(self, collection, query: str, n_results: int = 3) -> List[Dict]:
        query_embedding = self.pdf_processor.embedding_function([query])
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        relevant_chunks = []
        for doc, score, metadata in zip(results['documents'][0], 
                                      results['distances'][0], 
                                      results['metadatas'][0]):
            relevant_chunks.append({
                'content': doc,
                'score': float(score),
                'metadata': metadata
            })
        
        return relevant_chunks

    def _generate_context_prompt(self, query: str, chunks: List[Dict]) -> str:
        context = "\n\n".join([f"DOCUMENT EXCERPT {i+1}:\n{chunk['content']}" 
                             for i, chunk in enumerate(chunks)])
        
        return f"""
        INSTRUCTIONS:
        1. Analyze the following document excerpts and answer the question based on the provided information.
        2. Combine information from different excerpts when necessary.
        3. Respond in the same language as the question: '{query}'
        4. If no excerpt contains relevant information, respond: "I cannot answer based on the provided document."

        CONTEXT:
        {context}

        QUESTION: {query}
        """

    def execute_query(self, pdf_path: str, query: str) -> Dict:
        try:
            abs_path = os.path.abspath(pdf_path)
            if not os.path.exists(abs_path):
                raise ValueError(f"PDF file not found: {abs_path}")

            _, full_hash = self.pdf_processor.process(abs_path)
            collection_name = self.pdf_processor._sanitize_collection_name(full_hash)

            cached_response = self._get_cached_response(query, full_hash)
            if cached_response:
                return cached_response

            collection = self.pdf_processor.chroma_client.get_collection(collection_name)
            relevant_chunks = self._get_relevant_chunks(collection, query, n_results=3)

            if not relevant_chunks:
                raise ValueError("No relevant documents found")

            prompt = self._generate_context_prompt(query, relevant_chunks)
            
            completion = self.client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                model="llama3-70b-8192",
                temperature=0.3
            )

            response = {
                "answer": completion.choices[0].message.content,
                "sources": [chunk['metadata'] for chunk in relevant_chunks],
                "scores": [chunk['score'] for chunk in relevant_chunks]
            }

            self._cache_response(query, full_hash, response)
            return response

        except Exception as e:
            raise ValueError(f"Error processing query: {str(e)}")