from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.db.models.document import DocumentChunk

class EvidenceRetriever:
    """Retrieves top supporting source document chunks for a given claim."""

    @staticmethod
    def retrieve_evidence_chunks(
        claim_text: str,
        chunks: List[DocumentChunk],
        top_k: int = 3,
    ) -> List[Tuple[DocumentChunk, float]]:
        """
        Calculates relevance between claim text and all document chunks.
        Returns top_k (chunk, relevance_score) pairs.
        """
        if not chunks:
            return []

        chunk_texts = [c.text for c in chunks]
        corpus = [claim_text] + chunk_texts

        try:
            vectorizer = TfidfVectorizer(stop_words="english", lowercase=True)
            tfidf_matrix = vectorizer.fit_transform(corpus)
            claim_vec = tfidf_matrix[0]
            chunk_vecs = tfidf_matrix[1:]
            scores = cosine_similarity(claim_vec, chunk_vecs).flatten()
        except ValueError:
            scores = np.zeros(len(chunks))

        ranked = [
            (chunks[i], float(scores[i]))
            for i in range(len(chunks))
        ]
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked[:top_k]
