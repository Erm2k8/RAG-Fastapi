from sentence_transformers import util
from utils.pdf_processor import PDFProcessor
from core.database import DatabaseManager, QueryCache, Document
from groq import Groq
import os

class QueryService:
    def __init__(self):
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.pdf_processor = PDFProcessor()
        self.db_manager = DatabaseManager()

    def _get_cached_response(self, query: str, pdf_hash: str):
        query_hash = self.db_manager.generate_hash(query + pdf_hash)
        session = self.db_manager.get_session()
        try:
            cached = session.query(QueryCache).filter_by(query_hash=query_hash).first()
            return cached.response if cached else None
        finally:
            session.close()

    def _cache_response(self, query: str, pdf_hash: str, response: dict):
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

    def execute_query(self, pdf_path: str, query: str):
        try:
            abs_path = os.path.abspath(pdf_path)
            if not os.path.exists(abs_path):
                raise ValueError(f"Arquivo PDF não encontrado: {abs_path}")

            chunks, full_hash = self.pdf_processor.process(abs_path)
            collection_name = self.pdf_processor._sanitize_collection_name(full_hash)

            cached_response = self._get_cached_response(query, full_hash)
            if cached_response:
                return cached_response

            collection = self.pdf_processor.chroma_client.get_collection(collection_name)
            query_embedding = self.pdf_processor.embedding_function([query])
            results = collection.query(
                query_embeddings=query_embedding,
                n_results=1
            )

            if not results['documents']:
                raise ValueError("Nenhum documento relevante encontrado")

            best_doc_content = results['documents'][0][0]
            best_score = results['distances'][0][0]

            session = self.db_manager.get_session()
            try:
                doc_record = session.query(Document).filter_by(file_hash=full_hash).first()
                if not doc_record:
                    raise ValueError("Documento não encontrado no banco de dados")

                best_chunk = next(
                    (chunk for chunk in doc_record.chunks 
                    if chunk['page_content'] == best_doc_content),
                    None
                )

                if not best_chunk:
                    raise ValueError("Chunk do documento não encontrado")

                completion = self.client.chat.completions.create(
                    messages=[{
                        "role": "user",
                        "content": f"""
                            INSTRUÇÕES:
                            1. Baseie sua resposta STRITAMENTE neste documento: "{best_doc_content}"
                            2. Responda no MESMO IDIOMA da pergunta: '{query}'
                            3. Se o documento não contiver informações relevantes, diga: "Não posso responder pois esta informação não está no documento fornecido."
                            
                            PERGUNTA: {query}
                        """
                    }],
                    model="llama3-70b-8192"
                )

                response = {
                    "answer": completion.choices[0].message.content,
                    "source": best_chunk['metadata'],
                    "score": float(best_score)
                }

                self._cache_response(query, full_hash, response)
                return response

            finally:
                session.close()

        except Exception as e:
            raise ValueError(f"Erro no processamento da query: {str(e)}")