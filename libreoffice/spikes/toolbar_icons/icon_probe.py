"""Experimental LibreOffice Python macro: replace one command image in memory.

Copy this file and both SVGs together into the user Python macro directory.
Use only in a disposable LibreOffice profile; this is not production code.
"""
import os
import uno
from com.sun.star.beans import PropertyValue

COMMAND = "org.marinaMoji.kaeriten:apply_ruby"


def _set_variant(variant):
    ctx = XSCRIPTCONTEXT.getComponentContext()
    provider = ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.graphic.GraphicProvider", ctx)
    prop = PropertyValue()
    prop.Name = "URL"
    script_path = uno.fileUrlToSystemPath(__file__) if __file__.startswith("file:") else __file__
    prop.Value = uno.systemPathToFileUrl(os.path.join(os.path.dirname(script_path),
                                                      ("diagnostic.svg" if variant == "diagnostic" else "apply_ruby_" + variant + ".svg")))
    graphic = provider.queryGraphic((prop,))
    if graphic is None:
        raise RuntimeError("Could not load probe SVG")
    supplier = ctx.getValueByName("/singletons/com.sun.star.ui.theModuleUIConfigurationManagerSupplier")
    manager = supplier.getUIConfigurationManager("com.sun.star.text.TextDocument").getImageManager()
    # No store(): exercise the live in-memory change, not a profile write.
    for size in (0, 1, 2):
        manager.replaceImages(size, (COMMAND,), (graphic,))


def light_icon():
    _set_variant("light")


def dark_icon():
    _set_variant("dark")


def diagnostic_icon():
    _set_variant("diagnostic")


# Experimental listener. The registration holds the listener alive after the
# macro returns; retain the objects here as well for explicit cleanup.
import traceback
import unohelper
from com.sun.star.awt import XStyleChangeListener

_listener = None
_settings = None


def _log(message):
    script_path = uno.fileUrlToSystemPath(__file__) if __file__.startswith("file:") else __file__
    with open(os.path.join(os.path.dirname(script_path), "icon_probe.log"), "a", encoding="utf-8") as out:
        out.write(message + "\n")


def _apply_style(settings, reason):
    color = settings.FaceColor & 0xffffff
    r, g, b = (color >> 16) & 255, (color >> 8) & 255, color & 255
    # FaceColor is a proxy, not necessarily the actual toolbar background.
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
    variant = "dark" if luminance < 128 else "light"
    _log("{}: FaceColor=#{:06x}, variant={}".format(reason, color, variant))
    _set_variant(variant)


class StyleListener(unohelper.Base, XStyleChangeListener):
    def __init__(self, settings):
        self.settings = settings

    def styleSettingsChanged(self, event):
        try:
            _apply_style(self.settings, "styleSettingsChanged")
        except Exception:
            _log(traceback.format_exc())

    def disposing(self, event):
        _log("style settings disposed")


def start_auto():
    global _listener, _settings
    if _listener is not None:
        _settings.removeStyleChangeListener(_listener)
        _listener = _settings = None
    document = XSCRIPTCONTEXT.getDocument()
    if document is None:
        raise RuntimeError("Open a Writer document before starting the probe")
    frame = document.getCurrentController().getFrame()
    layout = frame.getPropertyValue("LayoutManager")
    toolbar = layout.getElement("private:resource/toolbar/addon_org.marinaMoji.kaeriten.toolbar.v7")
    candidates = [("frame", frame.getContainerWindow())]
    if toolbar is not None:
        candidates.insert(0, ("toolbar", toolbar.getRealInterface()))
    _settings = None
    for name, window in candidates:
        try:
            _settings = window.StyleSettings
        except AttributeError:
            _log(name + ": no XStyleSettingsSupplier")
            continue
        if _settings is not None:
            _log("using " + name + " style settings")
            break
    if _settings is None:
        raise RuntimeError("Neither the marinaMoji toolbar nor the Writer frame exposes style settings")
    _listener = StyleListener(_settings)
    _settings.addStyleChangeListener(_listener)
    _log("listener registered")
    _apply_style(_settings, "initial")


