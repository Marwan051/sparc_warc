"""Groq prompt and output validation from the legacy v2.4.1 analyzer."""
import re
from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate


CATEGORIES = Literal[
    "Politics", "Economy", "Sports", "Technology",
    "Culture", "Health", "Society", "Religion",
    "Weather", "Food", "Crime", "Lifestyle", "Security",
    "Science", "Environment", "Other",
]

MAX_TAGS = 6

_NOT_ARTICLE_TAG_RE = re.compile(r"^\W*NOT[_ ]ARTICLE\b\W*", re.IGNORECASE)

_SELF_FLAGGED_NOISE_RE = re.compile(
    r"navigation|not (?:part of|a coherent)|no substantive|contains no "
    r"(?:substantive|article)|(?:author|reviewer) bio|donation|cookie|"
    r"menu de navigation|pas (?:un )?(?:article|de contenu)|aucun contenu|"
    r"\u0642\u0627\u0626\u0645\u0629 (?:\u062a\u0646\u0642\u0644|\u0631\u0648\u0627\u0628\u0637|\u0623\u0642\u0633\u0627\u0645)|\u0644\u0627 \u064a\u062d\u062a\u0648\u064a|\u0646\u0628\u0630\u0629 \u0639\u0646 \u0627\u0644\u0643\u0627\u062a\u0628",
    re.IGNORECASE,
)

_META_OPENING_RE = re.compile(
    r"^\W*(?:the (?:provided |given |above |following )?"
    r"(?:text|excerpt|passage|content|chunk)"
    r"|this (?:text|excerpt|passage|content|is|page)"
    r"|(?:ce|le) (?:texte|passage|contenu)(?: fourni)?"
    r"|cet extrait|il s.agit"
    r"|\u0647\u0630\u0627 \u0627\u0644\u0646\u0635|\u0627\u0644\u0646\u0635|\u064a\u064f\u0639\u062f\u0651 \u0647\u0630\u0627 \u0627\u0644\u0646\u0635|\u064a\u0639\u062f \u0647\u0630\u0627 \u0627\u0644\u0646\u0635)",
    re.IGNORECASE,
)

_NON_ARTICLE_TERMS_RE = re.compile(
    r"not (?:the |an? )?(?:actual )?article|not (?:part of|a coherent)|"
    r"no substantive|site navigation|website navigation|"
    r"navigation (?:menu|links?|block|elements?|bar)|"
    r"(?:ticket|seat)[- ]booking|booking page|"
    r"(?:station|site|page) header|metadata block|"
    r"forum (?:interface|header|page)|website interface|web interface|"
    r"interface (?:text|elements?|excerpt)|copyright notice|"
    r"donation appeal|promotional blurb|comments? policy|brief news headline|"
    r"extrait d.interface|interface utilisateur|liens? de navigation|"
    r"menu de navigation|ne contient (?:aucun|pas) (?:de )?(?:contenu|article)|"
    r"aucun contenu|pas (?:un )?article|"
    r"\u062a\u0631\u0648\u064a\u0633|\u0648\u0627\u062c\u0647\u0629 (?:\u0627\u0644\u0645\u0648\u0642\u0639|\u0645\u0648\u0642\u0639|\u0627\u0644\u0645\u0633\u062a\u062e\u062f\u0645)|\u0639\u0646\u0627\u0635\u0631 (?:\u0627\u0644\u062a\u0646\u0642\u0644|\u062a\u0646\u0642\u0644)|"
    r"\u0642\u0627\u0626\u0645\u0629 (?:\u0627\u0644\u062a\u0646\u0642\u0644|\u062a\u0646\u0642\u0644|\u0631\u0648\u0627\u0628\u0637|\u0623\u0642\u0633\u0627\u0645)|"
    r"\u0644\u0627 \u064a\u062d\u062a\u0648\u064a (?:\u0639\u0644\u0649 )?(?:\u0645\u062d\u062a\u0648\u0649|\u0645\u0642\u0627\u0644|\u0646\u0635)|\u0644\u064a\u0633 \u0645\u0642\u0627\u0644",
    re.IGNORECASE,
)

