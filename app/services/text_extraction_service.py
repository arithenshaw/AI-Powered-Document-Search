"""
Text extraction service for PDF, DOCX, and TXT files
"""

from io import BytesIO
from typing import Optional

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


class TextExtractionService:
    """Service for extracting text from documents"""
    
    @staticmethod
    def extract_text(file_content: bytes, file_type: str) -> str:
        """
        Extract text from document based on file type
        
        Args:
            file_content: File content as bytes
            file_type: MIME type or file extension
            
        Returns:
            Extracted text
        """
        file_type_lower = file_type.lower()
        
        if "pdf" in file_type_lower:
            return TextExtractionService._extract_from_pdf(file_content)
        elif "wordprocessingml" in file_type_lower or "docx" in file_type_lower:
            return TextExtractionService._extract_from_docx(file_content)
        elif "text/plain" in file_type_lower or file_type_lower == "txt":
            return file_content.decode("utf-8")
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    @staticmethod
    def _extract_from_pdf(file_content: bytes) -> str:
        """Extract text from PDF file"""
        if not PDF_AVAILABLE:
            raise Exception("PyPDF2 not installed. Install with: pip install PyPDF2")
        
        pdf_file = BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    
    @staticmethod
    def _extract_from_docx(file_content: bytes) -> str:
        """Extract text from DOCX file"""
        if not DOCX_AVAILABLE:
            raise Exception("python-docx not installed. Install with: pip install python-docx")
        
        doc = Document(BytesIO(file_content))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()


text_extraction_service = TextExtractionService()

