$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\Claude_Sync.lnk")
$Shortcut.TargetPath = "C:\Users\note\Desktop\클로드_작업기록\sync-startup.bat"
$Shortcut.WorkingDirectory = "C:\Users\note\Desktop\클로드_작업기록"
$Shortcut.Description = "Claude Sync"
$Shortcut.Save()
Write-Host "Startup shortcut created successfully!"
