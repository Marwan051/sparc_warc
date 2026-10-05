"""Deterministic article cleanup and eligibility, ported from v2.4.1."""
import re
from typing import Optional
from urllib.parse import urlparse
from langchain_core.documents import Document


MIN_CHUNK_CHARS = 250

BOILERPLATE_PREFIXES = (
    "legal disclaimer",
    "menafn provides the information",
    "© copyright",
    "all rights reserved",
    "disclaimer:",
    "this article is meant for information purposes only",
    "this article and information do not constitute",
    "forward-looking statements contained in this press release",
    "securities and exchange commission",
    "skip to main content",
    "skip to content",
    "aller au contenu",
    "passer au contenu",
    "n'assume aucune responsabilit",
    "n’assume aucune responsabilit",
)

BLOCKED_DOMAINS = {
    "sixactualites.fr", "lg.com",
    "realting.com",        # real-estate UI text
    "kinoafisha.info",     # cinema ticket-booking pages
}

_NON_ARTICLE_URL_RE = re.compile(
    r"/publi-|/sponsored|advertorial|/partner-content|/forums?/",
    re.IGNORECASE,
)

_SITE_HEADER_MARKERS = ("Privacy Policy", "\u062a\u0633\u062c\u064a\u0644 \u0627\u0644\u062f\u062e\u0648\u0644",
                        "Se connecter")

_SITE_HEADER_MAX = 2500

_COPYRIGHT_TAIL_RE = re.compile(
    r"\s*(?:\u00a9|Copyright)\s*(?:19|20)\d{2}\b[^\n]{0,60}$", re.IGNORECASE
)

_CUT_MARKERS = (
    "Read more »",
    "Similar News:",
    "United States Latest News",
    "\u0635\u0648\u062a \u0627\u0644\u062d\u062c\u0627\u0632 \u0623\u0648\u0644 \u062c\u0631\u064a\u062f\u0629",
)

MIN_SCRIPT_RATIO = {"ar": 0.50, "en": 0.70, "fr": 0.70}

_MOJIBAKE_RE = re.compile(
    r"[ذر][^\u0600-\u06FF\s\d.,;:!?()«»\"'\-/%]"
    r"|[ØÙÐÑÃÂ][\u0080-\u00BF\u2018-\u203A\u0152\u0153\u0160\u0161\u0178\u017D\u017E\u0192\u02C6\u02DC]"
    r"|ط[§¨©ª«¬®¯°±]|ظ[„…†‡]"
    r"|\ufffd"
)

MOJIBAKE_RATIO_THRESHOLD = 0.03

GARBLED_MIN_LEN_TO_CHECK = 40

_HEADLINE_AGGREGATOR_PATTERN = re.compile(
    r"\d{2}:\d{2}\s*\|\s*\d{4}-\d{2}-\d{2}.*\d{2}:\d{2}\s*\|\s*\d{4}-\d{2}-\d{2}"
    r"|(?:\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}\s+){2}"
    r"|(?:Lebanon 24\s+){2,}",
    re.DOTALL,
)

_AUTHOR_BIO_RE = re.compile(
    r"(?:\bis an? [\w\s,-]{0,40}(?:journalist|reporter|editor|writer|correspondent)\b"
    r".{0,120}(?:years? of experience|covers|covering|when she|when he))"
    r"|(?:^[\W_]*(?:she|he) (?:also )?(?:covers|writes about|reports on)\b)",
    re.IGNORECASE | re.DOTALL,
)

_NPR_BIO_RE = re.compile(
    r"\bSee stories by\b|\bCopyright\s+(?:19|20)\d{2}\s+NPR\b", re.IGNORECASE
)

def _domain(url: Optional[str]) -> str:
    host = (urlparse(url or "").netloc or "").lower()
    return host[4:] if host.startswith("www.") else host

