# -*- coding: utf-8 -*-
"""
Tate-chū-yoko (縦中横) for LibreOffice Writer.

Native mechanism (LO Character → Position; confirmed vertical smoke):
  CharRotation = 900                 # 90° in tenths of a degree
  CharRotationIsFitToLine = True

Not CharCombineIsOn (that is warichū / text-combine=lines).
Not kumimoji. Not CSS text-combine-upright / Word’s dedicated feature.

Selection policy (marinaMoji usability — not a JLREQ hard limit):
  - Recommended: 2-grapheme digits, Latin, or a letter/digit mix (A4, 5G)
  - Extended: 3–4 grapheme digit/Latin/numeric → confirm override
  - Inappropriate Japanese / mixed prose / 5+ → refuse (no silent shrink)
  - Caret (no selection): detect an exact 2-grapheme digit/Latin run only
  - Horizontal writing: refuse new apply; remove still works
"""

from __future__ import annotations

import unicodedata

# CharRotation is tenths of a degree (UNO CharacterProperties).
_ROTATION_NONE = 0
_ROTATION_90 = 900
# com.sun.star.text.WritingMode2
_WM_LR_TB = 0
_WM_RL_TB = 1
_WM_TB_RL = 2
_WM_TB_LR = 3
_WM_PAGE = 4
_WM_CONTEXT = 5
_VERTICAL_WRITING_MODES = (_WM_TB_RL, _WM_TB_LR)
_HORIZONTAL_WRITING_MODES = (_WM_LR_TB, _WM_RL_TB)
_INHERITING_WRITING_MODES = (_WM_PAGE, _WM_CONTEXT)

# Verdicts from classify_selection / validate
OK = "ok"
CONFIRM = "confirm"
REFUSE = "refuse"

# Variation selectors treated as part of the preceding grapheme.
_VS_RANGES = (
    (0xFE00, 0xFE0F),
    (0xE0100, 0xE01EF),
)


def _is_vs(ch):
    o = ord(ch)
    return any(a <= o <= b for a, b in _VS_RANGES)


def iter_graphemes(text):
    """Yield user-perceived grapheme clusters (stdlib approximation).

    Groups combining marks and variation selectors with the base character.
    Does not rewrite or normalize the string.
    """
    if not text:
        return
    buf = []
    for ch in text:
        if buf and (unicodedata.combining(ch) or _is_vs(ch)):
            buf.append(ch)
            continue
        if buf:
            yield "".join(buf)
        buf = [ch]
    if buf:
        yield "".join(buf)


def grapheme_len(text):
    return sum(1 for _ in iter_graphemes(text))


def grapheme_list(text):
    return list(iter_graphemes(text))


def _is_ascii_digit(g):
    return len(g) >= 1 and "0" <= g[0] <= "9" and all(
        unicodedata.combining(c) or _is_vs(c) for c in g[1:]
    )


def _is_fullwidth_digit(g):
    if not g:
        return False
    o = ord(g[0])
    return 0xFF10 <= o <= 0xFF19 and all(
        unicodedata.combining(c) or _is_vs(c) for c in g[1:]
    )


def _is_digit_grapheme(g):
    return _is_ascii_digit(g) or _is_fullwidth_digit(g)


def _is_latin_grapheme(g):
    if not g:
        return False
    o = ord(g[0])
    if ("A" <= g[0] <= "Z") or ("a" <= g[0] <= "z"):
        return all(unicodedata.combining(c) or _is_vs(c) for c in g[1:])
    if 0xFF21 <= o <= 0xFF3A or 0xFF41 <= o <= 0xFF5A:
        return all(unicodedata.combining(c) or _is_vs(c) for c in g[1:])
    return False


def _is_numeric_extra(g):
    """Allowed inside extended numeric expressions (not alone as recommended)."""
    return g in (".", "%", ",", "．", "％", "，")


def _is_cjk_letter_grapheme(g):
    """Hiragana, katakana, or CJK ideograph — not conventional tate-chū-yoko."""
    if not g:
        return False
    o = ord(g[0])
    # Hiragana, Katakana, CJK Unified + Ext A common blocks (sufficient for policy).
    if 0x3040 <= o <= 0x309F:
        return True
    if 0x30A0 <= o <= 0x30FF:
        return True
    if 0x3400 <= o <= 0x9FFF:
        return True
    if 0xF900 <= o <= 0xFAFF:
        return True
    return False


