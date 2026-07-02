[Setup]
AppName=Gestion Atelier
AppVersion=1.0
DefaultDirName={autopf}\Gestion Atelier
DefaultGroupName=Gestion Atelier
UninstallDisplayIcon={app}\main.exe
Compression=lzma2
SolidCompression=yes
OutputDir=C:\Users\User\Documents\garage_app\output
OutputBaseFilename=GestionAtelierSetup
WizardStyle=modern

[Files]
; Copy the compiled executable
Source: "C:\Users\User\Documents\garage_app\dist\main.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Create Start Menu and Desktop shortcuts
Name: "{group}\Gestion Atelier"; Filename: "{app}\main.exe"
Name: "{autodesktop}\Gestion Atelier"; Filename: "{app}\main.exe"

[Code]
var
  DbHostPage: TInputQueryWizardPage;

procedure InitializeWizard;
begin
  // Create a custom page to ask the user for database credentials during installation
  DbHostPage := CreateInputQueryPage(wpReady,
    'Database Connection Settings',
    'PostgreSQL Database Configuration',
    'Please enter the connection details for the PostgreSQL database server.');
  
  DbHostPage.Add('Database Host:', False);
  DbHostPage.Add('Database Port:', False);
  DbHostPage.Add('Database Name:', False);
  DbHostPage.Add('Username:', False);
  DbHostPage.Add('Password:', True);

  // Set default values (will pre-fill the form)
  DbHostPage.Values[0] := 'localhost';
  DbHostPage.Values[1] := '5432';
  DbHostPage.Values[2] := 'garage_db';
  DbHostPage.Values[3] := 'postgres';
  DbHostPage.Values[4] := 'admin';
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  EnvFilePath: String;
  Lines: TArrayOfString;
begin
  // After files are copied, generate the .env file dynamically
  if CurStep = ssPostInstall then
  begin
    EnvFilePath := ExpandConstant('{app}\.env');
    SetArrayLength(Lines, 5);
    Lines[0] := 'DB_HOST=' + DbHostPage.Values[0];
    Lines[1] := 'DB_PORT=' + DbHostPage.Values[1];
    Lines[2] := 'DB_NAME=' + DbHostPage.Values[2];
    Lines[3] := 'DB_USER=' + DbHostPage.Values[3];
    Lines[4] := 'DB_PASSWORD=' + DbHostPage.Values[4];
    
    // Save lines into {app}\.env
    SaveStringsToFile(EnvFilePath, Lines, False);
  end;
end;
