from utils.pdf_processor import PDFProcessor

class DocumentService:
    @staticmethod
    def process_pdf(pdf_path: str):
        return PDFProcessor.process(pdf_path)