# -*- coding: utf-8 -*-
"""
LibreOffice Writer adapter — Japanese Typography Inspector (Stage E2).

Read-only: never writes properties, text, metadata, or preferences.
"""

from __future__ import annotations

import sys
import traceback

try:
    import typography_analysis as _analysis
except ImportError:
    _analysis = None

# ---------------------------------------------------------------------------
# Localization (en / ja / fr)
# ---------------------------------------------------------------------------

_STRINGS = {
    "en": {
        "command_title": "Inspect Japanese Typography",
        "report_title": "Japanese Typography",
        "scope_caret": "Current paragraph",
        "scope_single": "Selected passage (one paragraph)",
        "scope_multi": "Selected passage ({n} paragraphs)",
        "scope_unsupported": "Unsupported selection",
        "section_settings": "Composition settings",
        "section_issues": "Potential issues",
        "kinsoku_rules": "Kinsoku rules",
        "hanging_punctuation": "Hanging punctuation",
        "asian_western_spacing": "Asian–Western spacing",
        "punctuation_compression": "Punctuation compression",
        "asian_punctuation_kerning": "Asian punctuation kerning",
        "enabled": "Enabled",
        "disabled": "Disabled",
        "mixed": "Mixed",
        "unavailable": "Unavailable",
        "none": "None",
        "punctuation_only": "Punctuation only",
        "punctuation_and_kana": "Punctuation and kana",
        "no_issues": "No potential issues were found by the current inspection rules.",
        "limited": "This inspection does not check automatic line wrapping or full JLREQ compliance.",
        "readonly": "No changes made to the document.",
        "advisory_n": "{n} advisory",
        "advisory_n_plural": "{n} advisories",
        "info_n": "{n} informational",
        "diag.forbidden_rules_off": (
            "Japanese line-breaking restrictions are disabled for this paragraph. "
            "This may be intentional."
        ),
        "diag.mixed_width": (
            "Western or halfwidth punctuation appears where fullwidth Japanese "
            "punctuation is also used. Check whether intentional."
        ),
        "diag.halfwidth_punct": (
            "Halfwidth Japanese punctuation in Japanese text. "
            "Check whether intentional."
        ),
        "diag.western_punct_in_jp": (
            "Western punctuation in Japanese text. "
            "Check whether intentional."
        ),
        "diag.explicit_break_notstart": (
            "An explicit line break is followed by a character that is normally "
            "avoided at the start of a Japanese line."
        ),
        "err_no_doc": "Open a Writer document first.",
        "err_scope": "This selection cannot be inspected reliably in the current version.",
        "err_analysis": "Inspection module unavailable.",
        "close": "Close",
        "severity_information": "Information",
        "severity_advisory": "Advisory",
        "severity_warning": "Warning",
    },
    "ja": {
        "command_title": "日本語組版を点検",
        "report_title": "日本語組版",
        "scope_caret": "現在の段落",
        "scope_single": "選択範囲（1段落）",
        "scope_multi": "選択範囲（{n}段落）",
        "scope_unsupported": "未対応の選択範囲",
        "section_settings": "組版設定",
        "section_issues": "留意事項",
        "kinsoku_rules": "禁則処理",
        "hanging_punctuation": "ぶら下げ組み",
        "asian_western_spacing": "和欧間隔",
        "punctuation_compression": "約物の詰め",
        "asian_punctuation_kerning": "約物のカーニング",
        "enabled": "有効",
        "disabled": "無効",
        "mixed": "混在",
        "unavailable": "取得不可",
        "none": "なし",
        "punctuation_only": "約物のみ",
        "punctuation_and_kana": "約物と仮名",
        "no_issues": "現在の点検規則では、留意事項は見つかりませんでした。",
        "limited": "この点検は自動折り返しや JLREQ 全体の適合を判定しません。",
        "readonly": "文書は変更していません。",
        "advisory_n": "助言 {n} 件",
        "advisory_n_plural": "助言 {n} 件",
        "info_n": "参考 {n} 件",
        "diag.forbidden_rules_off": (
            "この段落では日本語の行頭・行末禁則が無効です。意図的な場合があります。"
        ),
        "diag.mixed_width": (
            "全角の日本語約物がある一方で、半角や欧文の約物も使われています。意図的か確認してください。"
        ),
        "diag.halfwidth_punct": (
            "日本語の文に半角の日本語約物があります。意図的か確認してください。"
        ),
        "diag.western_punct_in_jp": (
            "日本語の文に欧文約物があります。意図的か確認してください。"
        ),
        "diag.explicit_break_notstart": (
            "明示的な改行の直後に、通常は行頭に置かない文字が続いています。"
        ),
        "err_no_doc": "先に Writer 文書を開いてください。",
        "err_scope": "この選択範囲は、現状の点検では扱えません。",
        "err_analysis": "点検モジュールを読み込めません。",
        "close": "閉じる",
        "severity_information": "参考",
        "severity_advisory": "助言",
        "severity_warning": "警告",
    },
    "fr": {
        "command_title": "Vérifier la typographie japonaise",
        "report_title": "Typographie japonaise",
        "scope_caret": "Paragraphe courant",
        "scope_single": "Passage sélectionné (un paragraphe)",
        "scope_multi": "Passage sélectionné ({n} paragraphes)",
        "scope_unsupported": "Sélection non prise en charge",
        "section_settings": "Réglages de composition",
        "section_issues": "Points d’attention",
        "kinsoku_rules": "Règles de coupure japonaise",
        "hanging_punctuation": "Ponctuation suspendue",
        "asian_western_spacing": "Espacement asiatique–occidental",
        "punctuation_compression": "Compression de la ponctuation",
        "asian_punctuation_kerning": "Crénage de la ponctuation asiatique",
        "enabled": "Activé",
        "disabled": "Désactivé",
        "mixed": "Mixte",
        "unavailable": "Indisponible",
        "none": "Aucune",
        "punctuation_only": "Ponctuation seulement",
        "punctuation_and_kana": "Ponctuation et kana",
        "no_issues": (
            "Aucun point d’attention n’a été trouvé avec les règles "
            "d’inspection actuelles."
        ),
        "limited": (
            "Cette inspection ne vérifie pas les coupures automatiques "
            "ni la conformité JLREQ complète."
        ),
        "readonly": "Aucun changement n’a été apporté au document.",
        "advisory_n": "{n} avis",
        "advisory_n_plural": "{n} avis",
        "info_n": "{n} information",
        "diag.forbidden_rules_off": (
            "Les restrictions de coupure japonaise sont désactivées pour ce "
            "paragraphe. Cela peut être intentionnel."
        ),
        "diag.mixed_width": (
            "De la ponctuation occidentale ou demi-chasse apparaît là où la "
            "ponctuation japonaise pleine chasse est aussi utilisée. "
            "Vérifiez si c’est intentionnel."
        ),
        "diag.halfwidth_punct": (
            "Ponctuation japonaise demi-chasse dans un texte japonais. "
            "Vérifiez si c’est intentionnel."
        ),
        "diag.western_punct_in_jp": (
            "Ponctuation occidentale dans un texte japonais. "
            "Vérifiez si c’est intentionnel."
        ),
        "diag.explicit_break_notstart": (
            "Un saut de ligne explicite est suivi d’un caractère généralement "
            "évité en début de ligne japonaise."
        ),
        "err_no_doc": "Ouvrez d’abord un document Writer.",
        "err_scope": "Cette sélection ne peut pas être inspectée de façon fiable.",
        "err_analysis": "Module d’inspection indisponible.",
        "close": "Fermer",
        "severity_information": "Information",
        "severity_advisory": "Avis",
        "severity_warning": "Avertissement",
    },
}


