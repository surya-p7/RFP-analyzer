import re
from typing import Dict, List, Tuple
from pdfminer.high_level import extract_text
# import pytesseract
# from PIL import Image
# import io
import fitz  # PyMuPDF
import os
# import subprocess

class DocumentProcessor:
    def __init__(self):
        self.abbreviation_pattern = re.compile(r'([A-Z]{2,})\s*\(([^)]+)\)')
        self.abbreviations: Dict[str, str] = {}
        
        # # Try to find Tesseract path
        # try:
        #     # Try to get path from system
        #     result = subprocess.run(['where', 'tesseract'], capture_output=True, text=True)
        #     if result.returncode == 0:
        #         tesseract_path = result.stdout.strip().split('\n')[0]
        #         pytesseract.pytesseract.tesseract_cmd = tesseract_path
        #         print(f"Found Tesseract at: {tesseract_path}")
        #     else:
        #         # Fallback to common installation paths
        #         common_paths = [
        #             r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        #             r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        #             os.path.expanduser('~') + r'\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
        #         ]
        #         
        #         for path in common_paths:
        #             if os.path.exists(path):
        #                 pytesseract.pytesseract.tesseract_cmd = path
        #                 print(f"Found Tesseract at: {path}")
        #                 break
        #         else:
        #             print("Warning: Tesseract not found. OCR may not work properly.")
        # except Exception as e:
        #     print(f"Error finding Tesseract: {e}")
        #     print("Warning: Tesseract not found. OCR may not work properly.")

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using PDFMiner."""
        try:
            text = extract_text(pdf_path)
            if not text.strip():
                print("Warning: No text extracted from PDF. The document might be scanned or image-based.")
            return text
        except Exception as e:
            print(f"Error extracting text: {e}")
            return ""

    # def _extract_text_with_ocr(self, pdf_path: str) -> str:
    #     """Extract text using Tesseract OCR."""
    #     try:
    #         doc = fitz.open(pdf_path)
    #         text = []
    #         
    #         for page in doc:
    #             # Convert page to image
    #             pix = page.get_pixmap()
    #             img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    #             
    #             # Extract text from image
    #             page_text = pytesseract.image_to_string(img)
    #             text.append(page_text)
    #         
    #         return " ".join(text)
    #     except Exception as e:
    #         print(f"Error during OCR: {e}")
    #         return ""

    def remove_boilerplate(self, text: str) -> str:
        """Remove headers, footers, and page numbers."""
        # Remove page numbers
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
        # Remove common headers/footers
        text = re.sub(r'(Page|Page No\.|Page Number)\s*\d+', '', text)
        return text

    def extract_abbreviations(self, text: str) -> Dict[str, str]:
        """Extract and store abbreviation mappings."""
        matches = self.abbreviation_pattern.finditer(text)
        for match in matches:
            abbr, full_form = match.groups()
            self.abbreviations[abbr] = full_form
        return self.abbreviations

    def chunk_document(self, text: str, chunk_size: int = 1000, overlap: int = 150) -> List[Tuple[str, Dict]]:
        """Split document into chunks with metadata."""
        # First try section-wise chunking
        sections = self._split_by_sections(text)
        if sections:
            return sections

        # Fallback to fixed-size chunks
        chunks = []
        words = text.split()
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append((chunk, {
                'chunk_id': len(chunks),
                'start_word': i,
                'end_word': min(i + chunk_size, len(words))
            }))
        return chunks

    def _split_by_sections(self, text: str) -> List[Tuple[str, Dict]]:
        """Split document by common section headings."""
        section_patterns = [
            r'Scope of Work',
            r'Technical Requirements',
            r'Project Objectives',
            r'Evaluation Criteria',
            r'Terms and Conditions'
        ]
        
        sections = []
        current_pos = 0
        
        for pattern in section_patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            for i, match in enumerate(matches):
                start = match.start()
                if i < len(matches) - 1:
                    end = matches[i + 1].start()
                else:
                    end = len(text)
                
                section_text = text[start:end].strip()
                sections.append((section_text, {
                    'section_name': match.group(),
                    'start_pos': start,
                    'end_pos': end
                }))
        
        return sections if sections else [] 