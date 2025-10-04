; Inno Setup Script for TimeNest
; Script to create installer with auto-start functionality

[Setup]
AppName=TimeNest
AppVersion=1.0.0
AppPublisher=TimeNest Team
AppPublisherURL=https://github.com/yourusername/TimeNest
AppSupportURL=https://github.com/yourusername/TimeNest/issues
AppUpdatesURL=https://github.com/yourusername/TimeNest/releases

DefaultDirName={autopf}\TimeNest
DefaultGroupName=TimeNest
AllowNoIcons=yes
LicenseFile=
OutputDir=.
OutputBaseFilename=TimeNest_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "chinese"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "startup"; Description: "开机自启动"; GroupDescription: "启动选项:"; Flags: unchecked

[Files]
Source: "dist_nuitka\main.dist\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\TimeNest"; Filename: "{app}\TimeNest.exe"
Name: "{autodesktop}\TimeNest"; Filename: "{app}\TimeNest.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\TimeNest.exe"; Description: "{cm:LaunchProgram,TimeNest}"; Flags: nowait postinstall skipifsilent

[InstallDelete]
Type: filesandordirs; Name: "{app}\*"

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "TimeNest"; ValueData: """{app}\TimeNest.exe"""; Flags: uninsdeletevalue; Tasks: startup