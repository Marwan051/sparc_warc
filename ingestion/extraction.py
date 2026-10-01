import os
import re
import json
from typing import Dict, Any, List
from selectolax.parser import HTMLParser
from ingestion.text import decode_and_validate, is_valid_arabic_text

ARABIC_PATTERN = re.compile(r'[\u0600-\u06FF]')
LATIN_PATTERN = re.compile(r'[a-zA-Z]')
CYRILLIC_PATTERN = re.compile(r'[\u0400-\u04FF]')
# CJK scripts: kana is Japanese-specific, hangul Korean-specific, han shared
# (mostly Chinese in news, also used in Japanese).
KANA_PATTERN = re.compile(r'[\u3040-\u30FF]')
HANGUL_PATTERN = re.compile(r'[\uAC00-\uD7AF\u1100-\u11FF]')
CJK_PATTERN = re.compile(r'[\u3040-\u30FF\u4E00-\u9FFF\uAC00-\uD7AF]')

USE_TRAFILATURA = os.environ.get("USE_TRAFILATURA", "1") == "1"
TARGET_LANGUAGES = {"ar", "en", "fr"}

UNWANTED_TAGS = ["script", "style", "noscript", "header", "footer", "svg", "nav"]

# Language ID via Lingua (n-gram models, no torch). Detector is built lazily
# once in each long-lived Spark Python worker.
LINGUA_LANGUAGES = (
    "ARABIC", "ENGLISH", "FRENCH", "SPANISH", "GERMAN", "ITALIAN",
    "PORTUGUESE", "CATALAN", "ROMANIAN", "RUSSIAN", "TURKISH",
    "VIETNAMESE", "JAPANESE", "KOREAN", "CHINESE", "DUTCH", "TAMIL",
    "UKRAINIAN", "PERSIAN", "URDU",
)
LINGUA_MIN_CONFIDENCE = float(os.environ.get("LINGUA_MIN_CONFIDENCE", "0.5"))
_lingua_detector = None


def get_lingua_detector():
    global _lingua_detector
    if _lingua_detector is None:
        from lingua import Language, LanguageDetectorBuilder
        _lingua_detector = (
            LanguageDetectorBuilder.from_languages(
                *[getattr(Language, name) for name in LINGUA_LANGUAGES]
            )
            .with_preloaded_language_models()
            .build()
        )
    return _lingua_detector


_LINGUA_TO_CODE = {
    "ARABIC": "ar",
    "ENGLISH": "en",
    "FRENCH": "fr",
    "RUSSIAN": "ru",
    "JAPANESE": "ja",
    "KOREAN": "ko",
    "CHINESE": "zh",
    "PERSIAN": "fa",
    "URDU": "ur",
}

# Full Latin block (ASCII patterns miss French accents). Used only by the
# script gate below; existing patterns stay untouched.
_LATIN_FULL_PATTERN = re.compile(r"[a-zA-ZÀ-ɏḀ-ỿ]")
_SUPPORTED_SCRIPTS = re.compile(
    r"[a-zA-ZÀ-ɏḀ-ỿ\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\u0400-\u04FF"
    r"\u3040-\u30FF\u4E00-\u9FFF\uAC00-\uD7AF\u1100-\u11FF]"
)


def _unsupported_script_share(text: str) -> float:
    """Share of alpha chars outside Latin/Arabic/Cyrillic/CJK.

    Catches bodies in unloaded scripts (Kannada, Hindi, Bengali, ...) that
    boilerplate chrome smuggled past lingua's head sample: the chrome votes
    Latin, but a fifth or more of the full text is none of the above.
    """
    if not text:
        return 1.0
    alpha_count = 0
    other_count = 0
    for char in text:
        if not char.isalpha():
            continue
        alpha_count += 1
        if not _SUPPORTED_SCRIPTS.match(char):
            other_count += 1
    if not alpha_count:
        return 1.0
    return other_count / alpha_count


