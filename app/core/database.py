from sqlalchemy import create_engine, Column, Integer, String, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import hashlib
import os

from .config import DOCUMENTS_DATABASE_URL

os.makedirs("./data/documents", exist_ok=True)

Base = declarative_base()

class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    file_path = Column(String, unique=True)
    file_hash = Column(String, index=True)  
    chunks = Column(JSON) 
    
class QueryCache(Base):
    __tablename__ = 'query_cache'
    id = Column(Integer, primary_key=True)
    query_hash = Column(String, unique=True, index=True)
    pdf_hash = Column(String, index=True)  
    response = Column(JSON)

class DatabaseManager:
    def __init__(self, db_url=DOCUMENTS_DATABASE_URL):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.Session()
    
    @staticmethod
    def generate_hash(content: str) -> str:
        return hashlib.sha256(content.encode()).hexdigest()
    
    def document_exists(self, file_hash: str) -> bool:
        session = self.get_session()
        try:
            return session.query(Document).filter_by(file_hash=file_hash).first() is not None
        finally:
            session.close()