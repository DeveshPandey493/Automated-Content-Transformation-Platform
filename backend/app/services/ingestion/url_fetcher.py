import datetime
from typing import Dict, Any, Tuple
import httpx
from bs4 import BeautifulSoup
from app.core.security import validate_url_for_ssrf
from app.core.exceptions import DocumentProcessingError
from app.services.ingestion.extractors import normalize_text, count_words

async def fetch_and_extract_url(url: str) -> Tuple[str, str, Dict[str, Any]]:
    """
    Safely fetches a web URL, enforcing SSRF protections, timeout, and max size.
    Returns (page_title, cleaned_text, metadata).
    """
    # 1. SSRF DNS validation
    validate_url_for_ssrf(url)

    # 2. HTTP Request with strict limits
    headers = {
        "User-Agent": "ACTP-GovAI-Crawler/1.0 (+https://github.com/actp-platform)"
    }
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True, max_redirects=3) as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                raise DocumentProcessingError(
                    f"Remote server returned HTTP status {response.status_code} while fetching URL: {url}"
                )
            
            # Check content length (max 10MB)
            content = response.content
            if len(content) > 10 * 1024 * 1024:
                raise DocumentProcessingError(f"Remote document size exceeds 10MB ceiling: {url}")
    except httpx.RequestError as e:
        raise DocumentProcessingError(f"Network error while fetching URL '{url}': {e}")

    # 3. HTML parsing and article text extraction
    soup = BeautifulSoup(content, "html.parser")

    # Remove script, style, nav, footer, header tags
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "svg"]):
        tag.decompose()

    # Extract Title
    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    elif soup.find("h1"):
        title = soup.find("h1").get_text().strip()
    else:
        title = url.split("/")[-1] or "Web Article"

    # Prioritize article, main, or content containers
    main_content = soup.find("article") or soup.find("main") or soup.find("body") or soup
    raw_text = main_content.get_text(separator="\n")
    cleaned_text = normalize_text(raw_text)

    if len(cleaned_text) < 50:
        raise DocumentProcessingError(f"Insufficient textual content extracted from URL: {url}")

    meta = {
        "format": "html",
        "source_url": url,
        "retrieved_at": datetime.datetime.utcnow().isoformat(),
        "extracted_title": title,
    }

    return title, cleaned_text, meta
