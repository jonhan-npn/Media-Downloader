#define MyAppName "MediaDownloader"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "MediaDownloader"
#define MyAppExeName "MediaDownloader.exe"

[Setup]
AppId={{A7F2C9E1-57C6-4D87-8C0A-5E9A0D2F7B31}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\MediaDownloader
DefaultGroupName={#MyAppName}
OutputDir=..\..\..\release
OutputBaseFilename=MediaDownloader-Setup-{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\{#MyAppExeName}
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
Source: "..\..\..\dist\MediaDownloader\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\MediaDownloader"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\MediaDownloader"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch MediaDownloader"; Flags: postinstall nowait skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
