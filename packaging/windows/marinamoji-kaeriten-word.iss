; Per-user installer that registers the marinaMoji Kaeriten Word add-in on Windows.
; No admin rights, no network share: it copies the production manifest under
; %LOCALAPPDATA% and registers it in Office's developer-add-in key, which makes Word
; list it under Insertion > Compléments > Mes compléments > Compléments de développeur.
;
; Build (Windows, Inno Setup 6):
;   iscc /DAppVersion=0.0.4 /DManifestFile=C:\path\marinamoji-kaeriten-word.xml marinamoji-kaeriten-word.iss
#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif
#ifndef ManifestFile
  #error Pass /DManifestFile=<path to marinamoji-kaeriten-word.xml>
#endif
#ifndef OutDir
  #define OutDir "."
#endif
; Must equal <Id> in the manifest (stable; never change).
#define AddinId "7f3c8b2a-9d4e-4f1a-b6c2-8e5a1d3f9b7c"

[Setup]
AppId={{{#AddinId}}
AppName=marinaMoji Kaeriten (Word)
AppVersion={#AppVersion}
AppPublisher=marinaMoji
DefaultDirName={localappdata}\marinaMoji\Kaeriten
DisableDirPage=yes
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
Compression=lzma2
SolidCompression=yes
OutputDir={#OutDir}
OutputBaseFilename=marinamoji-kaeriten-word-setup
UninstallDisplayName=marinaMoji Kaeriten (Word)
WizardStyle=modern
CloseApplications=no

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"

[Files]
Source: "{#ManifestFile}"; DestDir: "{app}"; DestName: "marinamoji-kaeriten-word.xml"; Flags: ignoreversion

[Registry]
; Value name = add-in Id, data = manifest path (same layout office-addin-dev-settings uses).
Root: HKCU; Subkey: "Software\Microsoft\Office\16.0\WEF\Developer"; ValueType: string; \
  ValueName: "{#AddinId}"; ValueData: "{app}\marinamoji-kaeriten-word.xml"; Flags: uninsdeletevalue

[CustomMessages]
french.AfterInstall=Fermez complètement Word, puis rouvrez-le avec un document (connexion internet requise).%nAccueil → Kaeriten → volet Kaeriten, ou Insertion → Compléments → Mes compléments → Compléments de développeur.
english.AfterInstall=Close Word completely, then reopen it with a document (internet required).%nHome → Kaeriten → Kaeriten pane, or Insert → Add-ins → My Add-ins → Developer Add-ins.
japanese.AfterInstall=Word を完全に終了してから、文書を開いて再起動してください（インターネット接続が必要です）。%nホーム → Kaeriten、または 挿入 → アドイン → 個人用アドイン → 開発者アドイン。

[Code]
procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpFinished then
    WizardForm.FinishedLabel.Caption := WizardForm.FinishedLabel.Caption + #13#10#13#10 + CustomMessage('AfterInstall');
end;