def classify_run(text):
    """Classify a candidate run (already the intended span, not surrounding prose).

    Returns (kind, n) where kind is one of:
      digits | latin | alnum | numeric | japanese | mixed | empty | other
    and n is grapheme length. ``alnum`` is a digit/Latin mix with no
    punctuation (A4, 5G); ``numeric`` also allows . , %.
    """
    raw = text or ""
    # Keep internal spaces as disqualifying for recommended runs.
    if "\n" in raw or "\r" in raw:
        return "unsafe", grapheme_len(raw)
    clusters = grapheme_list(raw)
    n = len(clusters)
    if n == 0:
        return "empty", 0
    if any(_is_cjk_letter_grapheme(g) for g in clusters):
        return "japanese", n
    if all(_is_digit_grapheme(g) for g in clusters):
        return "digits", n
    if all(_is_latin_grapheme(g) for g in clusters):
        return "latin", n
    if all(_is_digit_grapheme(g) or _is_latin_grapheme(g) for g in clusters):
        return "alnum", n
    if all(
        _is_digit_grapheme(g) or _is_latin_grapheme(g) or _is_numeric_extra(g)
        for g in clusters
    ):
        # Must contain at least one digit for "numeric expression"
        if any(_is_digit_grapheme(g) for g in clusters):
            return "numeric", n
        return "mixed", n
    return "other", n


def classify_selection(text):
    """marinaMoji policy verdict for an explicit selection.

    Returns dict: verdict (ok|confirm|refuse), reason_key, kind, length, message_en
    """
    kind, n = classify_run(text)
    if kind == "empty":
        return _verdict(REFUSE, "empty", kind, n,
                        "Select a short number or letter sequence, or place the "
                        "cursor inside one.")
    if kind == "unsafe":
        return _verdict(REFUSE, "unsafe", kind, n,
                        "This selection crosses a line or paragraph break.")
    if kind == "japanese":
        return _verdict(
            REFUSE,
            "japanese",
            kind,
            n,
            "Tate-chū-yoko is intended for short horizontal sequences in "
            "vertical text. Select only the digits or letters to combine "
            "(for example `12` in `令和12年`), not the surrounding Japanese.",
        )
    if kind == "other" or kind == "mixed":
        return _verdict(
            REFUSE,
            "inappropriate",
            kind,
            n,
            "Tate-chū-yoko is intended for short horizontal sequences in "
            "vertical text. Select only the digits or letters to combine.",
        )
    if n == 1:
        return _verdict(
            REFUSE,
            "too_short",
            kind,
            n,
            "A single character is not conventional tate-chū-yoko. "
            "Select a short sequence such as two digits.",
        )
    if n == 2 and kind in ("digits", "latin", "alnum"):
        return _verdict(OK, "recommended", kind, n, "")
    if 3 <= n <= 4 and kind in ("digits", "latin", "alnum", "numeric"):
        return _verdict(
            CONFIRM,
            "extended",
            kind,
            n,
            "This selection is longer than a conventional two-character "
            "tate-chū-yoko. Characters may look compressed. Apply anyway?",
        )
    if n >= 5:
        return _verdict(
            REFUSE,
            "too_long",
            kind,
            n,
            "This selection is too long for conventional tate-chū-yoko. "
            "Try selecting a shorter sequence.",
        )
    return _verdict(
        REFUSE,
        "inappropriate",
        kind,
        n,
        "Tate-chū-yoko is intended for short horizontal sequences in "
        "vertical text. Select only the digits or letters to combine.",
    )


def _verdict(verdict, reason_key, kind, length, message_en):
    return {
        "verdict": verdict,
        "reason_key": reason_key,
        "kind": kind,
        "length": length,
        "message_en": message_en,
    }


def _is_digit_char(ch):
    o = ord(ch)
    return ("0" <= ch <= "9") or (0xFF10 <= o <= 0xFF19)


