import re
from typing import List, Dict, Any, Tuple

class ConstraintValidator:
    """Validates generated outputs against user-configured constraints."""

    @staticmethod
    def evaluate_constraints(
        content: str,
        target_words: int,
        required_keywords: List[str],
        prohibited_terms: List[str],
        format_type: str,
    ) -> Dict[str, Any]:
        words = len(re.findall(r"\b\w+\b", content))
        
        # 1. Length Compliance (0.0 to 1.0)
        if target_words > 0:
            diff = abs(words - target_words)
            length_score = max(0.0, 1.0 - (diff / target_words))
        else:
            length_score = 1.0

        # 2. Required Keywords Presence
        present_keywords = []
        missing_keywords = []
        for kw in required_keywords:
            if re.search(r"\b" + re.escape(kw) + r"\b", content, re.IGNORECASE):
                present_keywords.append(kw)
            else:
                missing_keywords.append(kw)

        keyword_score = (
            len(present_keywords) / len(required_keywords)
            if required_keywords
            else 1.0
        )

        # 3. Prohibited Terms Absence
        found_prohibited = []
        for pt in prohibited_terms:
            if re.search(r"\b" + re.escape(pt) + r"\b", content, re.IGNORECASE):
                found_prohibited.append(pt)

        prohibited_score = 0.0 if found_prohibited else 1.0

        # 4. Structural Format Section Adherence
        fmt = format_type.upper()
        format_score = 1.0
        sections_found = []

        if fmt == "EXECUTIVE_SUMMARY":
            expected = ["Overview", "Findings", "Implications"]
            for s in expected:
                if re.search(r"\b" + s + r"\b", content, re.IGNORECASE):
                    sections_found.append(s)
            format_score = len(sections_found) / len(expected)

        elif fmt == "PUBLIC_ADVISORY":
            expected = ["Advisory", "Action", "Guidance", "Fact"]
            for s in expected:
                if re.search(r"\b" + s + r"\b", content, re.IGNORECASE):
                    sections_found.append(s)
            format_score = max(0.5, len(sections_found) / len(expected))

        elif fmt == "FAQ":
            expected = ["Q", "A", "?"]
            has_q = bool(re.search(r"\bQ\d*:", content) or "?" in content)
            has_a = bool(re.search(r"\bA\d*:", content) or "Answer" in content)
            format_score = 1.0 if (has_q and has_a) else 0.5

        # Overall composite controllability score
        composite_score = round(
            (0.3 * length_score) + (0.3 * keyword_score) + (0.2 * prohibited_score) + (0.2 * format_score),
            3
        )

        return {
            "actual_words": words,
            "target_words": target_words,
            "length_score": round(length_score, 3),
            "keyword_score": round(keyword_score, 3),
            "present_keywords": present_keywords,
            "missing_keywords": missing_keywords,
            "prohibited_score": prohibited_score,
            "found_prohibited": found_prohibited,
            "format_score": round(format_score, 3),
            "controllability_score": composite_score,
            "is_fully_compliant": (
                composite_score >= 0.85
                and len(found_prohibited) == 0
                and len(missing_keywords) == 0
            ),
        }
