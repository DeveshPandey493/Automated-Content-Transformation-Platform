import re
from typing import List, Dict, Any
from app.services.chunking.chunker import split_into_sentences

NUMBER_REGEX = re.compile(r'\b(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?%?(?:\s*(?:crore|lakh|billion|million|trillion|GW|MW|tonne|tonnes|km|percent))?\b', re.IGNORECASE)
DATE_YEAR_REGEX = re.compile(r'\b(?:19\d{2}|20\d{2}(?:-\d{2,4})?|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:,\s+\d{4})?)\b', re.IGNORECASE)
ENTITY_REGEX = re.compile(r'\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+|[A-Z]{2,})\b')

class ClaimExtractor:
    """Extracts atomic factual claims, numbers, dates, and named entities from text."""

    @staticmethod
    def extract_claims(text: str) -> List[Dict[str, Any]]:
        """
        Segments generated text into discrete factual claims categorized by type.
        """
        # Split into sentences
        sentences = split_into_sentences(text)
        claims = []

        for sent in sentences:
            sent_clean = sent.strip()
            # Skip pure markdown headers or bullet indicators
            if sent_clean.startswith("#") or sent_clean.startswith("**Q") or len(sent_clean) < 15:
                continue

            # Detect claim attributes
            has_numbers = bool(NUMBER_REGEX.search(sent_clean))
            has_dates = bool(DATE_YEAR_REGEX.search(sent_clean))
            has_entities = bool(ENTITY_REGEX.search(sent_clean))

            if has_numbers and has_dates:
                claim_type = "NUMERICAL_HISTORICAL"
            elif has_numbers:
                claim_type = "NUMERICAL"
            elif has_dates:
                claim_type = "DATE"
            elif has_entities:
                claim_type = "ENTITY"
            elif any(w in sent_clean.lower() for w in ["approved", "policy", "mandated", "initiative", "scheme", "mission"]):
                claim_type = "POLICY"
            else:
                claim_type = "GENERAL"

            claims.append({
                "claim_text": sent_clean,
                "claim_type": claim_type,
                "numbers": NUMBER_REGEX.findall(sent_clean),
                "dates": DATE_YEAR_REGEX.findall(sent_clean),
                "entities": ENTITY_REGEX.findall(sent_clean),
            })

        return claims