def _is_latin_char(ch):
    o = ord(ch)
    return (
        ("A" <= ch <= "Z")
        or ("a" <= ch <= "z")
        or (0xFF21 <= o <= 0xFF3A)
        or (0xFF41 <= o <= 0xFF5A)
    )


def _is_alnum_char(ch):
    return _is_digit_char(ch) or _is_latin_char(ch)


def find_recommended_run_at_caret(paragraph_text, caret_index):
    """Find an exact 2-character digit, Latin or letter/digit run at the caret.

    caret_index is a code-point offset (0..len). Does **not** pick a 2-digit
    slice out of a longer number (e.g. caret in `2026` → None).
    Returns (start, end) half-open code-point indices, or None.
    """
    s = paragraph_text or ""
    n = len(s)
    if n == 0:
        return None
    i = caret_index
    if i < 0 or i > n:
        return None

    def expand(pred):
        # Prefer character to the right of caret, else left.
        pos = i
        if pos < n and pred(s[pos]):
            pass
        elif pos > 0 and pred(s[pos - 1]):
            pos = pos - 1
        else:
            return None
        start = pos
        while start > 0 and pred(s[start - 1]):
            start -= 1
        end = pos + 1
        while end < n and pred(s[end]):
            end += 1
        return (start, end)

    for pred in (_is_digit_char, _is_latin_char, _is_alnum_char):
        span = expand(pred)
        if span is None:
            continue
        start, end = span
        run = s[start:end]
        # Exact length 2 in graphemes and code points for these repertoires.
        if grapheme_len(run) == 2 and (end - start) == 2:
            kind, _n = classify_run(run)
            if kind in ("digits", "latin", "alnum"):
                return (start, end)
    return None


def text_unchanged_after_tatechuyoko_change(before, after):
    return before == after


def expand_tatechuyoko_span_indices(flags, index):
    n = len(flags)
    if n == 0:
        return None
    if index < 0 or index > n:
        return None
    pos = index
    if pos == n:
        pos = n - 1
    elif pos < n and not flags[pos]:
        if pos > 0 and flags[pos - 1]:
            pos = pos - 1
        elif not flags[pos]:
            return None
    if not flags[pos]:
        return None
    start = pos
    while start > 0 and flags[start - 1]:
        start -= 1
    end = pos + 1
    while end < n and flags[end]:
        end += 1
    return (start, end)


# ---------------------------------------------------------------------------
# UNO / document helpers
# ---------------------------------------------------------------------------


def _get_document():
    try:
        doc = XSCRIPTCONTEXT.getDocument()  # noqa: F821
        if doc is not None and hasattr(doc, "Text"):
            return doc
    except NameError:
        pass
    import uno

    ctx = uno.getComponentContext()
    desktop = ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.frame.Desktop", ctx
    )
    doc = desktop.getCurrentComponent()
    if doc is None or not hasattr(doc, "Text"):
        raise RuntimeError("Open a Writer document first.")
    return doc


def _text_of(doc, text_range):
    """XText that contains text_range (table cell, footnote, frame, header…).

    ``doc.Text`` is the body text only; a cursor made from it cannot cover a
    range that lives in another text.
    """
    try:
        text = text_range.getText()
        if text is not None:
            return text
    except Exception:
        pass
    return doc.Text


def _range_text(text_range):
    if text_range is None:
        return ""
    try:
        return text_range.getString()
    except AttributeError:
        return ""


def _is_collapsed(text_range):
    if text_range is None:
        return True
    try:
        if hasattr(text_range, "isCollapsed"):
            return bool(text_range.isCollapsed())
    except Exception:
        pass
    return len(_range_text(text_range)) == 0


def _get_selection_range(doc, *, allow_collapsed=False):
    controller = doc.getCurrentController()
    if controller is None:
        return None
    sel = controller.getSelection()
    if sel is None:
        return None
    if hasattr(sel, "getString"):
        if len(_range_text(sel)) == 0 and not allow_collapsed:
            return None
        return sel
    try:
        count = sel.getCount()
    except AttributeError:
        return None
    if count < 1:
        return None
    first = sel.getByIndex(0)
    if count == 1:
        if len(_range_text(first)) == 0 and not allow_collapsed:
            return None
        return first
    last = sel.getByIndex(count - 1)
    text = _text_of(doc, first)
    merged = text.createTextCursorByRange(first.getStart())
    merged.gotoRange(last.getEnd(), True)
    if len(_range_text(merged)) == 0 and not allow_collapsed:
        return None
    return merged


