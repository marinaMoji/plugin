# -*- coding: utf-8 -*-
"""Switch the toolbar icons between light and dark variants.

Add-on image URLs in Addons.xcu cannot follow the UI theme, so the startup job
swaps the Writer module's command images at runtime. The swap lives in memory
only (it is not persisted); it is re-applied on every launch and window event.

Appearance is read from a hidden dialog peer's StyleSettings (FaceColor): it
tracks the effective light/dark state even when LibreOffice is set to Automatic.
The first reading at startup can still be the light palette, so the listener
stays registered and the state is re-read on later window events.
"""
import os
import sys
import threading
import traceback

EXTENSION_ID = "org.marinaMoji.kaeriten"
MODULE = "com.sun.star.text.TextDocument"
LIGHT = "light"
DARK = "dark"

# Command name -> icon file stem (everything else uses its own name).
_ICON_STEM = {"copy_plain_text": "export_txt"}
COMMANDS = (
    "about_marinamoji",
    "render_kaeriten",
    "unrender_kaeriten",
    "copy_plain_text",
    "toggle_page_writing_mode",
    "apply_warichu",
    "remove_warichu",
    "apply_ruby",
    "remove_ruby",
    "apply_emphasis",
    "emphasis_menu",
    "remove_emphasis",
    "apply_tatechuyoko",
    "remove_tatechuyoko",
    "apply_jidori",
    "remove_jidori",
    "inspect_typography",
)


def variant_for_face_color(color):
    """Return DARK or LIGHT for a 0xRRGGBB toolbar/dialog face colour."""
    color &= 0xFFFFFF
    r, g, b = (color >> 16) & 255, (color >> 8) & 255, color & 255
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return DARK if luminance < 128 else LIGHT


def icon_file(command, variant):
    """Path of the icon, relative to the extension root."""
    folder = "icons-dark" if variant == DARK else "icons"
    return "{}/{}.svg".format(folder, _ICON_STEM.get(command, command))


def _log(message):
    print("marinamoji_theme: " + message, file=sys.stderr)


