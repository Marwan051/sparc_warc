import os
import re
import json
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Dict, Any, List
from urllib.parse import parse_qsl, unquote, urlencode, urljoin, urlsplit, urlunsplit

from selectolax.parser import HTMLParser
from ingestion.text import decode_and_validate, is_clean_encoding, is_valid_arabic_text

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

# Metadata is kept small and bounded so a pathological page cannot bloat a row.
MAX_META_VALUE_CHARS = 2000
MAX_JSONLD_BLOCK_BYTES = 8 * 1024
MAX_HTML_META_BYTES = 32 * 1024
MAX_DESCRIPTION_CHARS = 2000
MAX_KEYWORDS = 20
MAX_AUTHOR_NAMES = 10
MAX_CANONICAL_CHARS = 2048
MAX_HTML_JSONLD_BLOCKS = 8

TRACKING_QUERY_KEYS = {
    "fbclid", "gclid", "dclid", "gbraid", "wbraid", "msclkid",
    "mc_cid", "mc_eid", "igshid", "yclid", "_ga", "_gl",
}
ARTICLE_JSONLD_TYPES = (
    "NewsArticle", "ReportageNewsArticle", "Article", "BlogPosting", "WebPage",
)
LANGUAGE_NAMES = {
    "arabic": "ar", "english": "en", "french": "fr",
    "spanish": "es", "german": "de", "italian": "it",
}

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


def _jsonld_types(obj):
    value = obj.get("@type") if isinstance(obj, dict) else None
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        return {str(item) for item in value}
    return set()


def _ordered_jsonld(objects):
    """Article-shaped objects first; ignore page chrome when an article exists."""
    ranked = []
    for preferred in ARTICLE_JSONLD_TYPES:
        for obj in objects:
            if obj not in ranked and preferred in _jsonld_types(obj):
                ranked.append(obj)
    return ranked or list(objects)


def _first_jsonld_value(objects, *keys):
    for obj in _ordered_jsonld(objects):
        for key in keys:
            value = obj.get(key)
            if value:
                return value
    return None


def _meta_map(tree):
    meta = {}
    for node in tree.css("meta"):
        key = (
            node.attributes.get("property")
            or node.attributes.get("name")
            or node.attributes.get("http-equiv")
            or ""
        ).strip().lower()
        content = (node.attributes.get("content") or "").strip()
        if key and content:
            meta.setdefault(key, []).append(content[:MAX_META_VALUE_CHARS])
    return meta


def _link_payload(tree):
    links = {"canonical": None, "alternate": []}
    canonical = tree.css_first("link[rel=canonical]")
    if canonical:
        links["canonical"] = (canonical.attributes.get("href") or "").strip() or None
    for node in tree.css("link[rel=alternate][hreflang]"):
        href = (node.attributes.get("href") or "").strip()
        hreflang = (node.attributes.get("hreflang") or "").strip()
        if href:
            links["alternate"].append({"href": href[:MAX_CANONICAL_CHARS], "hreflang": hreflang})
    return links


def normalize_url(url):
    """Return a stable comparison key for a URL, or None if it is not HTTP(S)."""
    if not url:
        return None
    try:
        parts = urlsplit(str(url).strip())
        port = parts.port
    except ValueError:
        return None
    scheme = parts.scheme.lower()
    if scheme not in ("http", "https"):
        return None
    host = (parts.hostname or "").lower().rstrip(".")
    if not host:
        return None
    if host.startswith("www."):
        host = host[4:]
    netloc = host
    if port and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
        netloc = f"{host}:{port}"
    path = unquote(parts.path) or "/"
    if len(path) > 1:
        path = path.rstrip("/")
    query = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if key.lower() not in TRACKING_QUERY_KEYS and not key.lower().startswith("utm_")
    ]
    return urlunsplit((scheme, netloc, path, urlencode(sorted(query)), ""))


