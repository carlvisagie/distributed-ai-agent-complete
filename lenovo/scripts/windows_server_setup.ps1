$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

Write-Host "=== Lenovo Server Baseline (Windows) ==="

# ---- Identity (optional) ----
# Rename-Computer -NewName "LENOVO-SERVER" -Force

# ---- Power plan: prevent sleep/hibernate (servers must not sleep) ----
powercfg /setactive SCHEME_MIN
powercfg /change standby-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
powercfg /hibernate off

# ---- Enable Remote Desktop (RDP) ----
Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server' -Name 'fDenyTSConnections' -Value 0
Enable-NetFirewallRule -DisplayGroup "Remote Desktop"

# ---- Enable OpenSSH Server (SSH) ----
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0 | Out-Null
Start-Service sshd
Set-Service -Name sshd -StartupType Automatic
if (-not (Get-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -ErrorAction SilentlyContinue)) {
  New-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -DisplayName 'OpenSSH Server (sshd)' -Enabled True -Direction Inbound `
    -Protocol TCP -Action Allow -LocalPort 22 | Out-Null
} else {
  Enable-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' | Out-Null
}

# ---- Enable WSL2 + Virtualization platform ----
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart | Out-Null
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart | Out-Null

# ---- Basic inbound firewall tightening (keep what we explicitly enabled) ----
# NOTE: Do not "reset" firewall blindly on a machine you use daily. We only ensure needed rules are on.
Write-Host "Enabled: RDP + SSH inbound rules."

# ---- Create a local service user (optional but recommended) ----
# Change password after creation.
$svcUser = "svc_agentops"
if (-not (Get-LocalUser -Name $svcUser -ErrorAction SilentlyContinue)) {
  $pw = Read-Host "Create password for local user '$svcUser' (will not echo)" -AsSecureString
  New-LocalUser -Name $svcUser -Password $pw -PasswordNeverExpires:$true -AccountNeverExpires:$true | Out-Null
  Add-LocalGroupMember -Group "Administrators" -Member $svcUser
  Write-Host "Created local admin user: $svcUser"
} else {
  Write-Host "User exists: $svcUser"
}

Write-Host "`nNEXT:"
Write-Host "1) Reboot to finish WSL2 feature enablement."
Write-Host "2) Install Docker Desktop (WSL2 backend) or use a Linux VM."


# ---- Network Diagnostics ----
Write-Host "`n=== Network Configuration ==="
Write-Host "Network Adapters:"
Get-NetAdapter | Sort-Object Status -Descending | Format-Table -Auto Name,Status,LinkSpeed,MacAddress

Write-Host "`nIP Addresses:"
Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -notlike "169.254*"} | Format-Table -Auto InterfaceAlias,IPAddress,PrefixLength

Write-Host "`nDNS Servers:"
Get-DnsClientServerAddress -AddressFamily IPv4 | Format-Table -Auto InterfaceAlias,ServerAddresses
