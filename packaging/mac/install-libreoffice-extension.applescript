-- Install marinaMoji Kaeriten for LibreOffice on macOS (no Terminal).
-- Runs bundled install-libreoffice-macos.sh (bash).

on bundledResourcePath(fileName)
	set mePosix to POSIX path of (path to me)
	try
		return do shell script "ME=" & quoted form of mePosix & "; F=" & quoted form of fileName & "; " & ¬
			"if [ -f \"$ME/Contents/Resources/$F\" ]; then " & ¬
			"printf '%s\\n' \"$ME/Contents/Resources/$F\"; " & ¬
			"elif [ -f \"$(dirname \"$ME\")/../Resources/$F\" ]; then " & ¬
			"printf '%s\\n' \"$(cd \"$(dirname \"$ME\")/../Resources\" && pwd)/$F\"; " & ¬
			"else exit 1; fi"
	on error
		return ""
	end try
end bundledResourcePath

on run
	set scriptPath to my bundledResourcePath("install-libreoffice-macos.sh")

	if scriptPath is "" then
		display alert "Installer is incomplete." message "install-libreoffice-macos.sh not found in app bundle." as critical
		return
	end if

	try
		do shell script "bash " & quoted form of scriptPath
	on error errMsg number errNum
		-- do shell script maps script exit status to errNum (often 1 for any failure);
		-- match on message text from install-libreoffice-macos.sh exit codes 2/3/4.
		if errMsg contains "LibreOffice is still running" or errMsg contains "exit code 2" then
			display dialog "LibreOffice is still running." & return & return & ¬
				"Quit Writer completely (Cmd+Q), then run this installer again." ¬
				buttons {"OK"} default button "OK" with title "Quit LibreOffice first" with icon caution
		else if errMsg contains "LibreOffice was not found" or errMsg contains "exit code 3" then
			display alert "LibreOffice not found." message ¬
				"Install LibreOffice from https://www.libreoffice.org/ (or move LibreOffice.app into Applications), then run this installer again." as critical
		else if errMsg contains "Could not install the .oxt" or errMsg contains "exit code 4" then
			display alert "Extension install failed." message ¬
				"Python macros were copied, but the .oxt could not be registered." & return & return & ¬
				"In LibreOffice: Tools → Extension Manager → Add, then choose MarinaMojiKaeriten.oxt from this disk image." & return & return & ¬
				errMsg as critical
		else
			display alert "Could not finish LibreOffice install." message errMsg as critical
		end if
		return
	end try

	display dialog "marinaMoji Kaeriten is ready for LibreOffice." & return & return & ¬
		"1. Restart Writer completely (Cmd+Q, then reopen)." & return & ¬
		"2. View → Toolbars → marinaMoji." & return & return & ¬
		"Type 說㆒㆑者, then click Render kaeriten." ¬
		buttons {"OK"} default button "OK" with title "Install complete"
end run