def is_noise_summary(summary: Optional[str], category: Optional[str]) -> bool:
    """True if the model's own summary says the chunk is not article content.

    NOTE: clean_results.py has a copy of these rules - keep both in sync.
    """
    s = (summary or "").strip()
    if not s:
        return False
    if _NOT_ARTICLE_TAG_RE.match(s):
        return True
    if category == "Other" and _SELF_FLAGGED_NOISE_RE.search(s):
        return True
    return bool(_META_OPENING_RE.match(s) and _NON_ARTICLE_TERMS_RE.search(s[:300]))

class ChunkAnalysis(BaseModel):
    summary: str = Field(
        description="A concise 1-2 sentence summary of just THIS piece of "
        "text, written in the SAME language as the original text."
    )
    category: CATEGORIES = Field(
        description="The single best topic category for just THIS piece of "
        "text, based only on what this chunk itself discusses."
    )
    tags: List[str] = Field(
        default_factory=list,
        description="3-6 short keyword tags for retrieval (RAG): named "
        "entities and specific topical terms that appear in THIS chunk, "
        "in the SAME language as the text. No generic tags."
    )

DEFAULT_GROQ_MODEL = "qwen/qwen3.8-27b"

CHUNK_MAX_TOKENS = 600

RETRY_TEMPERATURE = 0.3

LANGUAGE_NAMES = {"ar": "Arabic", "en": "English", "fr": "French"}

CHUNK_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a multilingual news analyst. You get ONE piece of a "
            "longer article. Based ONLY on it: write a concise 1-2 sentence "
            "summary in the input language, pick ONE category, and extract "
            "3-6 tags for a retrieval (RAG) system.\n\n"
            "Rules:\n"
            "- State only what the text says; never guess about unseen parts.\n"
            "- Do not present upcoming/undecided things as finished, and keep "
            "who-did-what exact (winners/losers, subjects/objects).\n"
            "- The title is context only: never take names, roles, titles or "
            "facts from it. Attribute a quote only to the person the TEXT "
            "names as the speaker; if the text does not say who, do not "
            "guess.\n"
            "- Tags must come from the text itself, never from the title, the "
            "publisher name or copyright lines.\n"
            "- The summary is plain sentences only: no JSON, XML or field "
            "names. Start directly with the subject (who did what, what "
            "happened). Never open with 'The text', 'This text', 'This is', "
            "'The article', 'Le texte', 'Ce texte' or 'هذا النص'.\n"
            "- Never add a year, date, name or number that is not in the "
            "text.\n"
            "- If the text is NOT article content (unreadable, site "
            "navigation or header, a list of unrelated headlines/links, a "
            "cookie notice, an author bio, a forum/booking/product-page "
            "interface, a newsletter or donation appeal): start the summary "
            "with the exact English word NOT_ARTICLE: followed by one short "
            "sentence saying what it is, use category 'Other', and take no "
            "tags from menus or link lists. Never invent a plausible summary "
            "from noise.\n"
            "- Tags: specific named entities (people, organizations, places, "
            "laws, events) and specific topical terms that appear in the "
            "text; no generic words, no category name, no invented entities; "
            "max 6.\n\n"
            "Categories (pick the most specific): Weather; Food (recipes, "
            "dishes, food labeling and restaurant rules); Religion (prayer, fiqh, religious holidays, sermons; "
            "not Culture); Culture (arts, entertainment, celebrities, books, "
            "festivals); Crime (police, arrests, courts, fraud; Society only "
            "for social issues that are not mainly crime); Health (medicine, "
            "public health, nutrition science); Lifestyle (beauty, "
            "horoscopes, fashion, relationship advice, consumer tips, "
            "deals); Security (military operations, battlefield events, "
            "weapons, terrorism, cyber security; diplomacy and government "
            "positions on a war are Politics); Politics; Economy; Sports; "
            "Technology; Science (space, physics, astronomy, research "
            "findings); Environment (climate, pollution, forests, rivers, "
            "wildlife); Society; Other (only if nothing fits).",
        ),
        (
            "human",
            "The input language is {language}. Write the summary in {language}.\n"
            "Article title (context only): {title}\n\n"
            "Text:\n\n{text}",
        ),
    ]
)

