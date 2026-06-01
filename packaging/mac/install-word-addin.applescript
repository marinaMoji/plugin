-- Install marinaMoji Kaeriten manifest for Word on macOS (no Terminal).
-- Bundle this script as .app with manifest.production.xml in Contents/Resources/

on run
	set manifestName to "marinamoji-kaeriten.xml"
	set wefPosix to (POSIX path of (path to home folder)) & "Library/Containers/com.microsoft.Word/Data/Documents/wef"

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
		do shell script "rm -f " & quoted form of (wefPosix & "*.xml") & " " & quoted form of (wefPosix & "*.manifest.xml")
		do shell script "cp " & quoted form of bundledManifest & " " & quoted form of destPosix
	on error errMsg
		display alert "Could not copy manifest." message errMsg as critical
		return
	end try

	display dialog "marinaMoji Kaeriten is registered for Word." & return & return & ¬
		"1. Quit Word completely (Cmd+Q)." & return & ¬
		"2. Open Word with a document." & return & ¬
		"3. Accueil → Kaeriten → Kaeriten pane." & return & return & ¬
		"(Requires internet so Word can load the add-in from our website.)" ¬
		buttons {"OK"} default button "OK" with title "Install complete"
end run

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
