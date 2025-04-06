import os
import hashlib
from typing import List, Tuple
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import chromadb
from chromadb.utils import embedding_functions
from core.database import Document, DatabaseManager

class PDFProcessor:
    def __init__(self):
        os.makedirs("./data/vectors", exist_ok=True)
        
        self.chroma_client = chromadb.PersistentClient(path="./data/vectors/")
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="paraphrase-multilingual-mpnet-base-v2"
        )
        self.db_manager = DatabaseManager()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=300,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len
        )

    def _get_file_hash(self, file_path: str) -> str:
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()

    def _sanitize_collection_name(self, file_hash: str) -> str:
        return f"doc_{file_hash[:16]}"

    def process(self, pdf_path: str) -> Tuple[List, str]:
        abs_path = os.path.abspath(pdf_path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {abs_path}")

        file_hash = self._get_file_hash(abs_path)
        collection_name = self._sanitize_collection_name(file_hash)

        session = self.db_manager.get_session()
        try:
            existing_doc = session.query(Document).filter_by(file_hash=file_hash).first()
            
            if existing_doc:
                try:
                    col = self.chroma_client.get_collection(collection_name)
                    if col.count() == len(existing_doc.chunks):
                        return existing_doc.chunks, file_hash 
                except:
                    pass

            loader = PyPDFLoader(abs_path)
            pages = loader.load_and_split()
            
            chunks = self.text_splitter.split_documents(pages)
            chunk_data = [{
                "page_content": chunk.page_content,
                "metadata": {**chunk.metadata, "source": abs_path}
            } for chunk in chunks]

            collection = self.chroma_client.get_or_create_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )

            existing_ids = collection.get()['ids']
            if existing_ids:
                collection.delete(ids=existing_ids)

            collection.add(
                documents=[chunk['page_content'] for chunk in chunk_data],
                ids=[f"id_{i}" for i in range(len(chunk_data))],
                metadatas=[chunk['metadata'] for chunk in chunk_data]
            )

            doc_data = {
                "file_path": abs_path,
                "file_hash": file_hash,
                "chunks": chunk_data
            }

            if existing_doc:
                for key, value in doc_data.items():
                    setattr(existing_doc, key, value)
            else:
                session.add(Document(**doc_data))
            
            session.commit()
            return chunk_data, file_hash

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()