def _canonical_pair(tree, page_url):
    links = _link_payload(tree)
    raw = links["canonical"]
    resolved = urljoin(page_url or "", raw) if raw else None
    if resolved:
        try:
            resolved = urlunsplit(urlsplit(resolved)._replace(fragment=""))
        except ValueError:
            resolved = None
    canonical_url = resolved[:MAX_CANONICAL_CHARS] if resolved else None
    canonical_key = normalize_url(canonical_url) if canonical_url else None
    if canonical_url and not canonical_key:
        canonical_url = None
    if not canonical_key and page_url:
        canonical_key = normalize_url(page_url)
    return canonical_url, canonical_key, links


def parse_datetime(value):
    """Parse ISO-8601/RFC-822 metadata dates into an aware UTC datetime."""
    if value is None or isinstance(value, datetime):
        parsed = value
    else:
        text = str(value).strip()
        if not text or text.upper() == "N/A":
            return None
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            try:
                parsed = parsedate_to_datetime(text)
            except (TypeError, ValueError, OverflowError):
                return None
    if parsed is None:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def normalize_language(value):
    if not value:
        return None
    text = str(value).strip().lower().replace("_", "-")
    if not text:
        return None
    if text in LANGUAGE_NAMES:
        return LANGUAGE_NAMES[text]
    code = text.split("-", 1)[0]
    return code if code.isalpha() and len(code) in (2, 3) else None


def _term_list(value):
    if value is None:
        return []
    items = value if isinstance(value, list) else [value]
    terms = []
    for item in items:
        if isinstance(item, dict):
            item = item.get("name") or item.get("@value") or ""
        if isinstance(item, (list, tuple)):
            terms.extend(_term_list(item))
            continue
        for term in re.split(r"[,;]", str(item)):
            term = term.strip()
            if term and term not in terms:
                terms.append(term[:200])
            if len(terms) >= MAX_KEYWORDS:
                return terms
    return terms


def _name_list(value):
    names = []
    if isinstance(value, str):
        text = value.strip()
        if text:
            names.append(text[:300])
    elif isinstance(value, dict):
        name = value.get("name") or value.get("alternateName")
        if name:
            names.extend(_name_list(name))
    elif isinstance(value, (list, tuple)):
        for item in value:
            names.extend(_name_list(item))
    unique = []
    for name in names:
        if name not in unique:
            unique.append(name)
        if len(unique) >= MAX_AUTHOR_NAMES:
            break
    return unique


def _publisher_name(value):
    names = _name_list(value)
    return names[0] if names else None


def _html_meta_payload(meta, links, jsonld_objects):
    blocks = []
    for obj in jsonld_objects[:MAX_HTML_JSONLD_BLOCKS]:
        try:
            encoded = json.dumps(obj, ensure_ascii=False)
        except (TypeError, ValueError):
            continue
        if len(encoded.encode("utf-8")) <= MAX_JSONLD_BLOCK_BYTES:
            blocks.append(obj)
    payload = {"meta": meta, "links": links, "jsonld": blocks}

    def size(candidate):
        return len(json.dumps(candidate, ensure_ascii=False).encode("utf-8"))

    if size(payload) <= MAX_HTML_META_BYTES:
        return payload
    payload = {"meta": meta, "links": links, "jsonld": []}
    if size(payload) <= MAX_HTML_META_BYTES:
        return payload
    compact = {
        key: [value[:256] for value in values[:3]]
        for key, values in list(meta.items())[:40]
    }
    payload = {"meta": compact, "links": links, "jsonld": [], "truncated": True}
    if size(payload) <= MAX_HTML_META_BYTES:
        return payload
    return {"truncated": True, "meta_keys": sorted(compact)[:40]}


def extract_publication_date(tree: HTMLParser, objects=None) -> str:
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
    for item in _ordered_jsonld(objects if objects is not None else list(_jsonld_from_tree(tree))):
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

