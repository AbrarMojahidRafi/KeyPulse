; Open-source NSIS installer. Build from repository root after PyInstaller.
Unicode True
!include "MUI2.nsh"

Name "KeyPulse"
OutFile "dist\KeyPulseSetup.exe"
InstallDir "$LOCALAPPDATA\Programs\KeyPulse"
RequestExecutionLevel user
SetCompressor /SOLID lzma

!define MUI_ABORTWARNING
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"

Section "Install KeyPulse" SecInstall
    SetShellVarContext current
    SetOutPath "$INSTDIR"
    File /r "dist\KeyPulse\*.*"
    CreateDirectory "$SMPROGRAMS\KeyPulse"
    CreateShortCut "$SMPROGRAMS\KeyPulse\KeyPulse.lnk" "$INSTDIR\KeyPulse.exe"
    WriteUninstaller "$INSTDIR\Uninstall.exe"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\KeyPulse" "DisplayName" "KeyPulse"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\KeyPulse" "UninstallString" '"$INSTDIR\Uninstall.exe"'
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\KeyPulse" "DisplayVersion" "0.1.0"
SectionEnd

Section "Uninstall"
    SetShellVarContext current
    Delete "$SMPROGRAMS\KeyPulse\KeyPulse.lnk"
    RMDir "$SMPROGRAMS\KeyPulse"
    ; Only the fixed installation directory is removed. The user's separate
    ; %LOCALAPPDATA%\KeyPulse database intentionally survives uninstall.
    RMDir /r "$INSTDIR"
    DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\KeyPulse"
SectionEnd
