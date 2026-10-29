# -*- coding: utf-8 -*-
"""
Stage A jidori spike — experimental only (not toolbar / not shipped UX).

Applies CharScaleWidth / CharKerning from jidori_math.plan_jidori.
Does NOT modify global Options. Run via APSO / Scripts after copying next to
typography modules, or load from this spikes folder.

Usage idea:
  1. Select a short CJK run.
  2. Call apply_jidori_spike(5) for 5-cell target.
  3. Call remove_jidori_spike() to reset scale=100, kerning=0.
"""

from __future__ import annotations

import sys

try:
    import jidori_math as _math
except ImportError:
    # Same directory when run as LO macro with path tweak
    import os

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import jidori_math as _math


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


def _selection(doc):
    sel = doc.getCurrentController().getSelection()
    if sel is None:
        return None
    try:
        return sel.getByIndex(0)
    except Exception:
        return sel


def _message(doc, text):
    try:
        import uno
        from com.sun.star.awt.MessageBoxButtons import BUTTONS_OK
        from com.sun.star.awt.MessageBoxType import INFOBOX

        ctx = uno.getComponentContext()
        toolkit = ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.awt.Toolkit", ctx
        )
        window = doc.getCurrentController().getFrame().getContainerWindow()
        box = toolkit.createMessageBox(
            window, INFOBOX, BUTTONS_OK, "jidori spike", text[:1500]
        )
        box.execute()
    except Exception:
        print(text)


def apply_jidori_spike(target_cells=5, *_args):
    """Experimental: fit selection into target_cells (default 5)."""
    try:
        target_cells = int(target_cells)
    except Exception:
        target_cells = 5
    doc = _get_document()
    rng = _selection(doc)
    if rng is None:
        _message(doc, "Select a short CJK run first.")
        return
    try:
        text = rng.getString() or ""
    except Exception:
        text = ""
    if not text.strip():
        _message(doc, "Empty selection.")
        return

    plan = _math.plan_jidori(text, target_cells)
    em_pt = 12.0
    try:
        h = rng.getPropertyValue("CharHeightAsian")
        if h:
            em_pt = float(h)
        else:
            em_pt = float(rng.getPropertyValue("CharHeight") or 12.0)
    except Exception:
        pass

    scale, kern = _math.plan_to_uno_values(plan, em_pt)
    if scale is None:
        _message(doc, "Invalid plan: %s" % plan.note)
        return

    try:
        rng.setPropertyValue("CharScaleWidth", int(scale))
        rng.setPropertyValue("CharKerning", int(kern or 0))
    except Exception as exc:
        _message(doc, "Failed to set properties: %s" % type(exc).__name__)
        return

    _message(
        doc,
        "Applied spike jidori → %d cells\n"
        "mode=%s graphemes=%d\n"
        "CharScaleWidth=%s CharKerning=%s\n"
        "%s\n\n"
        "Visually compare to Format → Character → Position.\n"
        "Calibrate kerning units if expand looks wrong."
        % (target_cells, plan.mode, plan.grapheme_count, scale, kern, plan.note),
    )


def remove_jidori_spike(*_args):
    """Reset Scale width 100% and Spacing 0 on the selection."""
    doc = _get_document()
    rng = _selection(doc)
    if rng is None:
        _message(doc, "Select the jidori run first.")
        return
    try:
        rng.setPropertyValue("CharScaleWidth", 100)
        rng.setPropertyValue("CharKerning", 0)
    except Exception as exc:
        _message(doc, "Remove failed: %s" % type(exc).__name__)
        return
    _message(doc, "Reset CharScaleWidth=100, CharKerning=0.")


def g_exportedScripts():
    return (apply_jidori_spike, remove_jidori_spike)
