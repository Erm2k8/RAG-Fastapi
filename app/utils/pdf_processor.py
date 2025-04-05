from typing import List
import re
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

class PDFProcessor:
    _embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    _text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )

    @staticmethod
    def _clean_text(text: str) -> str:
        patterns = [
            r'^\d+\s+\|\s+.+$',
            r'^Capítulo\s+\d+', 
            r'^.*Confidencial.*$',
            r'^\d{1,2}/\d{1,2}/\d{4}',
            r'^Página\s+\d+'
        ]
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            line = re.sub(r'\s\d{1,3}\s*$', '', line.strip())
            if line and not any(re.match(p, line) for p in patterns):
                cleaned_lines.append(line)
        return '\n'.join(cleaned_lines)

    @staticmethod
    def process(pdf_path: str) -> FAISS:
        documents = []
        for page in PyPDFLoader(pdf_path).load_and_split():
            cleaned_text = PDFProcessor._clean_text(page.page_content)
            if len(cleaned_text) > 50:
                new_doc = page.model_copy()
                new_doc.page_content = cleaned_text
                documents.append(new_doc)
        
        chunks = PDFProcessor._text_splitter.split_documents(documents)
        vectorstore = FAISS.from_documents(chunks, PDFProcessor._embeddings)
        vectorstore.documents = chunks
        vectorstore.embedding_dimension = len(PDFProcessor._embeddings.embed_query("test"))
        return vectorstore