def _ui_lang(doc=None) -> str:
    """Best-effort UI language: ja / fr / en."""
    try:
        import uno

        ctx = uno.getComponentContext()
        cfg = ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.configuration.ConfigurationProvider", ctx
        )
        from com.sun.star.beans import PropertyValue

        arg = PropertyValue()
        arg.Name = "nodepath"
        arg.Value = "/org.openoffice.Setup/L10N"
        access = cfg.createInstanceWithArguments(
            "com.sun.star.configuration.ConfigurationAccess", (arg,)
        )
        locale = str(access.getByName("ooLocale") or "")
        low = locale.lower()
        if low.startswith("ja"):
            return "ja"
        if low.startswith("fr"):
            return "fr"
    except Exception:
        pass
    return "en"


def _t(lang: str, key: str, **kwargs) -> str:
    table = _STRINGS.get(lang) or _STRINGS["en"]
    text = table.get(key) or _STRINGS["en"].get(key) or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text


# ---------------------------------------------------------------------------
# Document / selection helpers
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
        raise RuntimeError("no_doc")
    return doc


def _get_prop(obj, name, default=None):
    try:
        return obj.getPropertyValue(name)
    except Exception:
        return default


def _get_prop_state(obj, name) -> str:
    try:
        state = obj.getPropertyState(name)
        # PropertyState: DIRECT_VALUE=0, DEFAULT_VALUE=1, AMBIGUOUS_VALUE=2
        try:
            val = int(state)
        except Exception:
            val = state
        if val == 0:
            return "direct"
        if val == 1:
            return "default"
        if val == 2:
            return "ambiguous"
        return "unknown"
    except Exception:
        return "unknown"


