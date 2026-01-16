# ========================================
# Helios Settings Restore Script
# Restores normal Windows settings
# Run as Administrator
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Helios Settings Restore Script" -ForegroundColor Cyan
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

Write-Host "[1/5] Re-enabling Windows Notifications..." -ForegroundColor Green

# Re-enable notifications
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\PushNotifications" -Name "ToastEnabled" -Value 1 -Force
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Notifications\Settings" -Name "NOC_GLOBAL_SETTING_ALLOW_NOTIFICATION_SOUND" -Value 1 -Force
Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Notifications\Settings" -Name "NOC_GLOBAL_SETTING_ALLOW_TOASTS_ABOVE_LOCK" -Value 1 -Force

# Re-enable notification center
Remove-ItemProperty -Path "HKCU:\Software\Policies\Microsoft\Windows\Explorer" -Name "DisableNotificationCenter" -Force -ErrorAction SilentlyContinue

Write-Host "[2/5] Re-enabling Windows Services..." -ForegroundColor Green

# Re-enable services
$servicesToEnable = @(
    "WSearch",              # Windows Search
    "SysMain",              # Superfetch
    "wuauserv"              # Windows Update
)

foreach ($service in $servicesToEnable) {
    $svc = Get-Service -Name $service -ErrorAction SilentlyContinue
    if ($svc) {
        Set-Service -Name $service -StartupType Automatic -ErrorAction SilentlyContinue
        Start-Service -Name $service -ErrorAction SilentlyContinue
        Write-Host "   Enabled: $service" -ForegroundColor Gray
    }
}

Write-Host "[3/5] Re-enabling Windows Update..." -ForegroundColor Green

Set-Service -Name wuauserv -StartupType Automatic -ErrorAction SilentlyContinue
Start-Service -Name wuauserv -ErrorAction SilentlyContinue

Write-Host "[4/5] Re-enabling Scheduled Tasks..." -ForegroundColor Green

# Re-enable scheduled tasks
$tasksToEnable = @(
    "\Microsoft\Windows\Application Experience\Microsoft Compatibility Appraiser",
    "\Microsoft\Windows\Application Experience\ProgramDataUpdater",
    "\Microsoft\Windows\Autochk\Proxy",
    "\Microsoft\Windows\Customer Experience Improvement Program\Consolidator",
    "\Microsoft\Windows\Customer Experience Improvement Program\UsbCeip",
    "\Microsoft\Windows\DiskDiagnostic\Microsoft-Windows-DiskDiagnosticDataCollector",
    "\Microsoft\Windows\Maintenance\WinSAT",
    "\Microsoft\Windows\Windows Error Reporting\QueueReporting"
)

foreach ($task in $tasksToEnable) {
    Enable-ScheduledTask -TaskName $task -ErrorAction SilentlyContinue
}

Write-Host "[5/5] Checking for Startup Backup..." -ForegroundColor Green

$backupFile = "$env:USERPROFILE\Desktop\helios_startup_backup.txt"
if (Test-Path $backupFile) {
    Write-Host "   Startup backup found: $backupFile" -ForegroundColor Yellow
    Write-Host "   Review this file to manually restore startup programs if needed" -ForegroundColor Yellow
} else {
    Write-Host "   No startup backup found" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RESTORE COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary of Changes:" -ForegroundColor Yellow
Write-Host "  - Notifications re-enabled" -ForegroundColor White
Write-Host "  - Windows services restored" -ForegroundColor White
Write-Host "  - Windows Update re-enabled" -ForegroundColor White
Write-Host "  - Scheduled tasks restored" -ForegroundColor White
Write-Host ""
Write-Host "NOTE: Startup programs must be restored manually from backup" -ForegroundColor Yellow
Write-Host "Backup location: $backupFile" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to restart now, or Ctrl+C to restart later..." -ForegroundColor Yellow
pause

# Restart computer
Restart-Computer -Force
