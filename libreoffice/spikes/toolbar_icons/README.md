# Toolbar image-manager probe

Experimental only; not included in the extension. It replaces the existing
Apply Ruby command image in Writer's module image manager with one of two
transparent SVGs. It does not subscribe to appearance changes and is not a
production implementation.

Use a disposable LibreOffice profile with the marinaMoji extension installed.
Copy `icon_probe.py` and both SVG files together into that profile's
`Scripts/python` directory. Open Writer with the marinaMoji toolbar visible.
Run `light_icon` and `dark_icon` through Tools > Macros > Run Macro (or APSO),
in light and dark application appearances, and observe the Apply Ruby button
at each toolbar size. Check another Writer window and a newly opened window.
Try changing the icon theme and switching appearances while Writer remains open.
Record whether each change is immediate, needs reopening the toolbar, or needs
restarting. Avoid saving documents during this test.

The probe does not call the image manager's `store()`, but LibreOffice may
persist modified UI configuration independently. Do not use a normal profile:
the probe can override a user's customized image for this command. Dispose of
the test profile after testing.

Local attempt: macOS, LibreOffice 26.8.0.3. The sandbox terminated the bundled
Python executable with status 137 and the isolated-profile `unopkg` process did
not complete. No live toolbar or appearance test was obtained. Python syntax
compilation succeeded; this does not validate the UNO calls or visible result.

Follow-up attempt: Writer launched with a disposable profile, but the extension
was absent from its toolbar. `unopkg` reported registration of version 0.3.36,
while listing without the profile argument returned the same package and the
isolated profile contained no extension files. Therefore the CLI installation
appears to have targeted the default profile instead. The probe was not run;
no live light/dark result is available. The standalone bundled Python binary
also exited 137 outside the sandbox.

Follow-up result reported by the user on macOS, LibreOffice 26.8.0.3:
`diagnostic_icon` immediately replaced Apply Ruby and `light_icon` restored
it. The explicit-appearance configuration listener also switched the icon.
The hidden-dialog style listener logged an initial FaceColor of #ffffff,
then style change notifications with #1e1e1e (dark) and #ffffff (light);
the user confirmed that LibreOffice was set to Automatic and switching macOS
appearance changed the icon. This is one platform/version only. Test other
platforms, versions, toolbar backgrounds and multiple windows before
production use.