class ThemeSwitcher(object):
    def __init__(self, ctx):
        self.ctx = ctx
        self.lock = threading.RLock()
        self.dialog = None
        self.settings = None
        self.listener = None
        self.applied = None
        self._graphics = {}

    # -- appearance ------------------------------------------------------
    def _current_variant(self):
        if self.settings is None:
            return None
        return variant_for_face_color(self.settings.FaceColor)

    def _parent_window(self):
        try:
            desktop = self.ctx.ServiceManager.createInstanceWithContext(
                "com.sun.star.frame.Desktop", self.ctx
            )
            frame = desktop.getCurrentFrame()
            return frame.getContainerWindow() if frame is not None else None
        except Exception:
            return None

    def _style_settings_source(self):
        """(dialog_or_None, StyleSettings) from a window that is never shown.

        macOS: a hidden dialog peer (verified there). On GTK and Windows a dialog
        peer can become a visible empty window, so other platforms read the
        document frame's own settings, and only then try an invisible child window.
        """
        smgr = self.ctx.ServiceManager
        parent = self._parent_window()
        if sys.platform == "darwin":
            dialog = smgr.createInstanceWithContext(
                "com.sun.star.awt.UnoControlDialog", self.ctx
            )
            model = smgr.createInstanceWithContext(
                "com.sun.star.awt.UnoControlDialogModel", self.ctx
            )
            dialog.setModel(model)
            toolkit = smgr.createInstanceWithContext("com.sun.star.awt.Toolkit", self.ctx)
            dialog.createPeer(toolkit, parent)
            return dialog, dialog.getPeer().StyleSettings
        # Prefer the frame's own window: it already exists, so no new window can
        # appear. Only if it exposes no style settings, create an invisible child.
        try:
            settings = parent.StyleSettings
            if settings is not None:
                _log("style source: frame window")
                return None, settings
        except Exception:
            pass
        import uno
        from com.sun.star.awt import Rectangle, WindowDescriptor

        toolkit = smgr.createInstanceWithContext("com.sun.star.awt.Toolkit", self.ctx)
        desc = WindowDescriptor()
        desc.Type = uno.Enum("com.sun.star.awt.WindowClass", "SIMPLE")
        desc.WindowServiceName = "window"
        desc.Parent = parent
        desc.ParentIndex = -1
        desc.Bounds = Rectangle(0, 0, 1, 1)
        desc.WindowAttributes = 0  # child window, never made visible
        child = toolkit.createWindow(desc)
        try:
            child.setVisible(False)  # belt and braces: some backends map it anyway
        except Exception:
            pass
        _log("style source: invisible child window")
        return child, child.StyleSettings

    def ensure_listener(self):
        """Register the style listener once; re-register if it was disposed."""
        with self.lock:
            if self.listener is not None:
                return True
            import unohelper
            from com.sun.star.awt import XStyleChangeListener

            switcher = self

            class _Listener(unohelper.Base, XStyleChangeListener):
                def styleSettingsChanged(self, event):
                    switcher.refresh(force=False, reason="style change")

                def disposing(self, event):
                    switcher.reset_listener()

            try:
                dialog, settings = self._style_settings_source()
            except Exception:
                traceback.print_exc(file=sys.stderr)
                return False
            if settings is None:
                return False
            listener = _Listener()
            settings.addStyleChangeListener(listener)
            self.dialog, self.settings, self.listener = dialog, settings, listener
            self.applied = None
            return True

    def reset_listener(self):
        with self.lock:
            self.dialog = self.settings = self.listener = None

    # -- images ----------------------------------------------------------
    def _root_url(self):
        pip = self.ctx.getValueByName(
            "/singletons/com.sun.star.deployment.PackageInformationProvider"
        )
        return pip.getPackageLocation(EXTENSION_ID).rstrip("/")

    def _graphic(self, url):
        graphic = self._graphics.get(url)
        if graphic is None:
            import uno
            from com.sun.star.beans import PropertyValue

            provider = self.ctx.ServiceManager.createInstanceWithContext(
                "com.sun.star.graphic.GraphicProvider", self.ctx
            )
            prop = PropertyValue()
            prop.Name = "URL"
            prop.Value = url
            graphic = provider.queryGraphic((prop,))
            if graphic is not None:
                self._graphics[url] = graphic
        return graphic

    def _image_sizes(self):
        import uno

        sizes = []
        for name in ("SIZE_DEFAULT", "SIZE_LARGE", "SIZE_32"):
            try:
                sizes.append(uno.getConstantByName("com.sun.star.ui.ImageType." + name))
            except Exception:
                pass
        return sizes or [0]

    def apply(self, variant):
        root = self._root_url()
        manager = (
            self.ctx.getValueByName(
                "/singletons/com.sun.star.ui.theModuleUIConfigurationManagerSupplier"
            )
            .getUIConfigurationManager(MODULE)
            .getImageManager()
        )
        names, graphics = [], []
        for command in COMMANDS:
            graphic = self._graphic(root + "/" + icon_file(command, variant))
            if graphic is not None:
                names.append("{}:{}".format(EXTENSION_ID, command))
                graphics.append(graphic)
        if not names:
            return
        # In-memory only: no store(), so nothing is written to the profile.
        for size in self._image_sizes():
            manager.replaceImages(size, tuple(names), tuple(graphics))
        self.applied = variant

    def refresh(self, force=False, reason=""):
        """Re-read the appearance and swap images when it changed (or force)."""
        with self.lock:
            try:
                variant = self._current_variant()
                if variant is None:
                    return
                if force or variant != self.applied:
                    _log("{} -> {} (FaceColor=#{:06x})".format(
                        reason or "refresh", variant, self.settings.FaceColor & 0xFFFFFF))
                    self.apply(variant)
            except Exception:
                traceback.print_exc(file=sys.stderr)

    # -- entry point -----------------------------------------------------
    def on_event(self, event_name):
        """Called by the startup job. New/loaded windows rebuild toolbars, so
        they force a re-apply; focus changes only re-apply when the look changed."""
        # Only touch the UI once a window exists: a peer created at OnStartApp,
        # before any frame, risks crashing LibreOffice during launch.
        if self._parent_window() is None:
            return
        if not self.ensure_listener():
            return
        force = event_name in ("OnNew", "OnLoad")
        self.refresh(force=force, reason=event_name)


_switcher = None


def handle_event(ctx, event_name):
    global _switcher
    if _switcher is None:
        _switcher = ThemeSwitcher(ctx)
    _switcher.on_event(event_name)
