; ============================================================================
; Doqurix - Professional Installer Script
; ============================================================================
; Inno Setup 6 Script with Python Runtime Bundling
; ============================================================================

#define MyAppName "Doqurix"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "AI Solutions"
#define MyAppURL "https://github.com/yourusername/doqurix"
#define MyAppExeName "Doqurix.exe"
#define MinWindowsVersion "10.0"

[Setup]
; Application Information
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppCopyright=Copyright (C) 2025 {#MyAppPublisher}

; Installation Directories
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=no
AllowNoIcons=yes

; Output Configuration
OutputDir=installer_output
OutputBaseFilename=Doqurix_Setup_v{#MyAppVersion}
; SetupIconFile - use application icon if available
#ifexist "app_icon.ico"
SetupIconFile=app_icon.ico
#endif
UninstallDisplayIcon={app}\{#MyAppExeName}

; Compression
Compression=lzma2/max
SolidCompression=yes
LZMAUseSeparateProcess=yes
LZMADictionarySize=1048576
LZMANumFastBytes=273

; Installer UI
WizardStyle=modern
WizardSizePercent=120
DisableWelcomePage=no
ShowLanguageDialog=auto

; System Requirements
MinVersion={#MinWindowsVersion}
PrivilegesRequired=admin
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; License and Info
LicenseFile=LICENSE.txt
InfoBeforeFile=README.txt

; Uninstall
UninstallDisplayName={#MyAppName}
UninstallFilesDir={app}\uninstall

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main Application Files
Source: "dist\Doqurix\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Doqurix\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Documentation
Source: "README.txt"; DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion

; Visual C++ Redistributable (required for numpy, llama-cpp, etc.)
Source: "vc_redist.x64.exe"; DestDir: "{tmp}"; Flags: deleteafterinstall

[Dirs]
; Create user data directories
Name: "{userappdata}\{#MyAppName}"; Permissions: users-full
Name: "{userappdata}\{#MyAppName}\data"; Permissions: users-full
Name: "{userappdata}\{#MyAppName}\models"; Permissions: users-full

[Icons]
; Start Menu Icons
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppExeName}"; Comment: "Doqurix - Intelligent Document Analysis"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"; IconFilename: "{uninstallexe}"
Name: "{group}\Documentation"; Filename: "{app}\README.txt"

; Desktop Icon
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon; IconFilename: "{app}\{#MyAppExeName}"; Comment: "Doqurix - Intelligent Document Analysis"

; Quick Launch Icon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: quicklaunchicon

[Run]
; Install Visual C++ Redistributable silently (required for AI components)
Filename: "{tmp}\vc_redist.x64.exe"; Parameters: "/install /quiet /norestart"; StatusMsg: "Installing Visual C++ Runtime (required)..."; Flags: waituntilterminated runhidden

; Launch application after installation
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent shellexec

[UninstallDelete]
; Clean up user data (optional - ask user)
Type: filesandordirs; Name: "{userappdata}\{#MyAppName}"

[Messages]
; Custom messages
WelcomeLabel2=This will install [name/ver] on your computer.%n%nThis application uses advanced AI technology to answer questions from your PDF documents.%n%nSystem Requirements:%n• Windows 10 or later (64-bit)%n• Minimum 8GB RAM%n• 5GB free disk space for AI models%n%nThe application will download AI models (~1GB) on first launch.

[Code]
var
  ProgressPage: TOutputProgressWizardPage;

// Check system requirements
function CheckSystemRequirements(): Boolean;
var
  Version: TWindowsVersion;
  MemoryMB: Cardinal;
begin
  Result := True;
  
  // Check Windows version
  GetWindowsVersionEx(Version);
  if Version.Major < 10 then
  begin
    MsgBox('This application requires Windows 10 or later.' + #13#10 + 
           'Your system: Windows ' + IntToStr(Version.Major) + '.' + IntToStr(Version.Minor), 
           mbError, MB_OK);
    Result := False;
    Exit;
  end;
  
  // Check if 64-bit Windows
  if not Is64BitInstallMode then
  begin
    MsgBox('This application requires 64-bit Windows.', mbError, MB_OK);
    Result := False;
    Exit;
  end;
end;

// Initialize setup
function InitializeSetup(): Boolean;
begin
  Result := CheckSystemRequirements();
end;

// Page change handler
procedure CurPageChanged(CurPageID: Integer);
begin
  case CurPageID of
    wpWelcome:
      WizardForm.WelcomeLabel2.Caption := 
        'This will install ' + '{#MyAppName}' + ' version {#MyAppVersion} on your computer.' + #13#10 + #13#10 +
        'This application helps you find answers from your PDF documents quickly and easily.' + #13#10 + #13#10 +
        'System Requirements:' + #13#10 +
        '• Windows 10 or later (64-bit)' + #13#10 +
        '• Minimum 8GB RAM' + #13#10 +
        '• 5GB free disk space' + #13#10 + #13#10 +
        'First-time setup requires an internet connection.' + #13#10 + #13#10 +
        'Click Next to continue, or Cancel to exit Setup.';
    
    wpInstalling:
      begin
        WizardForm.StatusLabel.Caption := 'Installing Doqurix...';
        WizardForm.ProgressGauge.Style := npbstMarquee;
      end;
    
    wpFinished:
      WizardForm.FinishedLabel.Caption := 
        'Setup has finished installing ' + '{#MyAppName}' + ' on your computer.' + #13#10 + #13#10 +
        'Important Notes:' + #13#10 +
        '• First-time setup will complete when you launch the application' + #13#10 +
        '• Please ensure you have a stable internet connection for initial setup' + #13#10 +
        '• After initial setup, the application works offline' + #13#10 + #13#10 +
        'Click Finish to exit Setup.';
  end;
end;

// Installation step handler
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Any post-installation tasks can be added here
  end;
end;

// Uninstall initialization
function InitializeUninstall(): Boolean;
var
  Response: Integer;
begin
  Result := True;
  
  Response := MsgBox('Do you want to remove user data (documents, models, settings)?' + #13#10 + #13#10 +
                     'Click Yes to remove all data (clean uninstall)' + #13#10 +
                     'Click No to keep your data for future installations', 
                     mbConfirmation, MB_YESNOCANCEL);
  
  if Response = IDCANCEL then
    Result := False;
end;