def _message(doc, title, text, kind="warning"):
    try:
        from com.sun.star.awt.MessageBoxButtons import BUTTONS_OK
        from com.sun.star.awt.MessageBoxType import ERRORBOX, INFOBOX, WARNINGBOX

        box_type = {"info": INFOBOX, "error": ERRORBOX}.get(kind, WARNINGBOX)
        frame = doc.getCurrentController().getFrame()
        window = frame.getContainerWindow()
        toolkit = window.getToolkit()
        box = toolkit.createMessageBox(window, box_type, BUTTONS_OK, title, text)
        box.execute()
    except Exception:
        pass


def _confirm(doc, title, text):
    """Yes/No confirmation. Returns True if the user accepts."""
    try:
        from com.sun.star.awt.MessageBoxButtons import BUTTONS_YES_NO
        from com.sun.star.awt.MessageBoxResults import YES
        from com.sun.star.awt.MessageBoxType import QUERYBOX

        frame = doc.getCurrentController().getFrame()
        window = frame.getContainerWindow()
        toolkit = window.getToolkit()
        box = toolkit.createMessageBox(
            window, QUERYBOX, BUTTONS_YES_NO, title, text
        )
        return box.execute() == YES
    except Exception:
        # If the confirm UI fails, do not apply extended selections.
        return False


def _set(cursor, name, value):
    try:
        cursor.setPropertyValue(name, value)
        return True
    except Exception:
        return False


def _get(cursor, name, default=None):
    try:
        return cursor.getPropertyValue(name)
    except Exception:
        return default


def _rotation_of(cursor):
    val = _get(cursor, "CharRotation", _ROTATION_NONE)
    if val is None or (isinstance(val, dict) and "error" in val):
        return _ROTATION_NONE
    try:
        return int(val)
    except (TypeError, ValueError):
        return _ROTATION_NONE


def _fit_of(cursor):
    return _get(cursor, "CharRotationIsFitToLine", False) is True


def _has_tatechuyoko(cursor):
    return _rotation_of(cursor) == _ROTATION_90 and _fit_of(cursor)


def selection_has_tatechuyoko(selection):
    return _has_tatechuyoko(selection)


def _selection_has_warichu(cursor):
    return _get(cursor, "CharCombineIsOn", False) is True


def _selection_has_ruby(cursor):
    val = _get(cursor, "RubyText", "")
    if val is None or (isinstance(val, dict) and "error" in val):
        return False
    return bool(str(val))


def resolve_is_vertical(paragraph_wm, page_wm):
    """Pure helper: decide vertical writing from paragraph + page WritingMode2.

    marinaMoji’s “Toggle vertical page” sets the *page* style. Paragraphs often
    keep LR_TB (0) or PAGE/CONTEXT in the API even when the page is vertical.
    Trust an explicit vertical paragraph, otherwise trust the page.
    """
    try:
        pwm = int(paragraph_wm) if paragraph_wm is not None else None
    except (TypeError, ValueError):
        pwm = None
    try:
        page = int(page_wm) if page_wm is not None else None
    except (TypeError, ValueError):
        page = None

    if pwm in _VERTICAL_WRITING_MODES:
        return True
    if page in _VERTICAL_WRITING_MODES:
        # Page is vertical — do not let a stale/default LR_TB on the paragraph
        # produce a false “horizontal” alert.
        return True
    if pwm in _HORIZONTAL_WRITING_MODES:
        return False
    if page in _HORIZONTAL_WRITING_MODES:
        return False
    return False


def _page_writing_mode(doc, text_range):
    """WritingMode of the page style that contains text_range (or the view)."""
    name = None
    try:
        cursor = _text_of(doc, text_range).createTextCursorByRange(text_range.getStart())
        name = cursor.getPropertyValue("PageStyleName")
    except Exception:
        name = None
    if not name:
        try:
            name = doc.getCurrentController().getViewCursor().getPropertyValue(
                "PageStyleName"
            )
        except Exception:
            name = None
    if not name:
        return None
    try:
        page = doc.getStyleFamilies().getByName("PageStyles").getByName(name)
        return page.getPropertyValue("WritingMode")
    except Exception:
        return None