def _strip_site_header(text: str) -> str:
    """Drop a site-menu header that ends with 'Advertisement'."""
    i = text.find("Advertisement", 0, _SITE_HEADER_MAX)
    if i != -1 and any(m in text[:i] for m in _SITE_HEADER_MARKERS):
        return text[i + len("Advertisement"):].lstrip()
    return text

def clean_article_text(text: str) -> str:
    """Strip the menu header, cut at the first 'link list' marker, drop
    a trailing copyright line."""
    if not text:
        return text
    text = _strip_site_header(text)
    cut = len(text)
    for m in _CUT_MARKERS:
        i = text.find(m)
        if i != -1:
            cut = min(cut, i)
    text = text[:cut].rstrip()
    return _COPYRIGHT_TAIL_RE.sub("", text).rstrip()

def _is_boilerplate_chunk(text: str) -> bool:
    if not text:
        return True
    head = text.strip()[:160].lower()
    return any(head.startswith(p) or p in head for p in BOILERPLATE_PREFIXES)

def _script_ratio(text: str, lang: str) -> float:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    if lang == "ar":
        ok = sum(
            "\u0600" <= c <= "\u06FF" or "\u0750" <= c <= "\u077F"
            or "\uFB50" <= c <= "\uFEFF"
            for c in letters
        )
    else:
        ok = sum(c.isascii() or "\u00C0" <= c <= "\u024F" for c in letters)
    return ok / len(letters)

def _is_garbled_text(text: str, lang: Optional[str] = None) -> bool:
    """Mojibake, or text whose script does not match the labelled language."""
    if not text:
        return True
    sample = text[:600]
    if len(sample) < GARBLED_MIN_LEN_TO_CHECK:
        return False
    if len(_MOJIBAKE_RE.findall(sample)) / len(sample) > MOJIBAKE_RATIO_THRESHOLD:
        return True
    lang = (lang or "").lower()
    if lang in MIN_SCRIPT_RATIO and _script_ratio(sample, lang) < MIN_SCRIPT_RATIO[lang]:
        return True
    return False

def _is_headline_aggregator(text: str) -> bool:
    return bool(text) and bool(_HEADLINE_AGGREGATOR_PATTERN.search(text[:500]))

_SENT_END_RE = re.compile(r"[.!?\u061f\u3002](?:\s|$)")

def _looks_like_headline_list(text: str) -> bool:
    """Long text with almost no sentences/commas = nav menu or news ticker."""
    if text.count("\u00b0C") >= 3:            # city temperature strips
        return True
    if len(re.findall(r"\(\d+\)", text)) >= 5:  # "SECTION NAME (218)" menus
        return True
    return (len(text) >= 500
            and len(_SENT_END_RE.findall(text)) <= 1
            and len(re.findall(r"[,\u060c]", text)) <= 2)

def _is_author_bio(text: str) -> bool:
    return bool(_AUTHOR_BIO_RE.search(text[:400]) or _NPR_BIO_RE.search(text))

def _noise_reason(c: Document) -> Optional[str]:
    """Return why a chunk should be dropped, or None if it is usable."""
    text = (c.page_content or "").strip()
    lang = (c.metadata.get("language") or "").lower()
    if len(text) < MIN_CHUNK_CHARS or _is_boilerplate_chunk(text):
        return "short"
    if _domain(c.metadata.get("source")) in BLOCKED_DOMAINS:
        return "blocked"
    if _NON_ARTICLE_URL_RE.search(c.metadata.get("source") or ""):
        return "non_article_url"
    if any(m in text for m in _CUT_MARKERS):
        return "linklist"
    if _is_author_bio(text):
        return "bio"
    if _looks_like_headline_list(text):
        return "headlines"
    if _is_garbled_text(text, lang):
        return "garbled"
    if _is_headline_aggregator(text):
        return "aggregator"
    return None

def noise_reason(chunk):
    """Stable reason for excluding a chunk, or None."""
    return _noise_reason(chunk)
