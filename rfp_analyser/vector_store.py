from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import ollama
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        # Ensure the persistence directory exists
        persist_dir = Path(".chroma_db")
        persist_dir.mkdir(exist_ok=True)
        
        try:
            # Initialize ChromaDB with the new configuration
            self.client = chromadb.PersistentClient(path=str(persist_dir))
            self.collection = self.client.get_or_create_collection(
                name="rfp_documents",
                metadata={"hnsw:space": "cosine"}  # Use cosine similarity
            )
            logger.info("Successfully initialized ChromaDB client and collection")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise

        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Successfully loaded embedding model")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise

        self.abbreviations: Dict[str, str] = {}

    def add_documents(self, chunks: List[tuple], metadata: Dict[str, Any] = None):
        """Add document chunks to the vector store."""
        if not chunks:
            logger.warning("No chunks provided to add_documents")
            return

        try:
            texts = [chunk[0] for chunk in chunks]
            metadatas = [chunk[1] for chunk in chunks]
            
            # Generate embeddings using sentence-transformers
            logger.info(f"Generating embeddings for {len(texts)} chunks")
            embeddings = self.embedding_model.encode(texts).tolist()

            # Add to ChromaDB
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=[f"doc_{i}" for i in range(len(texts))]
            )
            logger.info(f"Successfully added {len(texts)} chunks to vector store")
        except Exception as e:
            logger.error(f"Failed to add documents to vector store: {e}")
            raise

    def search(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """Search for relevant chunks using semantic similarity."""
        if not query.strip():
            logger.warning("Empty query provided to search")
            return []

        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()

            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k
            )

            # Process results
            processed_results = []
            for i in range(len(results['documents'][0])):
                processed_results.append({
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i]
                })

            logger.info(f"Found {len(processed_results)} results for query: {query[:50]}...")
            return processed_results
        except Exception as e:
            logger.error(f"Failed to search vector store: {e}")
            raise

    def expand_abbreviations(self, text: str) -> str:
        """Expand known abbreviations in the text."""
        if not text:
            return text

        try:
            expanded_text = text
            for abbr, full_form in self.abbreviations.items():
                expanded_text = expanded_text.replace(abbr, f"{abbr} ({full_form})")
            return expanded_text
        except Exception as e:
            logger.error(f"Failed to expand abbreviations: {e}")
            return text

    def set_abbreviations(self, abbreviations: Dict[str, str]):
        """Set the abbreviation mappings."""
        self.abbreviations = abbreviations
        logger.info(f"Set {len(abbreviations)} abbreviation mappings")

    def clear(self):
        """Clear all documents from the vector store."""
        try:
            self.collection.delete(where={})
            logger.info("Cleared all documents from vector store")
        except Exception as e:
            logger.error(f"Failed to clear vector store: {e}")
            raise 