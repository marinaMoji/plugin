-- Copy marinaMoji Kaeriten into ONLYOFFICE Desktop plugins folder (macOS).

on run
	set pluginFolderName to "marinamoji-kaeriten"
	set destRoot to (POSIX path of (path to home folder)) & "Library/Application Support/asc.onlyoffice.ONLYOFFICE/plugins/"
	set destPosix to destRoot & pluginFolderName & "/"
	set srcPosix to my pluginSourcePath()

	if srcPosix is "" then
		display alert "Installer is incomplete." message "Plugin files not found in app bundle." as critical
		return
	end if

	try
		do shell script "mkdir -p " & quoted form of destRoot
		do shell script "rm -rf " & quoted form of destPosix
		do shell script "cp -R " & quoted form of srcPosix & " " & quoted form of destPosix
	on error errMsg
		display alert "Could not install plugin." message errMsg as critical
		return
	end try

	display dialog "marinaMoji Kaeriten was installed for ONLYOFFICE." & return & return & ¬
		"Restart ONLYOFFICE Writer, then:" & return & ¬
		"Plugins → marinaMoji → marinaMoji Kaeriten" ¬
		buttons {"OK"} default button "OK" with title "Install complete"
end run

on pluginSourcePath()
	try
		set appPath to POSIX path of (path to me)
		set candidate to appPath & "Contents/Resources/marinamoji-kaeriten-onlyoffice/"
		do shell script "test -d " & quoted form of candidate
		return candidate
	on error
		return ""
	end try
end pluginSourcePath
