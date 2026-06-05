# -*- coding: utf-8 -*-
"""
Toolbar/menu ProtocolHandler for marinaMoji Kaeriten (loaded at extension root).
Loads the main macro module from Scripts/python/ on first button click.
"""
import os
import sys

import uno
import unohelper
from com.sun.star.frame import XDispatch, XDispatchProvider
from com.sun.star.lang import XInitialization, XServiceInfo

PROTOCOL = "org.marinaMoji.kaeriten:"
IMPLE_NAME = "MarinaMojiKaeritenProtocolHandler"
SERVICE_NAME = "com.sun.star.frame.ProtocolHandler"
_COMMANDS = frozenset(
    (
        "render_kaeriten",
        "unrender_kaeriten",
        "copy_plain_text",
        "toggle_page_writing_mode",
    )
)


def _extension_root():
    ref = __file__
    if isinstance(ref, str) and ref.startswith("file:"):
        ref = uno.fileUrlToSystemPath(ref)
    return os.path.dirname(os.path.abspath(ref))


def _macro_module():
    script_dir = os.path.join(_extension_root(), "Scripts", "python")
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    import marinamoji_kaeriten as macros  # noqa: WPS433 — LO extension layout

    return macros


class MarinaMojiKaeritenProtocolHandler(
    unohelper.Base, XServiceInfo, XDispatchProvider, XDispatch, XInitialization
):
    def __init__(self, ctx, *args):
        self.ctx = ctx
        self.frame = None

    def initialize(self, objects):
        if objects:
            self.frame = objects[0]

    def getImplementationName(self):
        return IMPLE_NAME

    def supportsService(self, name):
        return name == SERVICE_NAME

    def getSupportedServiceNames(self):
        return (SERVICE_NAME,)

    def queryDispatch(self, url, target_frame_name, search_flags):
        if url.Protocol == PROTOCOL and url.Path in _COMMANDS:
            return self
        return None

    def queryDispatches(self, requests):
        return tuple(
            self.queryDispatch(r.FeatureURL, r.FrameName, r.SearchFlags) for r in requests
        )

    def dispatch(self, url, args):
        if url.Protocol != PROTOCOL:
            return
        macros = _macro_module()
        path = url.Path
        if path == "render_kaeriten":
            macros.render_kaeriten()
        elif path == "unrender_kaeriten":
            macros.unrender_kaeriten()
        elif path == "copy_plain_text":
            macros.copy_plain_text()
        elif path == "toggle_page_writing_mode":
            macros.toggle_page_writing_mode()

    def addStatusListener(self, control, url):
        pass

    def removeStatusListener(self, control, url):
        pass


g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(
    MarinaMojiKaeritenProtocolHandler,
    IMPLE_NAME,
    (SERVICE_NAME,),
)
