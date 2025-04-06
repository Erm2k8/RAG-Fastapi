from services.query import QueryService
from services.pdf import PDFService
from core.database import DatabaseManager

def get_query_service():
    return QueryService()

def get_db_manager():
    return DatabaseManager()

def get_pdf_processor():
    return PDFService()