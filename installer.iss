; Inno Setup script for Adhan App  (https://jrsoftware.org/isinfo.php)
; Installer languages: English + Arabic (a language picker is shown first)
#ifndef MyAppVersion
  #define MyAppVersion "1.0.0"
#endif
#define MyAppName "Adhan App"
#define MyAppExe "AdhanApp.exe"

[Setup]
AppId={{C91575FD-3A2E-498D-B70F-7EEB0CD5D388}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=Repo-EG
AppPublisherURL=https://github.com/Repo-EG/adhan-app
AppSupportURL=https://github.com/Repo-EG/adhan-app/issues
AppUpdatesURL=https://github.com/Repo-EG/adhan-app/releases
; تثبيت لمستخدم واحد: لا يحتاج صلاحيات مدير، والمجلد قابل للكتابة (للإعدادات وملفات الأذان)
PrivilegesRequired=lowest
DefaultDirName={autopf}\AdhanApp
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=installer_output
OutputBaseFilename=AdhanApp-Setup-{#MyAppVersion}
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\{#MyAppExe}
Compression=lzma2
SolidCompression=yes
CloseApplications=yes
AppMutex=RepoEG.AdhanApp
; مظهر عصري (ويندوز 10 و 11) + صور المعالج
WizardStyle=modern
WizardSizePercent=110
WizardImageFile=wizard_large.bmp
WizardSmallImageFile=wizard_small.bmp
; نافذة اختيار اللغة تظهر دائمًا
ShowLanguageDialog=yes
UsePreviousLanguage=no

[Languages]
Name: "arabic"; MessagesFile: "Arabic.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[CustomMessages]
english.TaskAutostart=Start Adhan App when Windows starts
english.TaskGroup=Options:
english.RunLaunch=Launch Adhan App
english.LinkAudio=Adhan App - Adhan audio files
arabic.TaskAutostart=تشغيل البرنامج تلقائيًا عند تشغيل ويندوز
arabic.TaskGroup=خيارات:
arabic.RunLaunch=تشغيل مواقيت الصلاة والأذان
arabic.LinkAudio=Adhan App - ملفات الأذان
arabic.CreateDesktopIcon=إنشاء اختصار على سطح المكتب
arabic.AdditionalIcons=اختصارات إضافية:

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "autostart"; Description: "{cm:TaskAutostart}"; GroupDescription: "{cm:TaskGroup}"

[Dirs]
Name: "{app}\adhan"
Name: "{app}\takbeer"

[Files]
Source: "dist\AdhanApp\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion
; الملفات التالية تُضمَّن فقط إن وُجدت بجوار هذا الملف (صورة الخلفية وملفات الأذان)
Source: "wall.png"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "adhan\*"; DestDir: "{app}\adhan"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist
Source: "takbeer\*"; DestDir: "{app}\takbeer"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExe}"
Name: "{autoprograms}\{cm:LinkAudio}"; Filename: "{app}\adhan"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExe}"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "AdhanAppAlexandria"; ValueData: """{app}\{#MyAppExe}"" --minimized"; Flags: uninsdeletevalue; Tasks: autostart

[Run]
Filename: "{app}\{#MyAppExe}"; Description: "{cm:RunLaunch}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: files; Name: "{app}\settings.json"
Type: files; Name: "{app}\timings_cache.json"
Type: files; Name: "{app}\adhan_log.txt"
Type: files; Name: "{app}\adhan_log.txt.1"
Type: dirifempty; Name: "{app}\adhan"
Type: dirifempty; Name: "{app}\takbeer"

[Code]
// لغة البرنامج = لغة التثبيت (عند أول تثبيت فقط، دون المساس بإعدادات موجودة)
procedure CurStepChanged(CurStep: TSetupStep);
var
  Path, Lang: String;
begin
  if CurStep = ssPostInstall then
  begin
    Path := ExpandConstant('{app}\settings.json');
    if not FileExists(Path) then
    begin
      if ActiveLanguage = 'arabic' then Lang := 'ar' else Lang := 'en';
      SaveStringToFile(Path, '{"lang": "' + Lang + '"}', False);
    end;
  end;
end;

// إزالة التشغيل التلقائي مع ويندوز عند الحذف (حتى لو فُعّل من داخل البرنامج)
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usUninstall then
    RegDeleteValue(HKEY_CURRENT_USER, 'Software\Microsoft\Windows\CurrentVersion\Run', 'AdhanAppAlexandria');
end;
