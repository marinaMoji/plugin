# -*- coding: utf-8 -*-
"""
Shared Japanese typography analysis (host-independent).

No UNO imports. LibreOffice / future Word adapters feed plain data structures.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

# Bundled ja_JP locale defaults (LibreOffice i18npool ja_JP.xml). Used only when
# the host cannot supply ForbiddenCharacters for the applicable locale.
DEFAULT_JA_NOT_START = (
    "!%),.:;?]}¢°’”‰′″℃、。々〉》」』】〕ぁぃぅぇぉっゃゅょゎ゛゜ゝゞ"
    "ァィゥェォッャュョヮヵヶ・ーヽヾ！％），．：；？］｝｡｣､･ｧｨｩｪｫｬｭｮｯｰﾞﾟ¢"
)
DEFAULT_JA_NOT_END = "$([¥{£¥‘“〈《「『【〔＄（［｛｢£￥"

# Fullwidth JP punct ↔ non-fullwidth forms (Western ASCII and halfwidth JP).
# Each non-fullwidth form is labeled for clear per-occurrence reports.
# variant: "western" | "halfwidth_jp"
_PAIR_FORMS = (
    # role, fullwidth, (char, variant_key, label_en)
    (
        "IDEOGRAPHIC_FULL_STOP",
        "。",
        (
            (".", "western", "Western full stop"),
            ("｡", "halfwidth_jp", "Halfwidth Japanese full stop"),
        ),
    ),
    (
        "IDEOGRAPHIC_COMMA",
        "、",
        (
            (",", "western", "Western comma"),
            ("､", "halfwidth_jp", "Halfwidth Japanese comma"),
        ),
    ),
    (
        "PAREN_OPEN",
        "（",
        (("(", "western", "Western opening parenthesis"),),
    ),
    (
        "PAREN_CLOSE",
        "）",
        ((")", "western", "Western closing parenthesis"),),
    ),
)

# Cap occurrence listings so huge pastes stay readable (still many more than one).
_MAX_PUNCT_OCCURRENCES = 80

# Soft line break markers that may appear inside a single paragraph string.
# Paragraph boundaries are handled separately and are NOT treated as soft breaks.
_SOFT_BREAK_CHARS = ("\n", "\v", "\u2028")

SEVERITY_INFO = "information"
SEVERITY_ADVISORY = "advisory"
SEVERITY_WARNING = "warning"

CATEGORY_SETTING = "composition_setting"
CATEGORY_PUNCTUATION = "punctuation"
CATEGORY_EXPLICIT_BREAK = "explicit_line_break"

RULE_PARA_FORBIDDEN_OFF = "PARA_FORBIDDEN_RULES_OFF"
RULE_PUNCTUATION_MIXED_WIDTH = "PUNCTUATION_MIXED_WIDTH"
RULE_EXPLICIT_BREAK_BEFORE_NOTSTART = "EXPLICIT_BREAK_BEFORE_NOTSTART"


@dataclass(frozen=True)
class TextSpan:
    """Host-neutral span within one paragraph's extracted plain text."""

    start: int
    end: int
    paragraph_index: int = 0


@dataclass
class TypographyDiagnostic:
    rule_id: str
    category: str
    severity: str
    message_key: str
    evidence: str
    affected: Optional[TextSpan] = None
    message_parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


@dataclass
class ParagraphSnapshot:
    """Extracted paragraph facts for analysis (no UNO objects)."""

    index: int
    text: str
    # Effective booleans or None if unavailable
    para_is_forbidden_rules: Optional[bool] = None
    para_is_hanging_punctuation: Optional[bool] = None
    para_is_character_distance: Optional[bool] = None
    # PropertyState hints: "direct" | "default" | "ambiguous" | "unknown"
    forbidden_rules_state: str = "unknown"
    hanging_state: str = "unknown"
    distance_state: str = "unknown"
    # Locale hints
    lang_asian: Optional[str] = None  # e.g. "ja"
    lang_western: Optional[str] = None
    # Soft-break positions: indices of break characters inside text
    soft_break_offsets: Tuple[int, ...] = ()
    # Annotation flags (presence only)
    has_ruby: bool = False
    has_warichu: bool = False
    has_tatechuyoko: bool = False
    # Body text for punctuation rules (ruby readings stripped when possible)
    body_text: Optional[str] = None


