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
	on error errMsg
		if errMsg contains "LibreOffice is still running" or errMsg contains "exit code 2" then
			display dialog "LibreOffice is still running." & return & return & ¬
				"Quit Writer completely (Cmd+Q), then run this installer again." ¬
				buttons {"OK"} default button "OK" with title "Quit LibreOffice first" with icon caution
		else
			display alert "Could not install Python macros." message errMsg as critical
		end if
		return
	end try

	display dialog "marinaMoji Kaeriten is ready for LibreOffice." & return & return & ¬
		"1. In Extension Manager, click Add (if prompted) and accept the extension." & return & ¬
		"2. Restart Writer completely." & return & ¬
		"3. View → Toolbars → marinaMoji." & return & return & ¬
		"Type 說㆒㆑者, then click Render kaeriten." ¬
		buttons {"OK"} default button "OK" with title "Install complete"
end run
