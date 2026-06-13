[Setup]
AppName=Extracteur 3DMark
AppVersion=1.0
DefaultDirName={autopf}\Extracteur 3DMark
DefaultGroupName=Extracteur 3DMark
OutputDir=dist
OutputBaseFilename=Install_Extracteur_3DMark
Compression=lzma
SolidCompression=yes
UninstallDisplayIcon={app}\Extracteur_3DMark.exe
SetupIconFile=logo.ico
DisableProgramGroupPage=yes

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "Créer un raccourci sur le Bureau"; GroupDescription: "Raccourcis additionnels:"; Flags: unchecked
Name: "startmenuicon"; Description: "Créer un raccourci dans le Menu Démarrer"; GroupDescription: "Raccourcis additionnels:"

[Files]
Source: "dist\Extracteur_3DMark.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "logo.png"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Extracteur 3DMark"; Filename: "{app}\Extracteur_3DMark.exe"; Tasks: startmenuicon
Name: "{autodesktop}\Extracteur 3DMark"; Filename: "{app}\Extracteur_3DMark.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Extracteur_3DMark.exe"; Description: "Lancer Extracteur 3DMark"; Flags: nowait postinstall skipifsilent
