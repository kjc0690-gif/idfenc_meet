# Claude 동기화 알림 - Windows 부팅 시 토스트 알림
# 시작프로그램으로 등록되어 PC 켜면 자동 실행

Add-Type -AssemblyName System.Windows.Forms

# 30초 대기 (부팅 직후 바로 뜨면 놓칠 수 있으므로)
Start-Sleep -Seconds 30

# 토스트 알림
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom, ContentType = WindowsRuntime] | Out-Null

$xml = [Windows.Data.Xml.Dom.XmlDocument]::new()
$xml.LoadXml(@"
<toast duration="long">
  <visual>
    <binding template="ToastText02">
      <text id="1">Claude 동기화 알림</text>
      <text id="2">다른 PC와 동기화할까요? Claude에서 /sync-backup 실행하세요</text>
    </binding>
  </visual>
  <audio src="ms-winsoundevent:Notification.Default"/>
</toast>
"@)

[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Claude Code").Show(
    [Windows.UI.Notifications.ToastNotification]::new($xml)
)
