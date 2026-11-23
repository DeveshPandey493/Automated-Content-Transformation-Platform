import re
from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.services.chunking.chunker import split_into_sentences

class TfidfSentenceRanker:
    """Ranks document sentences by cosine similarity to whole-document TF-IDF centroid."""

    @staticmethod
    def rank_sentences(sentences: List[str]) -> List[Tuple[int, str, float]]:
        """
        Calculates sentence importance scores.
        Returns list of (original_index, sentence_text, importance_score).
        """
        if not sentences:
            return []
        if len(sentences) == 1:
            return [(0, sentences[0], 1.0)]

        try:
            vectorizer = TfidfVectorizer(
                stop_words="english",
                lowercase=True,
                max_features=5000,
            )
            tfidf_matrix = vectorizer.fit_transform(sentences)
        except ValueError:
            # Fallback if vocabulary empty
            return [(i, s, 1.0 / len(sentences)) for i, s in enumerate(sentences)]

        # Document centroid (mean TF-IDF vector)
        doc_centroid = np.asarray(tfidf_matrix.mean(axis=0))

        # Compute cosine similarity of each sentence to the centroid
        scores = cosine_similarity(tfidf_matrix, doc_centroid).flatten()

        ranked = []
        for idx, (sent, score) in enumerate(zip(sentences, scores)):
            ranked.append((idx, sent, float(score)))

        # Sort descending by score
        ranked.sort(key=lambda x: x[2], reverse=True)
        return ranked

    @staticmethod
    def select_top_sentences(
        sentences: List[str],
        target_words: int = 250,
    ) -> List[Tuple[int, str]]:
        """
        Selects top sentences up to target word limit while preserving original chronological order.
        """
        ranked = TfidfSentenceRanker.rank_sentences(sentences)
        selected_indices = set()
        total_words = 0

        for orig_idx, sent, score in ranked:
            words = len(re.findall(r"\b\w+\b", sent))
            if total_words + words <= target_words or not selected_indices:
                selected_indices.add(orig_idx)
                total_words += words
            if total_words >= target_words:
                break

        # Re-sort into chronological appearance
        chronological = [
            (idx, sentences[idx])
            for idx in sorted(selected_indices)
        ]
        return chronological
