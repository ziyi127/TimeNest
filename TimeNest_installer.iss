; Inno Setup Script for TimeNest
; Created by AI Assistant

#define MyAppName "TimeNest"
#define MyAppVersion "1.0"
#define MyAppPublisher "TimeNest Team"
#define MyAppURL "https://github.com/TimeNest"
#define MyAppExeName "TimeNest.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{8B4D9C54-3F3D-4F3E-8D74-2E9A9B7C9A9B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=
PrivilegesRequired=admin
OutputDir=dist_installer
OutputBaseFilename=TimeNest-setupx64
SetupIconFile=TKtimetable.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startup"; Description: "开机自启动"; GroupDescription: "启动选项:"; Flags: unchecked

[Files]
Source: "dist_pyinstaller\TimeNest\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist_pyinstaller\TimeNest\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs
; JSON files are now included from the _internal directory
Source: "dist_pyinstaller\TimeNest\_internal\classtableMeta.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist_pyinstaller\TimeNest\_internal\timetable.json"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist_pyinstaller\TimeNest\_internal\timetable_ui_settings.json"; DestDir: "{app}"; Flags: ignoreversion
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[InstallDelete]
Type: filesandordirs; Name: "{app}\_internal"

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: """{app}\{#MyAppExeName}"""; Flags: uninsdeletevalue; Tasks: startup