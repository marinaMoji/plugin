-- Install marinaMoji Kaeriten manifest for Word on macOS (no Terminal).
-- Bundle this script as .app with manifest.production.xml in Contents/Resources/

on run
	set manifestName to "marinamoji-kaeriten.xml"
	set wefPosix to (POSIX path of (path to home folder)) & "Library/Containers/com.microsoft.Word/Data/Documents/wef/"

	try
		do shell script "mkdir -p " & quoted form of wefPosix
	on error errMsg
		display alert "Could not create Word add-in folder." message errMsg as critical
		return
	end try

	set bundledManifest to my resourcePath("manifest.production.xml")
	if bundledManifest is "" then
		set bundledManifest to my resourcePath("marinamoji-kaeriten-word.xml")
	end if
	if bundledManifest is "" then
		display alert "Installer is incomplete." message "manifest.production.xml is missing from the app bundle." as critical
		return
	end if

	set destPosix to wefPosix & manifestName
	try
		do shell script "rm -f " & quoted form of destPosix
		do shell script "cp " & quoted form of bundledManifest & " " & quoted form of destPosix
	on error shellError
		-- macOS can refuse writes into another app's container; Finder is allowed to.
		try
			tell application "Finder"
				duplicate (POSIX file bundledManifest as alias) to (POSIX file wefPosix as alias) with replacing
				set name of (POSIX file (wefPosix & "manifest.production.xml") as alias) to manifestName
			end tell
		on error
			my manualFallback(bundledManifest, wefPosix, manifestName, shellError)
			return
		end try
	end try

	display dialog "marinaMoji Kaeriten is registered for Word." & return & return & ¬
		"1. Quit Word completely (Cmd+Q)." & return & ¬
		"2. Open Word with a document." & return & ¬
		"3. Accueil → Kaeriten → Kaeriten pane." & return & return & ¬
		"(Requires internet so Word can load the add-in from our website.)" ¬
		buttons {"OK"} default button "OK" with title "Install complete"
end run

on manualFallback(bundledManifest, wefPosix, manifestName, errMsg)
	display alert "macOS blocked the automatic install." message "Word's add-in folder is protected. Finish by hand: drag the file shown in the first Finder window into the second one, and rename it to " & manifestName & "." & return & return & "Alternatively allow this installer under System Settings → Privacy & Security → Full Disk Access, then run it again." & return & return & errMsg as critical
	try
		do shell script "open -R " & quoted form of bundledManifest
		do shell script "open " & quoted form of wefPosix
	end try
end manualFallback

on resourcePath(fileName)
	try
		set appPath to POSIX path of (path to me)
		set resourcesDir to appPath & "Contents/Resources/"
		set candidate to resourcesDir & fileName
		do shell script "test -f " & quoted form of candidate
		return candidate
	on error
		return ""
	end try
end resourcePath