@dataclass
class DocumentSnapshot:
    character_compression_type: Optional[int] = None  # 0/1/2 or None
    is_kern_asian_punctuation: Optional[bool] = None
    # Locale → {"begin": str, "end": str} or empty if unavailable
    forbidden_by_locale: Dict[str, Dict[str, str]] = field(default_factory=dict)


@dataclass
class InspectionScope:
    selection_kind: str  # caret_paragraph | selection_single | selection_multi | unsupported
    paragraphs: List[ParagraphSnapshot] = field(default_factory=list)
    document: DocumentSnapshot = field(default_factory=DocumentSnapshot)
    notes: List[str] = field(default_factory=list)


@dataclass
class SettingValue:
    key: str
    value: Any  # bool | int | str | "mixed" | None
    display: str  # preformatted English key; UI layer localizes
    mixed_detail: Optional[str] = None


@dataclass
class InspectionReport:
    scope_kind: str
    paragraph_count: int
    settings: List[SettingValue]
    diagnostics: List[TypographyDiagnostic]
    notes: List[str] = field(default_factory=list)
    limited_coverage: bool = True


def _cjk_ratio(text: str) -> float:
    if not text:
        return 0.0
    cjk = 0
    letters = 0
    for ch in text:
        o = ord(ch)
        if ch.isspace() or ch in "\n\v\u2028":
            continue
        letters += 1
        # CJK Unified + kana + punctuation blocks commonly used in JP text
        if (
            0x3040 <= o <= 0x30FF
            or 0x3400 <= o <= 0x9FFF
            or 0xF900 <= o <= 0xFAFF
            or 0x3000 <= o <= 0x303F
            or 0xFF00 <= o <= 0xFFEF
        ):
            cjk += 1
    if letters == 0:
        return 0.0
    return cjk / float(letters)


def _looks_japanese_context(para: ParagraphSnapshot) -> bool:
    lang = (para.lang_asian or "").lower()
    if lang.startswith("ja"):
        return True
    text = para.body_text if para.body_text is not None else para.text
    return _cjk_ratio(text) >= 0.35


def _latin_window_ratio(text: str, center: int, radius: int = 12) -> float:
    a = max(0, center - radius)
    b = min(len(text), center + radius + 1)
    window = text[a:b]
    if not window:
        return 0.0
    latin = sum(1 for ch in window if ("A" <= ch <= "Z") or ("a" <= ch <= "z"))
    return latin / float(len(window))


def _is_urlish(text: str) -> bool:
    lower = text.lower()
    return "http://" in lower or "https://" in lower or "www." in lower


def find_soft_break_offsets(text: str) -> Tuple[int, ...]:
    """Indices of soft-break characters inside a paragraph string."""
    out = []
    for i, ch in enumerate(text):
        if ch in _SOFT_BREAK_CHARS:
            out.append(i)
    return tuple(out)


def not_start_set_for_paragraph(
    para: ParagraphSnapshot, document: DocumentSnapshot
) -> Optional[str]:
    """Return beginLine string for the paragraph, or None if unknown."""
    lang = (para.lang_asian or "").lower()
    if lang.startswith("ja") or _cjk_ratio(para.text) >= 0.35:
        key = None
        for cand in ("ja-JP", "ja_JP", "ja"):
            if cand in document.forbidden_by_locale:
                key = cand
                break
        if key is None:
            # fuzzy: any ja*
            for k in document.forbidden_by_locale:
                if k.lower().startswith("ja"):
                    key = k
                    break
        if key is not None:
            begin = document.forbidden_by_locale[key].get("begin")
            if begin is not None:
                return begin
        return DEFAULT_JA_NOT_START
    return None


def analyze_forbidden_rules_off(
    paragraphs: Sequence[ParagraphSnapshot],
) -> List[TypographyDiagnostic]:
    findings: List[TypographyDiagnostic] = []
    for para in paragraphs:
        if para.para_is_forbidden_rules is None:
            continue
        if para.para_is_forbidden_rules is True:
            continue
        if not _looks_japanese_context(para):
            continue
        findings.append(
            TypographyDiagnostic(
                rule_id=RULE_PARA_FORBIDDEN_OFF,
                category=CATEGORY_SETTING,
                severity=SEVERITY_INFO,
                message_key="diag.forbidden_rules_off",
                evidence="ParaIsForbiddenRules=false",
                affected=TextSpan(0, len(para.text), para.index),
                message_parameters={"paragraph_index": para.index},
            )
        )
    return findings


