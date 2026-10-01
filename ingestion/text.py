import re
from typing import Optional, Tuple
from charset_normalizer import from_bytes

ARABIC_CHAR_PATTERN = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]')
# Letters that never occur in genuine Arabic but are routine in neighbours
# sharing the script. Lingua lacks Kurdish, so Sorani markers are the
# backstop there; fa/ur markers catch Persian/Urdu that still scores 'ar'.
NON_ARABIC_MARKERS = re.compile(
    '['
    '\u067E\u0686\u0698\u06AF\u06A9\u06CC'  # fa: pe che jeem gaf kaf yeh
    '\u0679\u0688\u0691\u06BA\u06BE\u06D2'  # ur: tte ddahal rre noon-ghunna he-do-chashmee bare-ye
    '\u06D5\u0695\u06B5\u06C6\u06CE'        # ku (Sorani): ae rra lla o u
    ']'
)

def is_target_language(lang_code: str) -> bool:
    if not lang_code:
        return False
    lang = str(lang_code).lower().strip()
    return lang in {"ar", "en", "fr"}

def is_clean_encoding(text: str) -> bool:
    if not text or "\ufffd" in text or "\x00" in text:
        return False
    # Ordinary accented Latin letters are valid French. Flag characteristic
    # UTF-8-as-Latin-1 byte sequences instead of treating every accent as bad.
    mojibake = re.findall(r"(?:Ã[\x80-\xBF]|Â[\x80-\xBF]|â[\x80-\xBF]{2})", text)
    if len(mojibake) >= 3 and sum(map(len, mojibake)) / len(text) > 0.01:
        return False
    controls = sum(1 for c in text if ord(c) < 32 and c not in "\n\r\t\f")
    if controls / len(text) > 0.001:
        return False
    return True

def is_valid_arabic_text(text: str) -> bool:
    if not text or len(text) < 20:
        return False
    sample = text[:500]
    arabic_chars = sum(c.isalpha() and bool(ARABIC_CHAR_PATTERN.match(c)) for c in sample)
    alpha_chars = sum(1 for c in sample if c.isalpha())
    if alpha_chars == 0:
        return False
    if (arabic_chars / alpha_chars) < 0.40:
        return False
    # Arabic-script neighbours (fa/ur/ku): a handful of distinctive letters
    # disqualifies, genuine Arabic carries none of them.
    markers = len(NON_ARABIC_MARKERS.findall(sample))
    if markers >= 2 and (markers / max(arabic_chars, 1)) > 0.02:
        return False
    return True

def decode_and_validate(raw_bytes: bytes, declared_encoding: Optional[str] = None) -> Tuple[Optional[str], str]:
    if not raw_bytes:
        return None, "empty_bytes"
    decoded_text = None
    if declared_encoding:
        try:
            decoded_text = raw_bytes.decode(declared_encoding, errors="strict")
        except (LookupError, UnicodeError):
            pass
    try:
        if decoded_text is None:
            decoded_text = raw_bytes.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        pass
    if not decoded_text:
        try:
            results = from_bytes(raw_bytes)
            best_match = results.best()
            if best_match and best_match.encoding:
                if not (best_match.encoding.lower() in ["iso-8859-1", "latin-1"] and best_match.coherence < 0.8):
                    decoded_text = str(best_match)
        except Exception:
            pass
    if not decoded_text:
        try:
            decoded_text = raw_bytes.decode("windows-1256", errors="strict")
        except UnicodeDecodeError:
            pass
    if not decoded_text:
        return None, "decode_failed"
    decoded_text = decoded_text.replace("\x00", "")
    if not is_clean_encoding(decoded_text):
        return None, "encoding_corrupted"
    return decoded_text, "success"