def _language_sample(text: str) -> str:
    """Sample the beginning, middle, and end without duplicating short text."""
    if len(text) <= 2000:
        return text
    middle_start = max(800, min(len(text) // 2 - 300, len(text) - 1200))
    return text[:800] + " " + text[middle_start:middle_start + 600] + " " + text[-600:]


def detect_languages_batch(texts: List[str], min_confidence=None) -> List[str]:
    if not texts:
        return []
    threshold = LINGUA_MIN_CONFIDENCE if min_confidence is None else min_confidence
    detector = get_lingua_detector()
    results = []
    for text in texts:
        if not text or len(text) < 20:
            results.append("unknown")
            continue
        sample = _language_sample(text)
        has_script = (
            ARABIC_PATTERN.search(sample)
            or LATIN_PATTERN.search(sample)
            or CYRILLIC_PATTERN.search(sample)
            or CJK_PATTERN.search(sample)
        )
        if not has_script:
            results.append("ignored")
            continue
        try:
            confidence = detector.compute_language_confidence_values(sample)
        except Exception:
            results.append("other")
            continue
        if not confidence or confidence[0].value <= 0.0:
            results.append("ignored")
            continue
        top = confidence[0]
        if top.value < threshold:
            results.append("other")
            continue
        code = _LINGUA_TO_CODE.get(top.language.name, "other")
        if code in ("en", "fr", "ar") and _unsupported_script_share(text) > 0.10:
            results.append("other")
            continue
        if code == "ar" and not is_valid_arabic_text(text):
            results.append("corrupted")
            continue
        results.append(code)
    return results

def _jsonld_objects(value):
    if isinstance(value, list):
        for item in value:
            yield from _jsonld_objects(item)
    elif isinstance(value, dict):
        yield value
        if "@graph" in value:
            yield from _jsonld_objects(value["@graph"])


def _jsonld_from_tree(tree):
    for script_node in tree.css("script[type='application/ld+json']"):
        raw = script_node.text(strip=True)
        if not raw:
            continue
        try:
            yield from _jsonld_objects(json.loads(raw))
        except (json.JSONDecodeError, ValueError, TypeError):
            continue


def extract_publication_date(tree: HTMLParser) -> str:
    meta_selectors = [
        ("meta[property='article:published_time']", "content"),
        ("meta[name='pubdate']", "content"),
        ("meta[name='publishdate']", "content"),
        ("meta[name='date']", "content"),
        ("meta[name='DC.date.issued']", "content"),
        ("meta[name='parsely-pub-date']", "content")
    ]
    for selector, attr in meta_selectors:
        node = tree.css_first(selector)
        if node and node.attributes.get(attr):
            date_val = node.attributes.get(attr).strip()
            if date_val:
                return date_val
    for item in _jsonld_from_tree(tree):
        date_val = item.get("datePublished") or item.get("dateCreated")
        if date_val:
            return str(date_val).strip()
    time_node = tree.css_first("time")
    if time_node:
        datetime_val = time_node.attributes.get("datetime")
        if datetime_val:
            return datetime_val.strip()
        text_val = time_node.text(strip=True)
        if text_val:
            return text_val
    return "N/A"

def extract_date_from_text_fallback(tree: HTMLParser) -> str:
    body_text = tree.body.text() if tree.body else tree.text()
    date_match = re.search(r'\b(19\d\d|20\d\d)[-/.](0?[1-9]|1[0-2])[-/.](0?[1-9]|[12]\d|3[01])\b', body_text)
    return date_match.group(0) if date_match else "N/A"

def extract_author(tree: HTMLParser) -> str:
    author_selectors = [
        ("meta[name='author']", "content"),
        ("meta[property='article:author']", "content"),
        ("meta[name='parsely-author']", "content"),
        ("meta[name='dc.creator']", "content"),
        ("meta[name='author_name']", "content")
    ]
    for selector, attr in author_selectors:
        node = tree.css_first(selector)
        if node and node.attributes.get(attr):
            val = node.attributes.get(attr).strip()
            if val:
                return val
    for item in _jsonld_from_tree(tree):
        if "author" not in item:
            continue
        author_data = item["author"]
        if isinstance(author_data, dict) and author_data.get("name"):
            return str(author_data["name"]).strip()
        if isinstance(author_data, list) and author_data:
            first = author_data[0]
            if isinstance(first, dict) and first.get("name"):
                return str(first["name"]).strip()
            if isinstance(first, str):
                return first.strip()
        if isinstance(author_data, str):
            return author_data.strip()
    return "N/A"

def _trafilatura_text(html_str: str) -> str:
    """Main-content extraction via trafilatura. Returns '' on failure/None."""
    try:
        from trafilatura import extract as _trafi_extract
        text = _trafi_extract(html_str, include_comments=False, include_tables=False)
    except Exception:
        return ""
    if not text:
        return ""
    return " ".join(text.split())


def extract_html_fields(record: Dict[str, Any], min_words: int = 80, use_trafilatura=None) -> Dict[str, Any]:
    html_str, status = decode_and_validate(record["raw_bytes"], record.get("charset"))
    if status != "success" or not html_str:
        return {"language": "corrupted", "word_count": 0, "clean_text": "", "extraction": "corrupted"}
    tree = HTMLParser(html_str)
    title_node = tree.css_first("title")
    title = title_node.text(strip=True) if title_node else "N/A"
    # Metadata scripts must be read before unwanted elements are removed.
    pub_date = extract_publication_date(tree)
    author = extract_author(tree)
    use_trafilatura = USE_TRAFILATURA if use_trafilatura is None else use_trafilatura
    trafi_text = _trafilatura_text(html_str) if use_trafilatura else ""
    for tag in tree.css(", ".join(UNWANTED_TAGS)):
        tag.decompose()
    if trafi_text and len(trafi_text.split()) >= min_words:
        clean_text = trafi_text
        extraction = "trafilatura"
    else:
        body = tree.body
        raw_text = body.text(separator=' ', strip=True) if body else tree.text(separator=' ', strip=True)
        clean_text = " ".join(raw_text.split())
        extraction = "selectolax"
    clean_text = clean_text.replace("\x00", "")
    word_cnt = len(clean_text.split())
    if word_cnt < min_words:
        return {"language": "too_short", "word_count": word_cnt, "clean_text": "", "extraction": extraction}
    if pub_date == "N/A":
        pub_date = extract_date_from_text_fallback(tree)
    return {
        "title": title,
        "author": author,
        "url": record["url"],
        "warc_date": record["warc_date"],
        "published_date": pub_date,
        "clean_text": clean_text,
        "word_count": word_cnt,
        "char_count": len(clean_text),
        "html_size_bytes": len(record["raw_bytes"]),
        "links_count": len(tree.css("a")),
        "headings_sample": [node.text(strip=True) for node in tree.css("h1, h2, h3")][:3],
        "extraction": extraction,
    }