def _context_snippet(text: str, index: int, radius: int = 8) -> str:
    a = max(0, index - radius)
    b = min(len(text), index + radius + 1)
    snippet = text[a:b].replace("\n", "⏎")
    return snippet


def _is_decimal_dot(text: str, index: int) -> bool:
    """True for digit.digit (Western decimal), which we leave alone."""
    if index <= 0 or index + 1 >= len(text):
        return False
    return text[index - 1].isdigit() and text[index + 1].isdigit()


def analyze_mixed_width(
    paragraphs: Sequence[ParagraphSnapshot],
) -> List[TypographyDiagnostic]:
    """
    List every Western or halfwidth-JP punctuation occurrence in Japanese-
    dominant text when the matching fullwidth form is also used nearby
    (same paragraph) or when the mark is a halfwidth JP form / a Western
    stop used as Japanese sentence punctuation.
    """
    findings: List[TypographyDiagnostic] = []
    for para in paragraphs:
        text = para.body_text if para.body_text is not None else para.text
        if not text or not _looks_japanese_context(para):
            continue
        if _cjk_ratio(text) < 0.45:
            continue
        for role, full, forms in _PAIR_FORMS:
            has_full = full in text
            for ch, variant, label in forms:
                start = 0
                while True:
                    i = text.find(ch, start)
                    if i < 0:
                        break
                    start = i + 1
                    if len(findings) >= _MAX_PUNCT_OCCURRENCES:
                        return findings
                    # Skip URL-ish passages for Western marks only
                    if variant == "western" and _is_urlish(text):
                        continue
                    if ch == "." and _is_decimal_dot(text, i):
                        continue
                    # Western marks in a Latin-heavy local window are allowed
                    if variant == "western" and _latin_window_ratio(text, i) >= 0.35:
                        continue
                    # Halfwidth JP punct is always noteworthy in JP prose.
                    # Western punct: report when fullwidth counterpart is also
                    # present in this paragraph, OR when local context is JP
                    # (already gated by latin_window + cjk_ratio).
                    if variant == "western" and not has_full:
                        # Still report Western sentence punctuation in JP prose
                        # (e.g. 「月.」) — that is the common mock-text failure.
                        pass
                    if variant == "halfwidth_jp":
                        msg_key = "diag.halfwidth_punct"
                    elif has_full:
                        msg_key = "diag.mixed_width"
                    else:
                        msg_key = "diag.western_punct_in_jp"
                    code = "U+%04X" % ord(ch)
                    evidence = "%s %s (%s) at %d: …%s…" % (
                        label,
                        repr(ch),
                        code,
                        i,
                        _context_snippet(text, i),
                    )
                    if has_full:
                        evidence += " — also uses fullwidth %r" % full
                    findings.append(
                        TypographyDiagnostic(
                            rule_id=RULE_PUNCTUATION_MIXED_WIDTH,
                            category=CATEGORY_PUNCTUATION,
                            severity=SEVERITY_ADVISORY,
                            message_key=msg_key,
                            evidence=evidence,
                            affected=TextSpan(i, i + len(ch), para.index),
                            message_parameters={
                                "paragraph_index": para.index,
                                "full": full,
                                "char": ch,
                                "variant": variant,
                                "label": label,
                                "offset": i,
                            },
                        )
                    )
    return findings


def _following_grapheme(text: str, break_index: int) -> Tuple[str, int, int]:
    """
    Character (approx. code point) immediately after a soft break.
    Returns (char, start, end). Empty char if none.
    Does not normalize Unicode; skips additional soft-break chars.
    """
    i = break_index + 1
    while i < len(text) and text[i] in _SOFT_BREAK_CHARS:
        i += 1
    if i >= len(text):
        return "", i, i
    # Include a following VS if present (U+FE00–FE0F, U+E0100–E01EF surrogate pair).
    ch = text[i]
    j = i + 1
    if j < len(text):
        o = ord(text[j])
        if 0xFE00 <= o <= 0xFE0F:
            j += 1
    return text[i:j], i, j