def _locale_tag(locale):
    if locale is None:
        return None
    try:
        lang = str(getattr(locale, "Language", "") or "")
        country = str(getattr(locale, "Country", "") or "")
        if lang and country:
            return "%s-%s" % (lang, country)
        return lang or None
    except Exception:
        return None


def _read_document_settings(doc) -> "_analysis.DocumentSnapshot":
    snap = _analysis.DocumentSnapshot()
    # DocumentSettings service
    settings = None
    try:
        settings = doc.createInstance("com.sun.star.document.Settings")
    except Exception:
        settings = None
    if settings is None:
        settings = doc

    for name, attr, cast in (
        ("CharacterCompressionType", "character_compression_type", int),
        ("IsKernAsianPunctuation", "is_kern_asian_punctuation", bool),
    ):
        raw = _get_prop(settings, name, None)
        if raw is None and settings is not doc:
            raw = _get_prop(doc, name, None)
        if raw is None:
            setattr(snap, attr, None)
            continue
        try:
            setattr(snap, attr, cast(raw))
        except Exception:
            setattr(snap, attr, None)

    # ForbiddenCharacters (document table, else locale defaults via XLocaleData)
    xfc = _get_prop(settings, "ForbiddenCharacters", None)
    if xfc is None and settings is not doc:
        xfc = _get_prop(doc, "ForbiddenCharacters", None)
    locales_to_try = []
    try:
        from com.sun.star.lang import Locale

        locales_to_try = [
            Locale("ja", "JP", ""),
            Locale("ja", "", ""),
        ]
    except Exception:
        locales_to_try = []
    for loc in locales_to_try:
        tag = _locale_tag(loc) or "ja-JP"
        chars = None
        if xfc is not None:
            try:
                chars = xfc.getForbiddenCharacters(loc)
            except Exception:
                chars = None
        if chars is None:
            try:
                import uno

                ctx = uno.getComponentContext()
                locale_data = ctx.ServiceManager.createInstanceWithContext(
                    "com.sun.star.i18n.LocaleData", ctx
                )
                chars = locale_data.getForbiddenCharacters(loc)
            except Exception:
                chars = None
        if chars is None:
            continue
        snap.forbidden_by_locale[tag] = {
            "begin": str(getattr(chars, "beginLine", "") or ""),
            "end": str(getattr(chars, "endLine", "") or ""),
        }
    return snap


