"""
CLI Document Ingestion Utility for Pinecone RAG.
Usage:
    python ingest_document.py path/to/document.pdf --title "Corporate VPN Setup Guide" --category "Network"
"""

import os
import sys
import argparse
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from config import Config
from services.knowledge_service import KnowledgeService
from ai.rag_pipeline import rag_pipeline


def main():
    parser = argparse.ArgumentParser(description="Ingest a technical PDF, DOCX, TXT, or CSV document into Pinecone.")
    parser.add_argument("file_path", help="Path to the document file (e.g. sample.pdf)")
    parser.add_argument("--title", help="Document Title (defaults to filename)")
    parser.add_argument("--category", default="General IT", help="Category (e.g. Network, Hardware, Software)")

    args = parser.parse_args()
    file_path = Path(args.file_path)

    if not file_path.exists():
        print(f"❌ Error: File not found at '{file_path}'")
        sys.exit(1)

    filename = file_path.name
    title = args.title or file_path.stem.replace("_", " ").title()

    print("=" * 60)
    print(f"📄 Ingesting: {filename}")
    print(f"📌 Title: {title}")
    print(f"🏷️  Category: {args.category}")
    print(f"🌲 Pinecone Index: {Config.PINECONE_INDEX_NAME}")
    print(f"🌐 Namespace: {Config.PINECONE_NAMESPACE}")
    print(f"🧠 Embedding Model: {Config.EMBEDDING_MODEL} (384 dimensions)")
    print("=" * 60)

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    mock_admin_user = {
        "id": "00000000-0000-0000-0000-000000000001",
        "email": "admin@enterprise.com",
        "role": "admin",
        "full_name": "Admin Ingestion Script",
    }

    try:
        print("1. Extracting text and parsing pages...")
        print("2. Splitting text into 500-token chunks with 100-token overlap...")
        print("3. Generating 384-dimensional vector embeddings...")
        print("4. Upserting vectors to Pinecone...")

        doc = KnowledgeService.upload_and_index_document(
            file_bytes=file_bytes,
            filename=filename,
            title=title,
            user=mock_admin_user,
            category=args.category,
        )

        print("=" * 60)
        print("✅ SUCCESS! Document indexed successfully.")
        print(f"🆔 Document ID: {doc.get('id')}")
        print(f"📊 Chunks Indexed: {doc.get('chunk_count')}")
        print(f"⚡ Status: {doc.get('status')}")
        print("=" * 60)
        print("You can now ask questions about this document in the AI Chatbot!")

    except Exception as e:
        print(f"❌ Ingestion failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