def _paragraph_writing_mode(doc, text_range):
    try:
        cursor = _text_of(doc, text_range).createTextCursorByRange(text_range.getStart())
        return cursor.getPropertyValue("WritingMode")
    except Exception:
        return None


def _paragraph_is_vertical(doc, text_range):
    """True when page or paragraph is vertical writing."""
    return resolve_is_vertical(
        _paragraph_writing_mode(doc, text_range),
        _page_writing_mode(doc, text_range),
    )


def _paragraph_text_and_offset(doc, text_range):
    """Return (paragraph_string, caret_offset_in_paragraph) for a collapsed range."""
    text = _text_of(doc, text_range)
    para = text.createTextCursorByRange(text_range.getStart())
    para.gotoStartOfParagraph(False)
    para_start = text.createTextCursorByRange(para.getStart())
    para_start.collapseToStart()
    para.gotoEndOfParagraph(True)
    para_text = _range_text(para)
    caret = text.createTextCursorByRange(text_range.getStart())
    caret.collapseToStart()
    measure = text.createTextCursorByRange(para_start.getStart())
    measure.collapseToStart()
    measure.gotoRange(caret.getStart(), True)
    offset = len(_range_text(measure))
    return para_text, offset


def _cursor_for_paragraph_slice(doc, text_range, start, end):
    """Build a cursor covering [start, end) code points in the paragraph of text_range."""
    text = _text_of(doc, text_range)
    para_start = text.createTextCursorByRange(text_range.getStart())
    para_start.gotoStartOfParagraph(False)
    para_start.collapseToStart()
    span = text.createTextCursorByRange(para_start.getStart())
    span.collapseToStart()
    if start:
        span.goRight(start, False)
    span.goRight(max(0, end - start), True)
    return span


def _anchor_inside_tatechuyoko(text, text_range):
    cursor = text.createTextCursorByRange(text_range.getStart())
    cursor.collapseToStart()

    right = text.createTextCursorByRange(cursor.getStart())
    if right.goRight(1, True) and _has_tatechuyoko(right):
        right.collapseToStart()
        return right

    left = text.createTextCursorByRange(cursor.getStart())
    if left.goLeft(1, True) and _has_tatechuyoko(left):
        left.collapseToStart()
        return left

    if not _is_collapsed(text_range) and _has_tatechuyoko(text_range):
        mid = text.createTextCursorByRange(text_range.getStart())
        mid.collapseToStart()
        return mid
    return None


def expand_to_tatechuyoko_span(text, text_range):
    if text_range is None:
        return None
    anchor = _anchor_inside_tatechuyoko(text, text_range)
    if anchor is None:
        return None

    start = text.createTextCursorByRange(anchor.getStart())
    start.collapseToStart()
    while True:
        probe = text.createTextCursorByRange(start.getStart())
        if not probe.goLeft(1, False):
            break
        check = text.createTextCursorByRange(probe.getStart())
        if not check.goRight(1, True) or not _has_tatechuyoko(check):
            break
        start.gotoRange(probe.getStart(), False)
        start.collapseToStart()

    span = text.createTextCursorByRange(start.getStart())
    span.collapseToStart()
    included = 0
    while True:
        check = text.createTextCursorByRange(start.getStart())
        if included:
            check.goRight(included, False)
        if not check.goRight(1, True) or not _has_tatechuyoko(check):
            break
        included += 1
    if included == 0:
        return None
    span.goRight(included, True)
    return span


def _apply_tatechuyoko(cursor):
    ok_rot = _set(cursor, "CharRotation", _ROTATION_90)
    ok_fit = _set(cursor, "CharRotationIsFitToLine", True)
    return ok_rot and ok_fit


def _clear_tatechuyoko(cursor):
    _set(cursor, "CharRotation", _ROTATION_NONE)
    _set(cursor, "CharRotationIsFitToLine", False)


