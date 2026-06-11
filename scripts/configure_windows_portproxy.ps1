param(
    [string]$ListenAddress = "0.0.0.0",
    [int[]]$Ports = @(80, 443, 8080)
)

$wslIp = (wsl.exe hostname -I).Trim().Split(" ", [System.StringSplitOptions]::RemoveEmptyEntries)[0]
if (-not $wslIp) {
    throw "Could not detect the WSL IP address. Start WSL and try again."
}

Write-Host "Forwarding Windows ports to WSL IP $wslIp"

foreach ($port in $Ports) {
    netsh interface portproxy delete v4tov4 listenaddress=$ListenAddress listenport=$port | Out-Null
    netsh interface portproxy add v4tov4 listenaddress=$ListenAddress listenport=$port connectaddress=$wslIp connectport=$port

    $ruleName = "MeiDuo Mall port $port"
    Remove-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
    New-NetFirewallRule `
        -DisplayName $ruleName `
        -Direction Inbound `
        -Action Allow `
        -Protocol TCP `
        -LocalPort $port | Out-Null
}

Write-Host ""
Write-Host "Done. Use this Windows IP from other devices:"
Get-NetIPAddress -AddressFamily IPv4 |
    Where-Object {
        $_.IPAddress -notlike "169.254*" -and
        $_.IPAddress -ne "127.0.0.1" -and
        $_.InterfaceAlias -notlike "*WSL*"
    } |
    Select-Object InterfaceAlias, IPAddress, PrefixLength |
    Format-Table -AutoSize

Write-Host "Map www.meiduo.site to that Windows IP on each client device or in your router DNS."
