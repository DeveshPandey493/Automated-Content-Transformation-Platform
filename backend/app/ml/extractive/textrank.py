import math
import re
from typing import List, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class TextRankSentenceRanker:
    """Graph-based PageRank sentence importance scoring."""

    @staticmethod
    def rank_sentences(
        sentences: List[str],
        damping: float = 0.85,
        max_iter: int = 100,
        tol: float = 1e-4,
    ) -> List[Tuple[int, str, float]]:
        """
        Builds sentence similarity graph and executes PageRank iterations.
        Returns list of (original_index, sentence, score).
        """
        N = len(sentences)
        if N == 0:
            return []
        if N == 1:
            return [(0, sentences[0], 1.0)]

        # 1. Similarity matrix
        try:
            vec = TfidfVectorizer(stop_words="english", lowercase=True)
            matrix = vec.fit_transform(sentences)
            sim_matrix = cosine_similarity(matrix, matrix)
        except ValueError:
            sim_matrix = np.ones((N, N)) / N

        # Zero out self-loops
        np.fill_diagonal(sim_matrix, 0.0)

        # Normalize rows to form transition probability matrix
        row_sums = sim_matrix.sum(axis=1)
        # Avoid division by zero
        row_sums[row_sums == 0] = 1.0
        transition_matrix = sim_matrix / row_sums[:, np.newaxis]

        # 2. Power iteration PageRank
        scores = np.ones(N) / N
        for _ in range(max_iter):
            prev_scores = np.copy(scores)
            scores = (1 - damping) / N + damping * transition_matrix.T.dot(prev_scores)
            if np.linalg.norm(scores - prev_scores, 1) < tol:
                break

        ranked = [
            (idx, sent, float(scores[idx]))
            for idx, sent in enumerate(sentences)
        ]
        ranked.sort(key=lambda x: x[2], reverse=True)
        return ranked

    @staticmethod
    def select_top_sentences(
        sentences: List[str],
        target_words: int = 250,
    ) -> List[Tuple[int, str]]:
        """Selects highest ranked sentences up to word limit in chronological order."""
        ranked = TextRankSentenceRanker.rank_sentences(sentences)
        selected_indices = set()
        total_words = 0

        for orig_idx, sent, score in ranked:
            words = len(re.findall(r"\b\w+\b", sent))
            if total_words + words <= target_words or not selected_indices:
                selected_indices.add(orig_idx)
                total_words += words
            if total_words >= target_words:
                break

        return [(idx, sentences[idx]) for idx in sorted(selected_indices)]
