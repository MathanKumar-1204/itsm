import pytest
from ai.rag_pipeline import RAGPipeline, generate_embedding, cosine_similarity


def test_embedding_dimension_and_normalization():
    vec = generate_embedding("GlobalProtect VPN connection guide")
    assert len(vec) == 384
    # Check unit norm approximately
    norm = sum(v * v for v in vec) ** 0.5
    assert abs(norm - 1.0) < 0.05


def test_cosine_similarity():
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    v3 = [0.0, 1.0, 0.0]

    assert abs(cosine_similarity(v1, v2) - 1.0) < 0.001
    assert abs(cosine_similarity(v1, v3) - 0.0) < 0.001


def test_rag_indexing_and_citation_retrieval():
    pipeline = RAGPipeline()

    chunks = [
        {
            "chunk_index": 0,
            "text": "To connect to GlobalProtect VPN, open the client, enter portal vpn.corp.com, and complete Microsoft Authenticator MFA within 60 seconds.",
            "page": 1,
            "section": "VPN Authentication",
        },
        {
            "chunk_index": 1,
            "text": "For email configuration, configure Microsoft Outlook with OAuth2 modern authentication pointing to outlook.office365.com.",
            "page": 2,
            "section": "Email Setup",
        },
    ]

    indexed_count = pipeline.index_document_chunks(
        doc_id="doc-test-101",
        doc_title="Remote Work IT Handbook",
        filename="remote_handbook.pdf",
        chunks=chunks,
        category="Network",
    )
    assert indexed_count == 2

    # Query for VPN
    results = pipeline.search_knowledge("How do I connect to the corporate VPN?", top_k=2)
    assert len(results) > 0
    top_result = results[0]
    assert top_result["document_id"] == "doc-test-101"
    assert top_result["title"] == "Remote Work IT Handbook"
    assert "vpn.corp.com" in top_result["excerpt"]
    assert top_result["score"] > 0


def test_rag_missing_context_behavior():
    pipeline = RAGPipeline()
    # Query completely unrelated to any indexed tech documentation
    res = pipeline.answer_with_rag("What is the recipe for chocolate chip cookies?")
    assert res["has_grounded_context"] is False
    assert len(res["sources"]) == 0
    assert "did not find documented internal policies" in res["answer"]
    assert "Create Ticket" in res["suggested_actions"]
