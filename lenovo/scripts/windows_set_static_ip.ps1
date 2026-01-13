$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest

$iface = Read-Host "InterfaceAlias (exact name from Get-NetAdapter)"
$ip = Read-Host "Static IP (e.g. 192.168.1.50)"
$prefix = Read-Host "PrefixLength (e.g. 24 for 255.255.255.0)"
$gw = Read-Host "Default Gateway (e.g. 192.168.1.1)"
$dns1 = Read-Host "DNS1 (e.g. 1.1.1.1)"
$dns2 = Read-Host "DNS2 (e.g. 8.8.8.8)"

# Remove existing IPv4 addresses on that interface (careful but deterministic)
Get-NetIPAddress -InterfaceAlias $iface -AddressFamily IPv4 -ErrorAction SilentlyContinue | `
  Where-Object {$_.IPAddress -notlike "169.254*"} | `
  ForEach-Object { Remove-NetIPAddress -InterfaceAlias $iface -IPAddress $_.IPAddress -Confirm:$false -ErrorAction SilentlyContinue }

New-NetIPAddress -InterfaceAlias $iface -IPAddress $ip -PrefixLength ([int]$prefix) -DefaultGateway $gw | Out-Null
Set-DnsClientServerAddress -InterfaceAlias $iface -ServerAddresses @($dns1,$dns2) | Out-Null

Write-Host "Static IP configured: $ip/$prefix via $gw"
Write-Host "DNS: $dns1, $dns2"