def _ranges_overlap(text, a, b) -> bool:
    """True if text ranges a and b overlap (XTextRangeCompare)."""
    try:
        # start(a) <= end(b) and start(b) <= end(a)
        return (
            text.compareRegionStarts(a, b.getEnd()) <= 0
            and text.compareRegionStarts(b, a.getEnd()) <= 0
        )
    except Exception:
        return False


def _enum_paragraphs_in_range(text, text_range):
    """Yield (paragraph cursor, index) for body paragraphs intersecting text_range."""
    enum = text.createEnumeration()
    idx = 0
    while enum.hasMoreElements():
        para = enum.nextElement()
        try:
            cursor = text.createTextCursorByRange(para)
        except Exception:
            idx += 1
            continue
        if _ranges_overlap(text, cursor, text_range):
            yield cursor, idx
        idx += 1


def _paragraph_cursor_at_caret(doc, selection):
    text = doc.Text
    cursor = text.createTextCursorByRange(selection)
    cursor.gotoStartOfParagraph(False)
    cursor.gotoEndOfParagraph(True)
    return cursor


def _is_collapsed(text_range) -> bool:
    try:
        if hasattr(text_range, "isCollapsed"):
            return bool(text_range.isCollapsed())
    except Exception:
        pass
    try:
        return text_range.getString() == ""
    except Exception:
        return True


def _selection_spans_multiple_text_objects(selection) -> bool:
    try:
        if hasattr(selection, "getCount") and selection.getCount() > 1:
            return True
    except Exception:
        pass
    return False


def _lang_from_cursor(cursor) -> tuple:
    asian = None
    western = None
    for prop, slot in (("CharLocaleAsian", "asian"), ("CharLocale", "western")):
        loc = _get_prop(cursor, prop, None)
        tag = _locale_tag(loc)
        if slot == "asian":
            asian = tag
        else:
            western = tag
    return asian, western


def _annotation_flags(cursor) -> dict:
    """Presence flags only — inspection does not interpret annotation contents."""
    flags = {"has_ruby": False, "has_warichu": False, "has_tatechuyoko": False}
    try:
        ruby = _get_prop(cursor, "RubyText", "") or ""
        if str(ruby).strip():
            flags["has_ruby"] = True
    except Exception:
        pass
    try:
        if bool(_get_prop(cursor, "CharCombineIsOn", False)):
            flags["has_warichu"] = True
    except Exception:
        pass
    try:
        if int(_get_prop(cursor, "CharRotation", 0) or 0) != 0:
            flags["has_tatechuyoko"] = True
    except Exception:
        pass
    # Light portion sample (step by run) for mixed formatting inside the paragraph
    try:
        text = cursor.getText()
        probe = text.createTextCursorByRange(cursor)
        probe.collapseToStart()
        end = cursor.getEnd()
        for _ in range(400):
            try:
                if text.compareRegionStarts(probe, end) >= 0:
                    break
            except Exception:
                break
            try:
                if str(_get_prop(probe, "RubyText", "") or "").strip():
                    flags["has_ruby"] = True
            except Exception:
                pass
            try:
                if bool(_get_prop(probe, "CharCombineIsOn", False)):
                    flags["has_warichu"] = True
            except Exception:
                pass
            try:
                if int(_get_prop(probe, "CharRotation", 0) or 0) != 0:
                    flags["has_tatechuyoko"] = True
            except Exception:
                pass
            # Advance by formatting run when possible
            moved = False
            try:
                moved = bool(probe.gotoEndOfSentence(False))
            except Exception:
                moved = False
            if not moved:
                if not probe.goRight(1, False):
                    break
    except Exception:
        pass
    return flags


def _body_text_excluding_ruby_readings(para_text: str, has_ruby: bool) -> str:
    """
    getString() on Writer paragraphs returns base text, not ruby readings,
    for ordinary RubyText annotations. Keep as-is; flag presence separately.
    """
    return para_text


