param(
    [switch]$Json
)

$ErrorActionPreference = "Continue"
$checks = New-Object System.Collections.Generic.List[object]

function Test-Executable {
    param([string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Add-Check {
    param(
        [string]$Name,
        [bool]$Ok,
        [string]$Detail,
        [switch]$Optional
    )
    $status = if ($Ok) { "OK" } elseif ($Optional) { "WARN" } else { "MISSING" }
    $checks.Add([pscustomobject]@{
        Name = $Name
        Status = $status
        Detail = $Detail
    })
}

$hasPython = Test-Executable "python"
Add-Check "Python" $hasPython $(if ($hasPython) { (& python --version 2>&1 | Out-String).Trim() } else { "python not found in PATH" })

$hasNode = Test-Executable "node"
Add-Check "Node.js" $hasNode $(if ($hasNode) { (& node --version 2>&1 | Out-String).Trim() } else { "node not found in PATH" })

$hasFfmpeg = Test-Executable "ffmpeg"
Add-Check "FFmpeg" $hasFfmpeg $(if ($hasFfmpeg) { "ffmpeg found in PATH" } else { "ffmpeg not found in PATH" })

$hasFfprobe = Test-Executable "ffprobe"
Add-Check "ffprobe" $hasFfprobe $(if ($hasFfprobe) { "ffprobe found in PATH" } else { "ffprobe not found in PATH" })

$edgeTts = $false
$edgeTtsDetail = "python not found; cannot import edge_tts"
if ($hasPython) {
    $importOutput = & python -c "import edge_tts" 2>&1
    $edgeTts = ($LASTEXITCODE -eq 0)
    if (-not $edgeTts -and $importOutput) {
        $edgeTtsDetail = "run: python -m pip install edge-tts"
    } elseif ($edgeTts) {
        $edgeTtsDetail = "edge_tts import succeeded"
    }
}
Add-Check "edge-tts" $edgeTts $edgeTtsDetail

$hasNpx = Test-Executable "npx"
$hyperframes = $false
$hyperframesDetail = "npx not found in PATH"
if ($hasNpx) {
    $hfOutput = & npx --no-install hyperframes --version 2>&1
    $hyperframes = ($LASTEXITCODE -eq 0)
    $hyperframesDetail = if ($hyperframes) { "hyperframes CLI resolved by npx" } else { "run: npx hyperframes, then verify with npx hyperframes doctor" }
}
Add-Check "hyperframes" $hyperframes $hyperframesDetail

$account = [Environment]::GetEnvironmentVariable("QQ_EMAIL_ACCOUNT", "Process")
if ([string]::IsNullOrWhiteSpace($account)) { $account = [Environment]::GetEnvironmentVariable("QQ_EMAIL_ACCOUNT", "User") }
$authCode = [Environment]::GetEnvironmentVariable("QQ_EMAIL_AUTH_CODE", "Process")
if ([string]::IsNullOrWhiteSpace($authCode)) { $authCode = [Environment]::GetEnvironmentVariable("QQ_EMAIL_AUTH_CODE", "User") }
$qqEmail = (-not [string]::IsNullOrWhiteSpace($account)) -and (-not [string]::IsNullOrWhiteSpace($authCode))
$qqEmailDetail = if ($qqEmail) { "QQ_EMAIL_ACCOUNT and QQ_EMAIL_AUTH_CODE are configured" } else { "configure with setx if delivery email is needed" }
Add-Check "QQ email credentials" $qqEmail $qqEmailDetail -Optional

if ($Json) {
    $checks | ConvertTo-Json -Depth 3
} else {
    $checks | Format-Table -AutoSize | Out-String -Width 200 | Write-Host
}

$missing = @($checks | Where-Object { $_.Status -eq "MISSING" })
if ($missing.Count -gt 0) {
    exit 1
}
exit 0