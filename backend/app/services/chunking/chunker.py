import re
from typing import List, Dict, Any, Optional

SENTENCE_SPLIT_REGEX = re.compile(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s+')

def split_into_sentences(text: str) -> List[str]:
    """Splits text into sentences while respecting common abbreviations."""
    sentences = SENTENCE_SPLIT_REGEX.split(text)
    return [s.strip() for s in sentences if s.strip()]

def chunk_document_text(
    full_text: str,
    target_words: int = 150,
    overlap_words: int = 25,
    page_records: Optional[List[Dict[str, Any]]] = None,
    section_records: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """
    Chunks document text at sentence boundaries.
    Calculates deterministic char_start, char_end, approximate token counts,
    and maps page numbers or section headings where available.
    """
    sentences = split_into_sentences(full_text)
    if not sentences:
        return []

    chunks = []
    current_sentences: List[str] = []
    current_word_count = 0
    chunk_index = 0

    # Helper to find character offset of substring in text
    search_cursor = 0

    def finalize_chunk(sentence_list: List[str], idx: int) -> Dict[str, Any]:
        nonlocal search_cursor
        chunk_str = " ".join(sentence_list)
        words = len(re.findall(r"\b\w+\b", chunk_str))
        approx_tokens = int(words * 1.3)

        # Find character offset
        start_char = full_text.find(sentence_list[0], search_cursor)
        if start_char == -1:
            start_char = full_text.find(sentence_list[0])
        end_char = start_char + len(chunk_str) if start_char != -1 else len(chunk_str)
        if start_char != -1:
            search_cursor = max(search_cursor, start_char)

        # Attribute page number if PDF page_records provided
        page_num = None
        if page_records:
            # Match against page records by checking overlap
            for p in page_records:
                if sentence_list[0] in p.get("text", ""):
                    page_num = p.get("page_number")
                    break

        # Attribute section heading if DOCX section_records provided
        section_heading = None
        if section_records:
            for s in section_records:
                if sentence_list[0] in s.get("text", ""):
                    section_heading = s.get("section_heading")
                    break

        return {
            "chunk_index": idx,
            "char_start": max(0, start_char),
            "char_end": max(0, end_char),
            "text": chunk_str,
            "token_count": approx_tokens,
            "page_number": page_num,
            "section_heading": section_heading,
        }

    for sent in sentences:
        sent_words = len(re.findall(r"\b\w+\b", sent))
        if current_word_count + sent_words > target_words and current_sentences:
            chunks.append(finalize_chunk(current_sentences, chunk_index))
            chunk_index += 1

            # Compute overlap sentences
            overlap_sentences = []
            overlap_count = 0
            for s in reversed(current_sentences):
                s_words = len(re.findall(r"\b\w+\b", s))
                if overlap_count + s_words <= overlap_words:
                    overlap_sentences.insert(0, s)
                    overlap_count += s_words
                else:
                    break

            current_sentences = overlap_sentences + [sent]
            current_word_count = overlap_count + sent_words
        else:
            current_sentences.append(sent)
            current_word_count += sent_words

    if current_sentences:
        chunks.append(finalize_chunk(current_sentences, chunk_index))

    return chunks
