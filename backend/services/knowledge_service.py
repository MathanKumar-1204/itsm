import os
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from repositories.db_repository import db
from repositories.supabase_client import get_supabase_admin_client
from utils.document_parser import validate_file, extract_text, chunk_document
from ai.rag_pipeline import rag_pipeline
from ai.groq_client import groq_client

logger = logging.getLogger(__name__)


class KnowledgeService:
    @classmethod
    def upload_and_index_document(
        cls,
        file_bytes: bytes,
        filename: str,
        title: str,
        user: Dict[str, Any],
        category: str = "General IT"
    ) -> Dict[str, Any]:
        """
        Validates, uploads to storage, extracts text, chunks, embeds, and indexes to Pinecone.
        """
        user_role = user.get("role", "employee")
        if user_role not in ["it_agent", "admin"]:
            raise PermissionError("Only IT staff and administrators can upload knowledge documents.")

        is_valid, err = validate_file(filename, len(file_bytes))
        if not is_valid:
            raise ValueError(err)

        user_id = user["id"]
        doc_id = str(uuid.uuid4())
        clean_title = (title or filename).strip()
        storage_path = f"documents/{doc_id}/{filename}"

        # 1. Attempt Supabase storage upload if configured
        admin_client = get_supabase_admin_client()
        if admin_client:
            try:
                # Ensure bucket exists
                try:
                    admin_client.storage.create_bucket("knowledge-base", options={"public": False})
                except Exception:
                    pass
                admin_client.storage.from_("knowledge-base").upload(storage_path, file_bytes)
            except Exception as e:
                logger.warning(f"Could not upload file to Supabase storage bucket: {e}")

        # 2. Create document record with 'processing' status
        doc_record = {
            "id": doc_id,
            "uploaded_by": user_id,
            "title": clean_title,
            "original_filename": filename,
            "storage_path": storage_path,
            "mime_type": os.path.splitext(filename)[1].lower(),
            "file_size": len(file_bytes),
            "status": "processing",
            "chunk_count": 0,
        }
        db.create_knowledge_document(doc_record)

        # 3. Text Extraction and Chunking
        try:
            sections = extract_text(file_bytes, filename)
            if not sections:
                raise ValueError("No extractable text was found in the document.")

            chunks = chunk_document(sections, chunk_size=500, chunk_overlap=100)
            if not chunks:
                raise ValueError("Document yielded 0 text chunks.")

            # 4. Generate embeddings and upsert into Pinecone
            chunk_count = rag_pipeline.index_document_chunks(
                doc_id=doc_id,
                doc_title=clean_title,
                filename=filename,
                chunks=chunks,
                category=category,
            )

            # 5. Mark indexed
            updated_doc = db.update_knowledge_document(doc_id, {
                "status": "indexed",
                "chunk_count": chunk_count,
                "error_message": None,
            })

            db.log_audit(
                actor_id=user_id,
                action="index_knowledge_document",
                entity_type="knowledge_document",
                entity_id=doc_id,
                metadata={"filename": filename, "chunk_count": chunk_count},
            )

            return updated_doc

        except Exception as e:
            logger.error(f"Ingestion failed for document {doc_id}: {e}")
            db.update_knowledge_document(doc_id, {
                "status": "failed",
                "error_message": str(e),
            })
            raise RuntimeError(f"Document ingestion failed: {e}")

    @classmethod
    def list_documents(cls) -> List[Dict[str, Any]]:
        return db.list_knowledge_documents()

    @classmethod
    def get_document(cls, doc_id: str) -> Dict[str, Any]:
        doc = db.get_knowledge_document(doc_id)
        if not doc:
            raise ValueError(f"Document '{doc_id}' not found.")
        return doc

    @classmethod
    def delete_document(cls, doc_id: str, user: Dict[str, Any]) -> bool:
        user_role = user.get("role", "employee")
        if user_role not in ["it_agent", "admin"]:
            raise PermissionError("Only IT staff and administrators can delete knowledge documents.")

        # Delete vectors
        rag_pipeline.delete_document_vectors(doc_id)
        # Delete record
        db.delete_knowledge_document(doc_id)

        db.log_audit(
            actor_id=user["id"],
            action="delete_knowledge_document",
            entity_type="knowledge_document",
            entity_id=doc_id,
        )
        return True

    @classmethod
    def search_knowledge(cls, query: str, top_k: int = 4, category: Optional[str] = None) -> List[Dict[str, Any]]:
        return rag_pipeline.search_knowledge(query=query, top_k=top_k, category=category)

    # ==================== KNOWLEDGE ARTICLE AUTOMATION ====================

    @classmethod
    def generate_article_from_ticket(cls, ticket_id: str, user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Drafts a structured knowledge article from a resolved ticket using Groq GPT-OSS.
        """
        user_role = user.get("role", "employee")
        if user_role not in ["it_agent", "admin"]:
            raise PermissionError("Only IT staff can draft knowledge articles from tickets.")

        ticket = db.get_ticket(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket '{ticket_id}' not found.")

        # Check resolution notes
        if not ticket.get("resolution") and ticket.get("status") not in ["resolved", "closed"]:
            raise ValueError("Cannot generate article from an unresolved ticket with no confirmed resolution.")

        prompt = (
            f"You are a Senior Technical Writer for an enterprise IT Knowledge Base.\n"
            f"Transform this resolved support ticket into a standardized reusable Knowledge Base article.\n\n"
            f"TICKET DETAILS:\n"
            f"- Title: {ticket.get('title')}\n"
            f"- Category: {ticket.get('category')}\n"
            f"- Problem Description: {ticket.get('description')}\n"
            f"- Confirmed Resolution: {ticket.get('resolution') or 'Resolved by standard procedures'}\n\n"
            f"Generate a JSON object with this exact structure:\n"
            f"{{\n"
            f'  "title": "Clear, searchable article title (e.g. How to Resolve...)",\n'
            f'  "summary": "Brief 2-3 sentence overview of the issue and fix",\n'
            f'  "content": "Full markdown guide with ## Problem, ## Symptoms, ## Root Cause, ## Resolution Steps, ## Prevention Tips",\n'
            f'  "category": "{ticket.get("category", "General IT")}"\n'
            f"}}"
        )

        title = f"Resolution Guide: {ticket.get('title')}"
        summary = f"Troubleshooting and resolution guide based on ticket {ticket.get('ticket_number')}."
        category = ticket.get("category", "General IT")
        content = (
            f"## Problem\n{ticket.get('description')}\n\n"
            f"## Resolution Steps\n{ticket.get('resolution', 'Follow standard diagnostic procedures.')}\n\n"
            f"## Prevention\nEnsure hardware and software drivers are kept up to date."
        )

        if groq_client.is_configured():
            try:
                res = groq_client.chat_json(messages=[{"role": "user", "content": prompt}], temperature=0.2)
                title = res.get("title", title)
                summary = res.get("summary", summary)
                content = res.get("content", content)
                category = res.get("category", category)
            except Exception as e:
                logger.warning(f"Groq article generation failed: {e}")

        article_data = {
            "title": title,
            "summary": summary,
            "content": content,
            "category": category,
            "source_ticket_id": ticket_id,
            "status": "draft",
            "created_by": user["id"],
        }
        saved_article = db.create_knowledge_article(article_data)

        db.log_audit(
            actor_id=user["id"],
            action="generate_knowledge_article",
            entity_type="knowledge_article",
            entity_id=saved_article["id"],
            metadata={"source_ticket_id": ticket_id},
        )

        return saved_article

    @classmethod
    def list_articles(cls, status: Optional[str] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
        return db.list_knowledge_articles(status=status, category=category)

    @classmethod
    def update_article(cls, article_id: str, updates: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        user_role = user.get("role", "employee")
        if user_role not in ["it_agent", "admin"]:
            raise PermissionError("Only IT staff can update knowledge articles.")
        return db.update_knowledge_article(article_id, updates)

    @classmethod
    def approve_article(cls, article_id: str, user: Dict[str, Any]) -> Dict[str, Any]:
        user_role = user.get("role", "employee")
        if user_role != "admin":
            raise PermissionError("Only administrators can approve knowledge articles for publication.")

        now = datetime.now(timezone.utc).isoformat()
        article = db.update_knowledge_article(article_id, {
            "status": "published",
            "approved_by": user["id"],
            "approved_at": now,
        })

        # Automatically index published article into vector database
        if article:
            chunks = [{
                "chunk_index": 0,
                "text": f"{article['title']}\n\n{article.get('summary', '')}\n\n{article['content']}",
                "page": 1,
                "section": "Article",
            }]
            rag_pipeline.index_document_chunks(
                doc_id=f"article_{article_id}",
                doc_title=article["title"],
                filename=f"article_{article_id}.md",
                chunks=chunks,
                category=article.get("category", "General IT"),
            )

        db.log_audit(
            actor_id=user["id"],
            action="approve_knowledge_article",
            entity_type="knowledge_article",
            entity_id=article_id,
        )
        return article

    @classmethod
    def reject_article(cls, article_id: str, user: Dict[str, Any]) -> Dict[str, Any]:
        user_role = user.get("role", "employee")
        if user_role != "admin":
            raise PermissionError("Only administrators can reject knowledge articles.")

        article = db.update_knowledge_article(article_id, {
            "status": "rejected",
        })
        db.log_audit(
            actor_id=user["id"],
            action="reject_knowledge_article",
            entity_type="knowledge_article",
            entity_id=article_id,
        )
        return article