def stop_auto():
    global _listener, _settings
    if _listener is not None:
        _settings.removeStyleChangeListener(_listener)
        _log("listener removed")
        _listener = _settings = None


# A second experiment: observe explicit LibreOffice appearance settings.
# Automatic (0) follows the OS and does not tell us the effective appearance.
from com.sun.star.beans import XPropertyChangeListener
_config = None
_config_listener = None


def _apply_appearance(value, reason):
    _log("{}: ApplicationAppearance={}".format(reason, value))
    if value in (1, 2):
        _set_variant("light" if value == 1 else "dark")
    else:
        _log("Automatic or unknown appearance: effective color unavailable")


class AppearanceListener(unohelper.Base, XPropertyChangeListener):
    def __init__(self, config):
        self.config = config
        self.last_value = None

    def update(self, reason):
        value = self.config.getPropertyValue("ApplicationAppearance")
        _log("{}: event; current value={}".format(reason, value))
        if value != self.last_value:
            self.last_value = value
            _apply_appearance(value, reason)

    def propertyChange(self, event):
        try:
            self.update("propertyChange")
        except Exception:
            _log(traceback.format_exc())

    def disposing(self, event):
        _log("appearance configuration disposed")


def start_config():
    global _config, _config_listener
    if _config_listener is not None:
        _config.removePropertyChangeListener("ApplicationAppearance", _config_listener)
    ctx = XSCRIPTCONTEXT.getComponentContext()
    provider = ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.configuration.ConfigurationProvider", ctx)
    node = PropertyValue()
    node.Name = "nodepath"
    node.Value = "/org.openoffice.Office.Common/Appearance"
    _config = provider.createInstanceWithArguments(
        "com.sun.star.configuration.ConfigurationAccess", (node,))
    _config_listener = AppearanceListener(_config)
    _config.addPropertyChangeListener("ApplicationAppearance", _config_listener)
    _log("appearance listener registered")
    _config_listener.update("initial")


def stop_config():
    global _config, _config_listener
    if _config_listener is not None:
        _config.removePropertyChangeListener("ApplicationAppearance", _config_listener)
        _config_listener = _config = None
        _log("appearance listener removed")


# A hidden UNO dialog peer may expose style settings even when Writer's own
# frame and toolbar do not. This probes notifications, not production behavior.
_proxy_dialog = None
_proxy_settings = None
_proxy_listener = None


def start_style_proxy():
    global _proxy_dialog, _proxy_settings, _proxy_listener
    if _proxy_listener is not None:
        stop_style_proxy()
    ctx = XSCRIPTCONTEXT.getComponentContext()
    smgr = ctx.ServiceManager
    dialog = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialog", ctx)
    model = smgr.createInstanceWithContext("com.sun.star.awt.UnoControlDialogModel", ctx)
    dialog.setModel(model)
    toolkit = smgr.createInstanceWithContext("com.sun.star.awt.Toolkit", ctx)
    parent = XSCRIPTCONTEXT.getDocument().getCurrentController().getFrame().getContainerWindow()
    dialog.createPeer(toolkit, parent)
    peer = dialog.getPeer()
    try:
        settings = peer.StyleSettings
    except AttributeError:
        dialog.dispose()
        raise RuntimeError("Hidden dialog peer does not expose style settings")
    listener = StyleListener(settings)
    settings.addStyleChangeListener(listener)
    _proxy_dialog, _proxy_settings, _proxy_listener = dialog, settings, listener
    _log("hidden dialog style listener registered")
    _apply_style(settings, "proxy initial")


def stop_style_proxy():
    global _proxy_dialog, _proxy_settings, _proxy_listener
    if _proxy_listener is not None:
        _proxy_settings.removeStyleChangeListener(_proxy_listener)
        _proxy_dialog.dispose()
        _proxy_dialog = _proxy_settings = _proxy_listener = None
        _log("hidden dialog style listener removed")


g_exportedScripts = (light_icon, dark_icon, diagnostic_icon, start_auto, stop_auto,
                     start_config, stop_config, start_style_proxy, stop_style_proxy)
