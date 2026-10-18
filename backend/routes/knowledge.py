import logging
from flask import Blueprint, request, jsonify, g
from utils.auth_middleware import require_auth, require_role
from services.knowledge_service import KnowledgeService
from models.schemas import (
    KnowledgeSearchRequest,
    KnowledgeArticleGenerateRequest,
    KnowledgeArticleUpdateRequest,
)

logger = logging.getLogger(__name__)
knowledge_bp = Blueprint("knowledge", __name__)


@knowledge_bp.route("/api/knowledge/documents", methods=["POST"])
@require_role(["it_agent", "admin"])
def upload_document():
    """Uploads and indexes a technical document (PDF, DOCX, TXT, CSV) into Pinecone."""
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file uploaded in form field 'file'."}), 400

    uploaded_file = request.files["file"]
    if uploaded_file.filename == "":
        return jsonify({"success": False, "error": "Selected file is empty."}), 400

    title = request.form.get("title") or uploaded_file.filename
    category = request.form.get("category", "General IT")

    try:
        file_bytes = uploaded_file.read()
        doc = KnowledgeService.upload_and_index_document(
            file_bytes=file_bytes,
            filename=uploaded_file.filename,
            title=title,
            user=g.current_user,
            category=category,
        )
        return jsonify({
            "success": True,
            "document": doc,
        }), 201
    except Exception as e:
        logger.error(f"Upload and indexing failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


@knowledge_bp.route("/api/knowledge/documents", methods=["GET"])
@require_role(["it_agent", "admin"])
def list_documents():
    """Lists indexed knowledge documents."""
    try:
        docs = KnowledgeService.list_documents()
        return jsonify({
            "success": True,
            "documents": docs,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@knowledge_bp.route("/api/knowledge/documents/<document_id>", methods=["GET"])
@require_role(["it_agent", "admin"])
def get_document(document_id: str):
    try:
        doc = KnowledgeService.get_document(document_id)
        return jsonify({
            "success": True,
            "document": doc,
        })
    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@knowledge_bp.route("/api/knowledge/documents/<document_id>", methods=["DELETE"])
@require_role(["it_agent", "admin"])
def delete_document(document_id: str):
    """Deletes document and removes associated vectors from Pinecone."""
    try:
        KnowledgeService.delete_document(document_id, user=g.current_user)
        return jsonify({
            "success": True,
            "message": f"Document {document_id} and associated vectors successfully removed.",
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@knowledge_bp.route("/api/knowledge/search", methods=["POST"])
@require_auth
def search_knowledge():
    """Semantic vector search against indexed technical documentation."""
    data = request.get_json() or {}
    try:
        req = KnowledgeSearchRequest(**data)
        results = KnowledgeService.search_knowledge(
            query=req.query,
            top_k=req.top_k,
            category=req.category,
        )
        return jsonify({
            "success": True,
            "results": results,
            "count": len(results),
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


# ==================== KNOWLEDGE ARTICLES ====================

@knowledge_bp.route("/api/knowledge/articles", methods=["GET"])
@require_auth
def list_articles():
    """Returns published knowledge articles for employees, all for IT staff."""
    status = request.args.get("status")
    category = request.args.get("category")
    user_role = g.current_user.get("role", "employee")

    if user_role == "employee":
        status = "published" # Employees only see published guides

    try:
        articles = KnowledgeService.list_articles(status=status, category=category)
        return jsonify({
            "success": True,
            "articles": articles,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@knowledge_bp.route("/api/knowledge/articles/generate", methods=["POST"])
@require_role(["it_agent", "admin"])
def generate_article():
    """Auto-generates draft knowledge article from resolved ticket using Groq GPT-OSS."""
    data = request.get_json() or {}
    try:
        req = KnowledgeArticleGenerateRequest(**data)
        article = KnowledgeService.generate_article_from_ticket(req.ticket_id, user=g.current_user)
        return jsonify({
            "success": True,
            "article": article,
        }), 201
    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@knowledge_bp.route("/api/knowledge/articles/<article_id>", methods=["PATCH"])
@require_role(["it_agent", "admin"])
def update_article(article_id: str):
    data = request.get_json() or {}
    try:
        req = KnowledgeArticleUpdateRequest(**data)
        updates = req.model_dump(exclude_unset=True)
        updated = KnowledgeService.update_article(article_id, updates, user=g.current_user)
        return jsonify({
            "success": True,
            "article": updated,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@knowledge_bp.route("/api/knowledge/articles/<article_id>/approve", methods=["POST"])
@require_role(["admin"])
def approve_article(article_id: str):
    """Admin approval to publish article and index into vector search."""
    try:
        article = KnowledgeService.approve_article(article_id, user=g.current_user)
        return jsonify({
            "success": True,
            "article": article,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@knowledge_bp.route("/api/knowledge/articles/<article_id>/reject", methods=["POST"])
@require_role(["admin"])
def reject_article(article_id: str):
    try:
        article = KnowledgeService.reject_article(article_id, user=g.current_user)
        return jsonify({
            "success": True,
            "article": article,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400