def analyze_explicit_break_before_notstart(
    paragraphs: Sequence[ParagraphSnapshot],
    document: DocumentSnapshot,
) -> List[TypographyDiagnostic]:
    findings: List[TypographyDiagnostic] = []
    for para in paragraphs:
        if not _looks_japanese_context(para):
            continue
        begin = not_start_set_for_paragraph(para, document)
        if not begin:
            continue
        forbidden = set(begin)
        # Prefer recorded soft_break_offsets; else scan text.
        offsets = para.soft_break_offsets or find_soft_break_offsets(para.text)
        for off in offsets:
            if off < 0 or off >= len(para.text):
                continue
            if para.text[off] not in _SOFT_BREAK_CHARS:
                continue
            ch, a, b = _following_grapheme(para.text, off)
            if not ch:
                continue
            # First code point of the following cluster
            head = ch[0]
            if head not in forbidden:
                continue
            findings.append(
                TypographyDiagnostic(
                    rule_id=RULE_EXPLICIT_BREAK_BEFORE_NOTSTART,
                    category=CATEGORY_EXPLICIT_BREAK,
                    severity=SEVERITY_ADVISORY,
                    message_key="diag.explicit_break_notstart",
                    evidence="soft_break + %r" % ch,
                    affected=TextSpan(off, b, para.index),
                    message_parameters={
                        "paragraph_index": para.index,
                        "character": ch,
                    },
                )
            )
    return findings


def _bool_label(value: Optional[bool]) -> str:
    if value is None:
        return "unavailable"
    return "enabled" if value else "disabled"


def _compression_label(value: Optional[int]) -> str:
    if value is None:
        return "unavailable"
    return {
        0: "none",
        1: "punctuation_only",
        2: "punctuation_and_kana",
    }.get(int(value), "unavailable")


def compose_settings(
    paragraphs: Sequence[ParagraphSnapshot],
    document: DocumentSnapshot,
) -> List[SettingValue]:
    def _collect(attr: str) -> SettingValue:
        key = {
            "para_is_forbidden_rules": "kinsoku_rules",
            "para_is_hanging_punctuation": "hanging_punctuation",
            "para_is_character_distance": "asian_western_spacing",
        }[attr]
        vals = []
        for p in paragraphs:
            vals.append(getattr(p, attr))
        if not vals:
            return SettingValue(key, None, "unavailable")
        if any(v is None for v in vals):
            if all(v is None for v in vals):
                return SettingValue(key, None, "unavailable")
        known = [v for v in vals if v is not None]
        if not known:
            return SettingValue(key, None, "unavailable")
        if all(v is True for v in known) and len(known) == len(vals):
            return SettingValue(key, True, "enabled")
        if all(v is False for v in known) and len(known) == len(vals):
            return SettingValue(key, False, "disabled")
        # Mixed or partial unavailable
        on_n = sum(1 for v in vals if v is True)
        off_n = sum(1 for v in vals if v is False)
        unk_n = sum(1 for v in vals if v is None)
        detail = "on=%d off=%d unavailable=%d" % (on_n, off_n, unk_n)
        return SettingValue(key, "mixed", "mixed", mixed_detail=detail)

    settings = [
        _collect("para_is_forbidden_rules"),
        _collect("para_is_hanging_punctuation"),
        _collect("para_is_character_distance"),
        SettingValue(
            "punctuation_compression",
            document.character_compression_type,
            _compression_label(document.character_compression_type),
        ),
        SettingValue(
            "asian_punctuation_kerning",
            document.is_kern_asian_punctuation,
            _bool_label(document.is_kern_asian_punctuation),
        ),
    ]
    return settings


def run_inspection(scope: InspectionScope) -> InspectionReport:
    paras = list(scope.paragraphs)
    diagnostics: List[TypographyDiagnostic] = []
    diagnostics.extend(analyze_forbidden_rules_off(paras))
    diagnostics.extend(analyze_mixed_width(paras))
    diagnostics.extend(analyze_explicit_break_before_notstart(paras, scope.document))
    # Stable deterministic order
    order = {
        RULE_PARA_FORBIDDEN_OFF: 0,
        RULE_PUNCTUATION_MIXED_WIDTH: 1,
        RULE_EXPLICIT_BREAK_BEFORE_NOTSTART: 2,
    }
    diagnostics.sort(
        key=lambda d: (
            order.get(d.rule_id, 99),
            d.affected.paragraph_index if d.affected else 0,
            d.affected.start if d.affected else 0,
            d.rule_id,
        )
    )
    return InspectionReport(
        scope_kind=scope.selection_kind,
        paragraph_count=len(paras),
        settings=compose_settings(paras, scope.document),
        diagnostics=diagnostics,
        notes=list(scope.notes),
        limited_coverage=True,
    )