def _snapshot_paragraph(cursor, index: int):
    text = ""
    try:
        text = cursor.getString() or ""
    except Exception:
        text = ""
    soft = _analysis.find_soft_break_offsets(text)
    asian, western = _lang_from_cursor(cursor)
    flags = _annotation_flags(cursor)

    def _bool_prop(name):
        raw = _get_prop(cursor, name, None)
        if raw is None:
            return None
        return bool(raw)

    return _analysis.ParagraphSnapshot(
        index=index,
        text=text,
        para_is_forbidden_rules=_bool_prop("ParaIsForbiddenRules"),
        para_is_hanging_punctuation=_bool_prop("ParaIsHangingPunctuation"),
        para_is_character_distance=_bool_prop("ParaIsCharacterDistance"),
        forbidden_rules_state=_get_prop_state(cursor, "ParaIsForbiddenRules"),
        hanging_state=_get_prop_state(cursor, "ParaIsHangingPunctuation"),
        distance_state=_get_prop_state(cursor, "ParaIsCharacterDistance"),
        lang_asian=asian,
        lang_western=western,
        soft_break_offsets=soft,
        has_ruby=flags["has_ruby"],
        has_warichu=flags["has_warichu"],
        has_tatechuyoko=flags["has_tatechuyoko"],
        body_text=_body_text_excluding_ruby_readings(text, flags["has_ruby"]),
    )


def extract_scope(doc) -> "_analysis.InspectionScope":
    """Build InspectionScope without modifying the document."""
    notes = []
    controller = doc.getCurrentController()
    selection = controller.getSelection()
    if selection is None:
        return _analysis.InspectionScope(
            selection_kind="unsupported", notes=["no_selection"]
        )

    if _selection_spans_multiple_text_objects(selection):
        return _analysis.InspectionScope(
            selection_kind="unsupported",
            notes=["multi_object_selection"],
        )

    try:
        text_range = selection.getByIndex(0) if hasattr(selection, "getByIndex") else selection
    except Exception:
        text_range = selection

    text = doc.Text
    document_snap = _read_document_settings(doc)

    if _is_collapsed(text_range):
        cursor = _paragraph_cursor_at_caret(doc, text_range)
        para = _snapshot_paragraph(cursor, 0)
        return _analysis.InspectionScope(
            selection_kind="caret_paragraph",
            paragraphs=[para],
            document=document_snap,
            notes=notes,
        )

    # Non-collapsed: collect intersecting paragraphs
    paragraphs = []
    try:
        for cursor, idx in _enum_paragraphs_in_range(text, text_range):
            # Expand cursor to full paragraph for settings (effective para props)
            full = text.createTextCursorByRange(cursor)
            full.gotoStartOfParagraph(False)
            full.gotoEndOfParagraph(True)
            paragraphs.append(_snapshot_paragraph(full, len(paragraphs)))
    except Exception as exc:
        notes.append("enum_failed:%s" % type(exc).__name__)
        # Fallback: treat selection's paragraph only
        cursor = _paragraph_cursor_at_caret(doc, text_range)
        paragraphs = [_snapshot_paragraph(cursor, 0)]

    if not paragraphs:
        cursor = _paragraph_cursor_at_caret(doc, text_range)
        paragraphs = [_snapshot_paragraph(cursor, 0)]

    kind = "selection_single" if len(paragraphs) == 1 else "selection_multi"
    # For single-paragraph selection, analyze selected substring for textual rules
    # but keep paragraph-level settings from the full paragraph.
    if kind == "selection_single":
        try:
            selected = text_range.getString() or ""
            if selected and paragraphs:
                p0 = paragraphs[0]
                paragraphs[0] = _analysis.ParagraphSnapshot(
                    index=p0.index,
                    text=selected,
                    para_is_forbidden_rules=p0.para_is_forbidden_rules,
                    para_is_hanging_punctuation=p0.para_is_hanging_punctuation,
                    para_is_character_distance=p0.para_is_character_distance,
                    forbidden_rules_state=p0.forbidden_rules_state,
                    hanging_state=p0.hanging_state,
                    distance_state=p0.distance_state,
                    lang_asian=p0.lang_asian,
                    lang_western=p0.lang_western,
                    soft_break_offsets=_analysis.find_soft_break_offsets(selected),
                    has_ruby=p0.has_ruby,
                    has_warichu=p0.has_warichu,
                    has_tatechuyoko=p0.has_tatechuyoko,
                    body_text=selected,
                )
        except Exception:
            pass

    return _analysis.InspectionScope(
        selection_kind=kind,
        paragraphs=paragraphs,
        document=document_snap,
        notes=notes,
    )


