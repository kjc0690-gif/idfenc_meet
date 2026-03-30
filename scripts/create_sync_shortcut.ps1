$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\Claude_Sync_Notify.lnk")
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = '-ExecutionPolicy Bypass -WindowStyle Hidden -File "C:\Users\kjc06\클로드 작업기록\idfenc_meet\scripts\sync-notify.ps1"'
$Shortcut.Description = "Claude Sync Notify"
$Shortcut.WindowStyle = 7
$Shortcut.Save()
Write-Host "Shortcut created!"