RETRYABLE_ERROR_SUBSTRINGS = (
    "rate_limit",
    "rate limit",
    "connection error",
    "connection reset",
    "timeout",
    "timed out",
    "remote end closed",
    "server disconnected",
    "leaked structured-output syntax",
    "bad summary",
)

_RETRYABLE_STATUS_RE = re.compile(r"error code:\s*(429|500|502|503|504)")

def _is_retryable(error_str: str) -> bool:
    low = error_str.lower()
    return any(s in low for s in RETRYABLE_ERROR_SUBSTRINGS) or bool(
        _RETRYABLE_STATUS_RE.search(low)
    )

def _is_daily_quota_error(error_str: str) -> bool:
    low = error_str.lower()
    return "tokens per day" in low or "(tpd)" in low

_WAIT_RE = re.compile(r"try again in (?:(\d+)m)?\s*([\d.]+)s", re.IGNORECASE)

MAX_AUTO_WAIT = 15 * 60

def _quota_wait_seconds(err: str) -> Optional[float]:
    m = _WAIT_RE.search(err)
    if not m:
        return None
    return int(m.group(1) or 0) * 60 + float(m.group(2)) + 5

_SUMMARY_CONTAMINATION_MARKERS = (
    "</summary>", "<summary>", "<parameter", "</parameter",
    '"category":', '"tags":', '"summary":', "```json", "<|", "|>",
)

def _is_contaminated_summary(summary: Optional[str]) -> bool:
    if not summary:
        return False
    return any(m in summary for m in _SUMMARY_CONTAMINATION_MARKERS)

def _cap_tags(tags: Optional[List[str]], max_tags: int = MAX_TAGS) -> List[str]:
    return (tags or [])[:max_tags]

_TAG_TOKEN_RE = re.compile(r"\w{3,}", re.UNICODE)

def _norm_token(t: str) -> str:
    t = t.lower()
    return t[2:] if t.startswith("\u0627\u0644") and len(t) > 4 else t

def _filter_tags(tags: Optional[List[str]], text: str,
                 min_keep: int = 2) -> List[str]:
    """Keep tags with at least one word that appears in the chunk text.

    Drops tags the model took from the title or the publisher name. If fewer
    than min_keep tags survive, the original list is kept (better than none).
    """
    tags = tags or []
    hay = (text or "").lower()
    kept = []
    for tag in tags:
        toks = [_norm_token(t) for t in _TAG_TOKEN_RE.findall(tag)]
        if toks and any(t in hay for t in toks):
            kept.append(tag)
    return kept if len(kept) >= min_keep else tags

_FOREIGN_SCRIPT_RE = re.compile(
    r"[\u0400-\u04FF\u0E00-\u0E7F\u1100-\u11FF\u3040-\u30FF\u3400-\u9FFF\uAC00-\uD7AF]"
)

_TERMINALS = tuple(".!?\u2026\u00bb\u201d\")\u3002\u061f")

def _summary_problem(summary: str, lang: str) -> Optional[str]:
    """Return a reason if the summary is unusable (triggers a retry)."""
    s = (summary or "").strip()
    if not s:
        return "empty summary"
    if _is_contaminated_summary(s):
        return "leaked structured-output syntax"
    if _FOREIGN_SCRIPT_RE.search(s):
        return "foreign script in summary"
    if lang.lower() in ("en", "fr") and re.search(r"[\u0600-\u06FF]", s):
        return "Arabic script in non-Arabic summary"
    if not s.endswith(_TERMINALS):
        return "truncated summary"
    return None
