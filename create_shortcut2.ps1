$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\Claude_Sync.lnk")
$Shortcut.TargetPath = "$env:USERPROFILE\claude-sync.bat"
$Shortcut.WorkingDirectory = "$env:USERPROFILE"
$Shortcut.Description = "Claude Sync"
$Shortcut.WindowStyle = 7
$Shortcut.Save()
Write-Host "Startup shortcut updated!"
