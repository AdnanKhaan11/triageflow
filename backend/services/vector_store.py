"""
backend/services/vector_store.py

A thin wrapper around ChromaDB: ingesting documents (chunked +
embedded) and querying them.
"""

from __future__ import annotations

import re
from typing import List, Dict, Any

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

from dotenv import load_dotenv

load_dotenv()


def clean_text(text: str) -> str:
    """Remove excess whitespace/newlines from extracted PDF text."""
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\n\s*\n", "\n\n", text)
    return text.strip()


class VectorStoreClient:
    """
    Wraps ChromaDB ingestion and querying behind a simple interface,
    so the rest of the project never talks to Chroma/LangChain
    directly.
    """

    def __init__(self, persist_directory: str = "./data/chroma_store") -> None:
        self.persist_directory = persist_directory

        self.embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

        # This is the SAME object we'll keep using for both ingestion
        # and querying -- there is only ever one vectorstore reference,
        # so nothing can silently point at an empty/stale collection.
        self.vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
        )

    def ingest_documents(self, file_paths: List[str]) -> None:
        """
        Load one or more PDF files, clean + chunk them, embed, and
        add them into the persistent collection. Each chunk keeps
        the source filename and page number as metadata.
        """
        all_chunks: List[Document] = []

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
        )

        for path in file_paths:
            loader = PyPDFLoader(path)
            pages = loader.load()  # one Document per PDF page, metadata pre-filled

            # Clean each page's text WITHOUT throwing away the Document
            # wrapper -- this is the fix for the earlier bug. We modify
            # page_content in place, metadata stays attached.
            for page in pages:
                page.page_content = clean_text(page.page_content)

            # split_documents expects real Document objects (with
            # metadata) -- which is exactly what we still have here.
            chunks = text_splitter.split_documents(pages)
            all_chunks.extend(chunks)

        # add_documents adds to the EXISTING self.vectorstore, rather
        # than creating a separate, disconnected store like before.
        self.vectorstore.add_documents(all_chunks)

    def query(self, text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Run a similarity search and return a list of plain dicts,
        each with the chunk text plus its source metadata.
        """
        results = self.vectorstore.similarity_search(text, k=top_k)

        return [
            {
                "text": doc.page_content,
                "source": doc.metadata.get("source", "unknown"),
                "page": doc.metadata.get("page", None),
            }
            for doc in results
        ]


# ---------------------------------------------------------------------
# Quick manual test -- run this file directly to sanity-check ingestion
# and retrieval before wiring it into retrieval_agent.py.
# ---------------------------------------------------------------------
if __name__ == "__main__":
    store = VectorStoreClient()

    store.ingest_documents(["./data/manuals/TriageFlow_Equipment_Manual.pdf"])

    results = store.query("pump vibration increasing", top_k=3)
    for r in results:
        print(r)
        print("---")

# whole workflow for ingesting a PDF and querying it:
#  A Document — LangChain's basic unit of text. It's not just a string — it's an object with two parts:
# python:
#     Document(page_content="the actual text here", metadata={"source": "file.pdf", "page": 3})

# PDF file
#    │
#    ▼ (PyPDFLoader)
# List[Document]  — one per page, metadata already has source+page
#    │
#    ▼ (RecursiveCharacterTextSplitter.split_documents)
# List[Document]  — smaller chunks, metadata copied onto each one
#    │
#    ▼ (Chroma.from_documents — embeds AND stores in one call)
# ChromaDB collection on disk
#    │
#    ▼ (later: vectorstore.similarity_search(query, k=5))
# List[Document]  — the most relevant chunks, with their metadata intact