def _resolve_apply_target(doc):
    """Return (cursor, source) or (None, reason_message).

    source is 'selection' or 'caret'.
    """
    selection = _get_selection_range(doc, allow_collapsed=True)
    if selection is None:
        return None, (
            "Select a short number or letter sequence, or place the "
            "cursor inside one."
        )

    if _is_collapsed(selection):
        # Prefer remove target detection is separate; here detect 2-char run.
        para_text, offset = _paragraph_text_and_offset(doc, selection)
        found = find_recommended_run_at_caret(para_text, offset)
        if found is None:
            return None, (
                "Select a short number or letter sequence, or place the "
                "cursor inside one."
            )
        start, end = found
        cursor = _cursor_for_paragraph_slice(doc, selection, start, end)
        return cursor, "caret"

    cursor = _text_of(doc, selection).createTextCursorByRange(selection)
    return cursor, "selection"


def apply_tatechuyoko(*_args):
    """Toolbar: validate then apply 90° + fit-to-line."""
    try:
        doc = _get_document()
    except RuntimeError:
        return

    target, meta = _resolve_apply_target(doc)
    if target is None:
        _message(doc, "marinaMoji tate-chū-yoko", meta, kind="info")
        return

    if not _paragraph_is_vertical(doc, target):
        _message(
            doc,
            "marinaMoji tate-chū-yoko",
            "Tate-chū-yoko is intended for vertical writing.",
            kind="info",
        )
        return

    if _selection_has_warichu(target):
        _message(
            doc,
            "marinaMoji tate-chū-yoko",
            "This selection overlaps an existing annotation. "
            "Adjust the selection before applying tate-chū-yoko.",
            kind="warning",
        )
        return

    if _selection_has_ruby(target):
        _message(
            doc,
            "marinaMoji tate-chū-yoko",
            "This selection overlaps an existing annotation. "
            "Adjust the selection before applying tate-chū-yoko.",
            kind="warning",
        )
        return

    base = _range_text(target)
    decision = classify_selection(base)
    if decision["verdict"] == REFUSE:
        _message(
            doc,
            "marinaMoji tate-chū-yoko",
            decision["message_en"],
            kind="info",
        )
        return
    if decision["verdict"] == CONFIRM:
        if not _confirm(
            doc,
            "marinaMoji tate-chū-yoko",
            decision["message_en"],
        ):
            return

    before = _range_text(target)
    if not _apply_tatechuyoko(target):
        _message(
            doc,
            "marinaMoji tate-chū-yoko",
            "Could not apply tate-chū-yoko on this selection.\n"
            "Enable Asian language support if it is off.",
            kind="error",
        )
        return
    after = _range_text(target)
    if after != before:
        _message(
            doc,
            "marinaMoji tate-chū-yoko",
            "Apply changed the underlying text unexpectedly. "
            "Please undo and report this.",
            kind="error",
        )
        return
    try:
        doc.getCurrentController().select(target)
    except Exception:
        pass


def remove_tatechuyoko(*_args):
    """Toolbar: clear 90°+fit; works in any writing direction."""
    try:
        doc = _get_document()
    except RuntimeError:
        return
    selection = _get_selection_range(doc, allow_collapsed=True)
    if selection is None:
        _message(
            doc,
            "marinaMoji tate-chū-yoko",
            "Place the cursor inside 縦中横 text, or select it, then remove.",
            kind="info",
        )
        return

    text = _text_of(doc, selection)
    span = expand_to_tatechuyoko_span(text, selection)
    if span is None:
        if not _is_collapsed(selection) and selection_has_tatechuyoko(selection):
            span = text.createTextCursorByRange(selection)
        else:
            _message(
                doc,
                "marinaMoji tate-chū-yoko",
                "No tate-chū-yoko found at the cursor.",
                kind="info",
            )
            return

    before = _range_text(span)
    _clear_tatechuyoko(span)
    after = _range_text(span)
    if after != before:
        _message(
            doc,
            "marinaMoji tate-chū-yoko",
            "Remove changed the underlying text unexpectedly. "
            "Please undo and report this.",
            kind="error",
        )
        return
    try:
        doc.getCurrentController().select(span)
    except Exception:
        pass
