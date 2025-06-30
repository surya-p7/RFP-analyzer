from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import tempfile
import os
import logging
from typing import List, Dict, Any
import ollama
from pathlib import Path

from document_processor import DocumentProcessor
from vector_store import VectorStore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="RFP Analyzer")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
doc_processor = DocumentProcessor()
vector_store = VectorStore()

# Summary questions
SUMMARY_QUESTIONS = [
    ("Project Objectives", "What are the main objectives of the proposed project?"),
    ("Project Background and Purpose", "What is the background and purpose of this RFP?"),
    ("Issuer and Key Team Members", "Who issued the RFP, and who are the key team members mentioned?"),
    ("Critical Dates", "What are the important submission deadlines or event dates mentioned?"),
    ("Financial Details", "What financial details are provided (e.g., budget, payment terms, contract duration)?"),
    ("Extracted Financial Items", "Are there details about earnest money deposit, bid value, or payment terms?"),
    ("Technical Specifications", "What technical specifications or architecture plans are included?"),
    ("Bill of Materials", "Is there a Bill of Materials (BOM) and what are the components?"),
    ("Scope of Work", "What are the bidder responsibilities or scope of work?"),
    ("Evaluation Criteria", "What are the criteria for evaluating proposals?"),
    ("Consortium Participation Rules", "What rules are outlined regarding consortium participation?"),
    ("Project Location and Logistics", "Where is the project located, and what logistics are mentioned?"),
    ("Presentation and PoC", "What are the service standards or PoC requirements?"),
    ("Service Level Agreements", "What are the expected SLAs or KPIs mentioned?"),
    ("Payment Terms", "What is the payment schedule or invoicing procedure?"),
    ("Key Challenges and Risks", "What challenges and risk mitigation strategies are listed?"),
    ("Dependencies & Assumptions", "What dependencies or assumptions are noted?"),
    ("Key Differentiators", "What value additions or unique differentiators are required?")
]

class Query(BaseModel):
    question: str

def validate_pdf_file(file: UploadFile) -> None:
    """Validate that the uploaded file is a PDF."""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )
    
    # Check file size (limit to 10MB)
    file_size = 0
    for chunk in file.file:
        file_size += len(chunk)
        if file_size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=400,
                detail="File size exceeds 10MB limit"
            )
    file.file.seek(0)  # Reset file pointer

@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...)):
    """Process and index an RFP document."""
    try:
        logger.info(f"Processing document: {file.filename}")
        
        # Validate file
        validate_pdf_file(file)
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        try:
            # Process document
            text = doc_processor.extract_text_from_pdf(tmp_path)
            if not text.strip():
                raise HTTPException(
                    status_code=400,
                    detail="Could not extract text from the PDF. The document might be corrupted or empty."
                )
            
            text = doc_processor.remove_boilerplate(text)
            
            # Extract and store abbreviations
            abbreviations = doc_processor.extract_abbreviations(text)
            vector_store.set_abbreviations(abbreviations)
            logger.info(f"Extracted {len(abbreviations)} abbreviations")
            
            # Chunk and index document
            chunks = doc_processor.chunk_document(text)
            vector_store.add_documents(chunks)
            logger.info(f"Indexed {len(chunks)} document chunks")
            
            return {
                "message": "Document processed successfully",
                "stats": {
                    "abbreviations_found": len(abbreviations),
                    "chunks_indexed": len(chunks)
                }
            }
        finally:
            # Cleanup
            try:
                os.unlink(tmp_path)
            except Exception as e:
                logger.warning(f"Failed to delete temporary file: {e}")
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query_document(query: Query):
    """Query the RFP document."""
    try:
        logger.info(f"Processing query: {query.question}")
        
        # Search for relevant chunks
        results = vector_store.search(query.question)
        if not results:
            return {"answer": "No relevant information found in the document."}
        
        # Prepare context
        context = "\n\n".join([r['text'] for r in results])
        context = vector_store.expand_abbreviations(context)
        
        # Generate response using Granite
        prompt = f"""You are a highly accurate AI analyst designed to extract answers from government RFP (Request for Proposal) documents. Use only the information provided in the context below to answer the user's question. You must avoid assumptions and always interpret the document logically, even when the language is indirect or synonymous.

### Strict Instructions:
- ✅ Use **ONLY** the provided context — no external knowledge or hallucinations.
- ✅ If the answer is **not available**, reply with: **"Not mentioned in the provided context."**
- ✅ Interpret **abbreviations intelligently**: if an acronym is asked, look throughout the document (including full forms) to resolve it.
- ✅ Understand **semantically equivalent phrases**, like:
  - "floated by", "published by", "invited by" = **issued by**
  - "money to be paid" = **Earnest Money Deposit**
- ✅ Search for **true intent** of the question.
- ✅ Prefer **concise**, factual answers.

### Context:
{context}

### User Question:
{query.question}

### Answer:"""

        response = ollama.generate(model='granite3.2:8b', prompt=prompt)
        return {"answer": response['response']}
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/summary")
async def get_summary():
    """Generate a comprehensive summary of the RFP."""
    try:
        logger.info("Generating document summary")
        summary = {}
        for section, question in SUMMARY_QUESTIONS:
            results = vector_store.search(question)
            if not results:
                summary[section] = "Not mentioned in the provided context."
                continue
                
            context = "\n\n".join([r['text'] for r in results])
            context = vector_store.expand_abbreviations(context)
            
            prompt = f"""You are a highly accurate AI analyst. Answer the following question based ONLY on the provided context. If the information is not available, respond with "Not mentioned in the provided context."

Context:
{context}

Question: {question}

Answer:"""
            
            response = ollama.generate(model='granite3.2:8b', prompt=prompt)
            summary[section] = response['response']
        
        return summary
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info("Starting RFP Analyzer server")
    logger.info("Server will be available at: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000) 