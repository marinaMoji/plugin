# -*- coding: utf-8 -*-
"""
About marinaMoji — branded illustrated guide (offline HTML).

Opens a locale-matched local HTML page bundled with the extension.
Does not modify the document. Website link lives in the HTML footer.
"""

from __future__ import annotations

import os
import sys

_SITE = "https://marinamoji.crcao.fr"

_STRINGS = {
    "en": {
        "title": "About marinaMoji",
        "missing": "The marinaMoji guide could not be found in this installation.",
        "open_fail": "Could not open the marinaMoji guide (%s).",
    },
    "ja": {
        "title": "marinaMoji について",
        "missing": "このインストールに marinaMoji の案内が見つかりません。",
        "open_fail": "marinaMoji の案内を開けませんでした（%s）。",
    },
    "fr": {
        "title": "À propos de marinaMoji",
        "missing": "Le guide marinaMoji est introuvable dans cette installation.",
        "open_fail": "Impossible d’ouvrir le guide marinaMoji (%s).",
    },
}


def _ui_lang(doc=None) -> str:
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


def _t(lang: str, key: str, *args) -> str:
    table = _STRINGS.get(lang) or _STRINGS["en"]
    text = table.get(key) or _STRINGS["en"].get(key) or key
    if args:
        try:
            return text % args
        except Exception:
            return text
    return text


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


def _message(doc, title, text, kind="info"):
    try:
        import uno
        from com.sun.star.awt.MessageBoxButtons import BUTTONS_OK
        from com.sun.star.awt.MessageBoxType import ERRORBOX, INFOBOX, WARNINGBOX

        box_type = INFOBOX
        if kind == "error":
            box_type = ERRORBOX
        elif kind == "warning":
            box_type = WARNINGBOX
        ctx = uno.getComponentContext()
        toolkit = ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.awt.Toolkit", ctx
        )
        window = doc.getCurrentController().getFrame().getContainerWindow()
        box = toolkit.createMessageBox(window, box_type, BUTTONS_OK, title, text[:1500])
        box.execute()
    except Exception:
        print("%s: %s" % (title, text))


def _module_file():
    ref = __file__
    if isinstance(ref, str) and ref.startswith("file:"):
        try:
            import uno

            ref = uno.fileUrlToSystemPath(ref)
        except Exception:
            ref = ref[5:]
            if ref.startswith("//"):
                ref = ref[2:]
    return os.path.abspath(ref)


def extension_root():
    """OXT root when packed as Scripts/python/about.py → ../.."""
    here = os.path.dirname(_module_file())
    # Scripts/python → Scripts → extension root
    return os.path.normpath(os.path.join(here, "..", ".."))


def help_dir():
    return os.path.join(extension_root(), "help")


def guide_path_for_lang(lang: str) -> str:
    name = "about_%s.html" % (lang if lang in ("en", "ja", "fr") else "en")
    path = os.path.join(help_dir(), name)
    if os.path.isfile(path):
        return path
    fallback = os.path.join(help_dir(), "about_en.html")
    return fallback if os.path.isfile(fallback) else path


def _to_file_url(path: str) -> str:
    import uno

    return uno.systemPathToFileUrl(os.path.abspath(path))


def open_local_guide(path: str) -> None:
    """Open a local HTML file in the default browser (cross-platform)."""
    import uno

    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager
    url = _to_file_url(path)
    try:
        from com.sun.star.system.SystemShellExecuteFlags import URIS_ONLY

        exe = smgr.createInstanceWithContext(
            "com.sun.star.system.SystemShellExecute", ctx
        )
        exe.execute(url, "", URIS_ONLY)
        return
    except Exception:
        pass
    # Fallback: OS openers
    if sys.platform == "darwin":
        os.system('open "%s"' % path.replace('"', ""))
    elif sys.platform.startswith("win"):
        os.startfile(path)  # type: ignore[attr-defined]
    else:
        os.system('xdg-open "%s"' % path.replace('"', ""))


def show_about_marinamoji(*_args):
    """Toolbar: open the branded marinaMoji guide (document untouched)."""
    try:
        doc = _get_document()
    except RuntimeError:
        doc = None
    lang = _ui_lang(doc)
    title = _t(lang, "title")
    path = guide_path_for_lang(lang)
    if not os.path.isfile(path):
        if doc is not None:
            _message(doc, title, _t(lang, "missing"), kind="error")
        return
    try:
        open_local_guide(path)
    except Exception as exc:
        if doc is not None:
            _message(
                doc,
                title,
                _t(lang, "open_fail", type(exc).__name__),
                kind="error",
            )


# Pure helpers for unit tests
def resolve_guide_filename(lang: str) -> str:
    if lang in ("ja", "fr"):
        return "about_%s.html" % lang
    return "about_en.html"