def extract_author(tree: HTMLParser, objects=None) -> str:
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
    for item in _ordered_jsonld(objects if objects is not None else list(_jsonld_from_tree(tree))):
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


def _first_meta_value(meta, *keys):
    for key in keys:
        values = meta.get(key)
        if values:
            return values[0]
    return None


def extract_html_fields(record: Dict[str, Any], min_words: int = 80, use_trafilatura=None) -> Dict[str, Any]:
    html_str, status = decode_and_validate(record["raw_bytes"], record.get("charset"))
    if status != "success" or not html_str:
        return {"language": "corrupted", "word_count": 0, "clean_text": "", "extraction": "corrupted"}
    tree = HTMLParser(html_str)
    # Metadata scripts and tags must be read before unwanted elements are removed.
    meta = _meta_map(tree)
    objects = list(_jsonld_from_tree(tree))
    ordered = _ordered_jsonld(objects)
    canonical_url, canonical_key, links = _canonical_pair(tree, record.get("url"))
    title_node = tree.css_first("title")
    headline = _first_jsonld_value(ordered, "headline")
    title = title_node.text(strip=True) if title_node else (
        str(headline).strip() if headline else "N/A"
    )
    pub_date = extract_publication_date(tree, ordered)
    author = extract_author(tree, ordered)
    modified_value = _first_meta_value(
        meta, "article:modified_time", "og:updated_time", "last-modified"
    ) or _first_jsonld_value(ordered, "dateModified")
    description_value = _first_meta_value(
        meta, "description", "og:description", "twitter:description"
    ) or _first_jsonld_value(ordered, "description")
    section_value = _first_meta_value(meta, "article:section") or _first_jsonld_value(
        ordered, "articleSection"
    )
    if isinstance(section_value, (list, tuple)):
        section_value = section_value[0] if section_value else None
    declared_language = _first_jsonld_value(ordered, "inLanguage")
    if isinstance(declared_language, dict):
        declared_language = declared_language.get("@value") or declared_language.get("name")
    html_node = tree.css_first("html")
    if not declared_language and html_node:
        declared_language = html_node.attributes.get("lang")
    keywords = _term_list(meta.get("keywords"))
    for term in _term_list(_first_jsonld_value(ordered, "keywords")):
        if term not in keywords and len(keywords) < MAX_KEYWORDS:
            keywords.append(term)
    tags = _term_list(meta.get("article:tag"))
    for name in _name_list(_first_jsonld_value(ordered, "about", "mentions")):
        if name not in tags and len(tags) < MAX_KEYWORDS:
            tags.append(name)
    author_names = _name_list(
        ([] if author == "N/A" else [author]) + _name_list(_first_jsonld_value(ordered, "author"))
    )
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
    # Validate what will actually be classified and stored. Corruption in the
    # article body can be diluted by markup when the raw HTML is checked above.
    if not is_clean_encoding(clean_text):
        return {
            "language": "corrupted",
            "word_count": 0,
            "clean_text": "",
            "extraction": extraction,
        }
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
        "published_at": parse_datetime(pub_date),
        "modified_at": parse_datetime(modified_value),
        "description": str(description_value).strip()[:MAX_DESCRIPTION_CHARS] if description_value else None,
        "publisher": _publisher_name(_first_jsonld_value(ordered, "publisher")),
        "in_language": normalize_language(declared_language),
        "section": str(section_value).strip()[:200] if section_value else None,
        "keywords": keywords,
        "tags": tags,
        "author_names": author_names,
        "canonical_url": canonical_url,
        "canonical_key": canonical_key,
        "html_meta": _html_meta_payload(meta, links, objects),
        "clean_text": clean_text,
        "word_count": word_cnt,
        "char_count": len(clean_text),
        "html_size_bytes": len(record["raw_bytes"]),
        "links_count": len(tree.css("a")),
        "headings_sample": [node.text(strip=True) for node in tree.css("h1, h2, h3")][:3],
        "extraction": extraction,
    }
