# ========================================
# Helios AI Agent Cleanup Script
# Stops all unnecessary processes and notifications
# Run as Administrator
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Helios AI Agent Cleanup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "[1/8] Disabling Windows Notifications..." -ForegroundColor Green

# Disable all notification types
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\PushNotifications" -Name "ToastEnabled" -Value 0 -Force
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Notifications\Settings" -Name "NOC_GLOBAL_SETTING_ALLOW_NOTIFICATION_SOUND" -Value 0 -Force
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Notifications\Settings" -Name "NOC_GLOBAL_SETTING_ALLOW_TOASTS_ABOVE_LOCK" -Value 0 -Force

# Disable notification center
New-Item -Path "HKCU:\Software\Policies\Microsoft\Windows\Explorer" -Force | Out-Null
Set-ItemProperty -Path "HKCU:\Software\Policies\Microsoft\Windows\Explorer" -Name "DisableNotificationCenter" -Value 1 -Force

Write-Host "[2/8] Stopping Email and Communication Apps..." -ForegroundColor Green

# Stop common email/communication apps
$appsToStop = @(
    "Outlook",
    "OUTLOOK",
    "Thunderbird",
    "Mail",
    "Slack",
    "Teams",
    "Discord",
    "Skype",
    "Zoom",
    "WhatsApp",
    "Telegram",
    "Signal"
)

foreach ($app in $appsToStop) {
    Get-Process -Name $app -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
}

Write-Host "[3/8] Disabling Startup Programs..." -ForegroundColor Green

# Disable common startup programs (registry method)
$startupPaths = @(
    "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run",
    "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run",
    "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"
)

# Backup current startup items
$backupFile = "$env:USERPROFILE\Desktop\helios_startup_backup.txt"
"Helios Startup Backup - $(Get-Date)" | Out-File $backupFile
"" | Out-File $backupFile -Append

foreach ($path in $startupPaths) {
    if (Test-Path $path) {
        "Registry Path: $path" | Out-File $backupFile -Append
        Get-ItemProperty -Path $path | Out-File $backupFile -Append
        "" | Out-File $backupFile -Append
    }
}

Write-Host "   Startup items backed up to: $backupFile" -ForegroundColor Yellow

# Disable startup items (keep only essential ones)
$essentialStartup = @(
    "SecurityHealth",
    "Windows Defender",
    "WindowsDefender",
    "OneDrive"  # Remove this if you don't want OneDrive
)

foreach ($path in $startupPaths) {
    if (Test-Path $path) {
        $items = Get-ItemProperty -Path $path
        $items.PSObject.Properties | ForEach-Object {
            if ($_.Name -notin @("PSPath", "PSParentPath", "PSChildName", "PSDrive", "PSProvider") -and 
                $_.Name -notin $essentialStartup) {
                Remove-ItemProperty -Path $path -Name $_.Name -Force -ErrorAction SilentlyContinue
            }
        }
    }
}

Write-Host "[4/8] Disabling Windows Services (Non-Essential)..." -ForegroundColor Green

# Services to disable (non-essential for AI agent work)
$servicesToDisable = @(
    "WSearch",              # Windows Search
    "SysMain",              # Superfetch
    "DiagTrack",            # Diagnostics Tracking
    "dmwappushservice",     # WAP Push Message Routing
    "MapsBroker",           # Downloaded Maps Manager
    "lfsvc",                # Geolocation Service
    "RetailDemo",           # Retail Demo Service
    "WMPNetworkSvc",        # Windows Media Player Network Sharing
    "XblAuthManager",       # Xbox Live Auth Manager
    "XblGameSave",          # Xbox Live Game Save
    "XboxNetApiSvc",        # Xbox Live Networking Service
    "XboxGipSvc"            # Xbox Accessory Management Service
)

foreach ($service in $servicesToDisable) {
    $svc = Get-Service -Name $service -ErrorAction SilentlyContinue
    if ($svc) {
        Stop-Service -Name $service -Force -ErrorAction SilentlyContinue
        Set-Service -Name $service -StartupType Disabled -ErrorAction SilentlyContinue
        Write-Host "   Disabled: $service" -ForegroundColor Gray
    }
}

Write-Host "[5/8] Stopping Browser Processes (Keep Only Essential)..." -ForegroundColor Green

# Close all browser instances (you can reopen when needed)
$browsersToClose = @(
    "chrome",
    "firefox",
    "msedge",
    "brave",
    "opera"
)

foreach ($browser in $browsersToClose) {
    Get-Process -Name $browser -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
}

Write-Host "[6/8] Disabling Windows Update (Temporary - for AI work)..." -ForegroundColor Green

# Disable Windows Update temporarily
Stop-Service -Name wuauserv -Force -ErrorAction SilentlyContinue
Set-Service -Name wuauserv -StartupType Disabled -ErrorAction SilentlyContinue

Write-Host "   WARNING: Windows Update disabled. Re-enable later with:" -ForegroundColor Yellow
Write-Host "   Set-Service -Name wuauserv -StartupType Automatic" -ForegroundColor Yellow

Write-Host "[7/8] Disabling Scheduled Tasks (Non-Essential)..." -ForegroundColor Green

# Disable common scheduled tasks that cause notifications
$tasksToDisable = @(
    "\Microsoft\Windows\Application Experience\Microsoft Compatibility Appraiser",
    "\Microsoft\Windows\Application Experience\ProgramDataUpdater",
    "\Microsoft\Windows\Autochk\Proxy",
    "\Microsoft\Windows\Customer Experience Improvement Program\Consolidator",
    "\Microsoft\Windows\Customer Experience Improvement Program\UsbCeip",
    "\Microsoft\Windows\DiskDiagnostic\Microsoft-Windows-DiskDiagnosticDataCollector",
    "\Microsoft\Windows\Maintenance\WinSAT",
    "\Microsoft\Windows\Windows Error Reporting\QueueReporting"
)

foreach ($task in $tasksToDisable) {
    Disable-ScheduledTask -TaskName $task -ErrorAction SilentlyContinue
}

Write-Host "[8/8] Cleaning Up System Tray..." -ForegroundColor Green

# Kill system tray notification processes
$trayProcesses = @(
    "OneDrive",
    "Dropbox",
    "GoogleDrive",
    "iCloudServices",
    "SpotifyWebHelper",
    "AdobeNotificationClient",
    "CCXProcess",
    "Creative Cloud"
)

foreach ($proc in $trayProcesses) {
    Get-Process -Name $proc -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CLEANUP COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary of Changes:" -ForegroundColor Yellow
Write-Host "  - All notifications disabled" -ForegroundColor White
Write-Host "  - Email/communication apps stopped" -ForegroundColor White
Write-Host "  - Non-essential startup programs disabled" -ForegroundColor White
Write-Host "  - Non-essential Windows services disabled" -ForegroundColor White
Write-Host "  - Browser processes closed" -ForegroundColor White
Write-Host "  - Windows Update temporarily disabled" -ForegroundColor White
Write-Host "  - System tray cleaned up" -ForegroundColor White
Write-Host ""
Write-Host "Backup saved to: $backupFile" -ForegroundColor Cyan
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Restart Helios for all changes to take effect" -ForegroundColor White
Write-Host "2. After restart, only Docker and AI agent will run" -ForegroundColor White
Write-Host "3. To restore settings, run: restore_helios_settings.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to restart now, or Ctrl+C to restart later..." -ForegroundColor Yellow
pause

# Restart computer
Restart-Computer -Force