# ---------------------------------------------------------------------------
# Report formatting + UI
# ---------------------------------------------------------------------------


def format_report(report, lang: str) -> str:
    lines = []
    lines.append(_t(lang, "report_title"))
    if report.scope_kind == "caret_paragraph":
        lines.append(_t(lang, "scope_caret"))
    elif report.scope_kind == "selection_single":
        lines.append(_t(lang, "scope_single"))
    elif report.scope_kind == "selection_multi":
        lines.append(_t(lang, "scope_multi", n=report.paragraph_count))
    else:
        lines.append(_t(lang, "scope_unsupported"))
    lines.append("")
    lines.append(_t(lang, "section_settings").upper())
    lines.append("")

    key_map = {
        "kinsoku_rules": "kinsoku_rules",
        "hanging_punctuation": "hanging_punctuation",
        "asian_western_spacing": "asian_western_spacing",
        "punctuation_compression": "punctuation_compression",
        "asian_punctuation_kerning": "asian_punctuation_kerning",
    }
    for setting in report.settings:
        label = _t(lang, key_map.get(setting.key, setting.key))
        display_key = setting.display
        value = _t(lang, display_key) if display_key in _STRINGS["en"] else display_key
        if setting.display == "mixed" and setting.mixed_detail:
            value = "%s (%s)" % (_t(lang, "mixed"), setting.mixed_detail)
        # pad label
        lines.append("%-28s %s" % (label, value))

    lines.append("")
    lines.append(_t(lang, "section_issues").upper())
    lines.append("")

    if not report.diagnostics:
        lines.append(_t(lang, "no_issues"))
    else:
        adv = sum(1 for d in report.diagnostics if d.severity == _analysis.SEVERITY_ADVISORY)
        info = sum(1 for d in report.diagnostics if d.severity == _analysis.SEVERITY_INFO)
        summary_bits = []
        if adv:
            key = "advisory_n_plural" if adv != 1 else "advisory_n"
            summary_bits.append(_t(lang, key, n=adv))
        if info:
            summary_bits.append(_t(lang, "info_n", n=info))
        if summary_bits:
            lines.append(", ".join(summary_bits))
            lines.append("")
        for i, diag in enumerate(report.diagnostics, 1):
            sev = _t(lang, "severity_%s" % diag.severity)
            msg = _t(lang, diag.message_key)
            lines.append("%d. [%s] %s" % (i, sev, msg))
            if diag.evidence:
                lines.append("   · %s" % diag.evidence)
            lines.append("")

    lines.append("────────────────────────────────────────")
    lines.append(_t(lang, "limited"))
    lines.append(_t(lang, "readonly"))
    return "\n".join(lines).rstrip() + "\n"


