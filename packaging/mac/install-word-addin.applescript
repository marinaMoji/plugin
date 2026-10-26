-- Install marinaMoji Kaeriten manifest for Word on macOS (no Terminal).
-- Bundle this script as .app with manifest.production.xml in Contents/Resources/
--
-- macOS blocks other apps from writing into Word's container (Operation not permitted),
-- and no script-based route (shell, Finder, System Events) gets around it. So: try the
-- copy; if macOS refuses, stage the file on the Desktop and have the user drag it into
-- Word's folder (a few seconds).

on run
	set manifestName to "marinamoji-kaeriten.xml"
	set wefPosix to (POSIX path of (path to home folder)) & "Library/Containers/com.microsoft.Word/Data/Documents/wef/"

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
		do shell script "mkdir -p " & quoted form of wefPosix & " && cp -f " & quoted form of bundledManifest & " " & quoted form of destPosix
	on error errMsg
		my blocked(bundledManifest, wefPosix, manifestName, errMsg)
		return
	end try

	display dialog "marinaMoji Kaeriten is registered for Word." & return & return & ¬
		"1. Quit Word completely (Cmd+Q)." & return & ¬
		"2. Open Word with a document." & return & ¬
		"3. Accueil → Kaeriten → Kaeriten pane." & return & return & ¬
		"(Requires internet so Word can load the add-in from our website.)" ¬
		buttons {"OK"} default button "OK" with title "Install complete"
end run

-- macOS refused the copy: do it by hand.
on blocked(bundledManifest, wefPosix, manifestName, errMsg)
	display alert "One quick step by hand." message ¬
		"macOS protects Word's add-in folder, so this installer cannot copy the file itself." & return & return & ¬
		"Click Continue: a Finder window shows the file, next to Word's add-in folder. Drag the file into the folder." ¬
		buttons {"Continue", "Cancel"} default button "Continue" cancel button "Cancel"
	my byHand(bundledManifest, wefPosix, manifestName)
end blocked

-- Stage a correctly named copy on the Desktop and show it next to Word's folder.
on byHand(bundledManifest, wefPosix, manifestName)
	set stagedPosix to (POSIX path of (path to desktop folder)) & manifestName
	do shell script "cp -f " & quoted form of bundledManifest & " " & quoted form of stagedPosix
	do shell script "open -R " & quoted form of stagedPosix
	do shell script "open " & quoted form of wefPosix
	display dialog "Drag " & manifestName & " (selected on your Desktop) into the Finder window for Word's add-in folder." & return & return & ¬
		"If it asks, choose Replace." & return & return & ¬
		"Then quit Word completely (Cmd+Q) and reopen it with a document." buttons {"OK"} default button "OK" with title "Install by hand"
end byHand

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
