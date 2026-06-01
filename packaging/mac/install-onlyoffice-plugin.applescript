-- Copy marinaMoji Kaeriten into ONLYOFFICE Desktop plugins folder (macOS).
-- Runs bundled install-onlyoffice-macos.sh (bash).

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

on bundledPluginSourceDir()
	set mePosix to POSIX path of (path to me)
	try
		return do shell script "ME=" & quoted form of mePosix & "; " & ¬
			"if [ -d \"$ME/Contents/Resources/marinamoji-kaeriten-onlyoffice\" ]; then " & ¬
			"printf '%s\\n' \"$ME/Contents/Resources/marinamoji-kaeriten-onlyoffice/\"; " & ¬
			"elif [ -d \"$(dirname \"$ME\")/../Resources/marinamoji-kaeriten-onlyoffice\" ]; then " & ¬
			"printf '%s\\n' \"$(cd \"$(dirname \"$ME\")/../Resources/marinamoji-kaeriten-onlyoffice\" && pwd)/\"; " & ¬
			"else exit 1; fi"
	on error
		return ""
	end try
end bundledPluginSourceDir

on run
	set scriptPath to my bundledResourcePath("install-onlyoffice-macos.sh")
	set srcDir to my bundledPluginSourceDir()

	if scriptPath is "" or srcDir is "" then
		display alert "Installer is incomplete." message "Plugin files not found in app bundle." as critical
		return
	end if

	try
		do shell script "bash " & quoted form of scriptPath & " " & quoted form of srcDir
	on error errMsg
		if errMsg contains "ONLYOFFICE not found" or errMsg contains "exit code 2" then
			display alert "ONLYOFFICE not found." message "Install ONLYOFFICE Desktop Editors, open Writer once, then run this installer again." as critical
		else
			display alert "Could not install plugin." message errMsg as critical
		end if
		return
	end try

	display dialog "marinaMoji was installed for ONLYOFFICE." & return & return & ¬
		"1. Quit ONLYOFFICE completely (Cmd+Q)." & return & ¬
		"2. Reopen Writer." & return & ¬
		"3. Plugins → marinaMoji" & return & return & ¬
		"(Experimental — compound marks may stack imperfectly.)" ¬
		buttons {"OK"} default button "OK" with title "Install complete"
end run