def _show_report_dialog(doc, title: str, body: str, lang: str) -> None:
    import uno

    try:
        ctx = uno.getComponentContext()
        smgr = ctx.ServiceManager
        dialog_model = smgr.createInstanceWithContext(
            "com.sun.star.awt.UnoControlDialogModel", ctx
        )
        dialog_model.Title = title
        dialog_model.Width = 280
        dialog_model.Height = 250
        dialog_model.Closeable = True

        def _insert(name, service, **props):
            m = dialog_model.createInstance(
                "com.sun.star.awt.UnoControl%sModel" % service
            )
            m.Name = name
            for k, v in props.items():
                setattr(m, k, v)
            dialog_model.insertByName(name, m)

        _insert(
            "report",
            "Edit",
            PositionX=8,
            PositionY=6,
            Width=264,
            Height=218,
            MultiLine=True,
            ReadOnly=True,
            VScroll=True,
            HScroll=False,
            AutoVScroll=True,
            Text=body,
        )
        _insert(
            "close",
            "Button",
            PositionX=220,
            PositionY=230,
            Width=52,
            Height=14,
            Label=_t(lang, "close"),
            PushButtonType=2,
            DefaultButton=True,
        )

        control = smgr.createInstanceWithContext(
            "com.sun.star.awt.UnoControlDialog", ctx
        )
        control.setModel(dialog_model)
        toolkit = smgr.createInstanceWithContext("com.sun.star.awt.Toolkit", ctx)
        peer_parent = None
        try:
            peer_parent = doc.getCurrentController().getFrame().getContainerWindow()
        except Exception:
            peer_parent = None
        control.createPeer(toolkit, peer_parent)
        control.setVisible(True)
        control.execute()
        control.dispose()
    except Exception:
        # Fallback message box (truncated)
        try:
            from com.sun.star.awt.MessageBoxButtons import BUTTONS_OK
            from com.sun.star.awt.MessageBoxType import INFOBOX

            ctx = uno.getComponentContext()
            toolkit = ctx.ServiceManager.createInstanceWithContext(
                "com.sun.star.awt.Toolkit", ctx
            )
            window = doc.getCurrentController().getFrame().getContainerWindow()
            box = toolkit.createMessageBox(
                window, INFOBOX, BUTTONS_OK, title, body[:1800]
            )
            box.execute()
        except Exception:
            traceback.print_exc(file=sys.stderr)


def _message(doc, title, text, kind="info"):
    import uno

    try:
        from com.sun.star.awt.MessageBoxButtons import BUTTONS_OK
        from com.sun.star.awt.MessageBoxType import ERRORBOX, INFOBOX

        box_type = ERRORBOX if kind == "error" else INFOBOX
        ctx = uno.getComponentContext()
        toolkit = ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.awt.Toolkit", ctx
        )
        window = doc.getCurrentController().getFrame().getContainerWindow()
        box = toolkit.createMessageBox(window, box_type, BUTTONS_OK, title, text)
        box.execute()
    except Exception:
        print("%s: %s" % (title, text), file=sys.stderr)


def inspect_japanese_typography(*_args):
    """Entry point: inspect current paragraph / selection (read-only)."""
    if _analysis is None:
        try:
            doc = _get_document()
        except RuntimeError:
            return
        lang = _ui_lang(doc)
        _message(doc, _t(lang, "command_title"), _t(lang, "err_analysis"), kind="error")
        return

    # Capture modified flag before any UNO reads (should stay unchanged)
    was_modified = None
    try:
        doc = _get_document()
    except RuntimeError:
        return

    lang = _ui_lang(doc)
    title = _t(lang, "command_title")

    try:
        was_modified = bool(doc.isModified())
    except Exception:
        was_modified = None

    try:
        scope = extract_scope(doc)
    except Exception:
        traceback.print_exc(file=sys.stderr)
        _message(doc, title, _t(lang, "err_scope"), kind="error")
        return

    if scope.selection_kind == "unsupported":
        _message(doc, title, _t(lang, "err_scope"), kind="info")
        return

    try:
        report = _analysis.run_inspection(scope)
        body = format_report(report, lang)
    except Exception:
        traceback.print_exc(file=sys.stderr)
        _message(doc, title, _t(lang, "err_analysis"), kind="error")
        return

    # Restore modified flag if a getter somehow dirtied the doc (defensive)
    try:
        if was_modified is not None and bool(doc.isModified()) != was_modified:
            doc.setModified(was_modified)
    except Exception:
        pass

    _show_report_dialog(doc, title, body, lang)

    # Again after dialog (dialog must not dirty)
    try:
        if was_modified is not None and bool(doc.isModified()) != was_modified:
            doc.setModified(was_modified)
    except Exception:
        pass

