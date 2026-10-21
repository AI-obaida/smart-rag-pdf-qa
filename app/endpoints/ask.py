from functools import lru_cache
from urllib.error import URLError

from flask import Blueprint, current_app, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.models import Document
from app.services.structured_rag_service import StructuredRAGService
from app.services.citation_entailment_validator import CitationEntailmentValidator
from app.services.question_relevance_guard import QuestionRelevanceGuard
from app.services.question_fact_consistency_guard import QuestionFactConsistencyGuard


ask_bp = Blueprint("ask", __name__, url_prefix="/api/ask")


@lru_cache(maxsize=1)
def get_embedding_model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(
        "intfloat/multilingual-e5-small",
        device="cpu",
    )


@ask_bp.post("")
def ask_pdf():
    if not request.is_json:
        return jsonify({
            "error": "Content-Type must be application/json"
        }), 415

    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        return jsonify({
            "error": "Invalid JSON object"
        }), 400

    question = payload.get("question")
    document_id = payload.get("document_id")
    top_k = payload.get("top_k", 3)

    if not isinstance(question, str) or not question.strip():
        return jsonify({
            "error": "question must not be empty"
        }), 400

    if (
        not isinstance(document_id, int)
        or isinstance(document_id, bool)
        or document_id < 1
    ):
        return jsonify({
            "error": "document_id must be a positive integer"
        }), 400

    if (
        not isinstance(top_k, int)
        or isinstance(top_k, bool)
        or not 1 <= top_k <= 20
    ):
        return jsonify({
            "error": "top_k must be between 1 and 20"
        }), 400

    try:
        document = db.session.get(Document, document_id)

        if document is None:
            return jsonify({
                "error": "Document not found"
            }), 404

        model = get_embedding_model()

        service = StructuredRAGService(
            embedding_model=model,
            citation_validator=CitationEntailmentValidator(
                model="qwen2.5:3b",
            ),
            relevance_guard=QuestionRelevanceGuard(
                model="qwen2.5:3b",
            ),
        )

        service.consistency_guard = QuestionFactConsistencyGuard()

        result = service.ask(
            question=question,
            document_id=document_id,
            top_k=top_k,
        )

        return jsonify(result), 200

    except SQLAlchemyError:
        current_app.logger.exception("Database error in Ask API")
        return jsonify({
            "error": "Database operation failed"
        }), 503

    except (ConnectionError, TimeoutError, URLError):
        current_app.logger.exception("Model connection failed")
        return jsonify({
            "error": "AI model service unavailable"
        }), 503

    except Exception:
        current_app.logger.exception("Ask API failed")
        return jsonify({
            "error": "Unable to answer the question"
        }), 500

