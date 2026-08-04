# tryworld-koubo · 成片交付邮件通知（Windows PowerShell）
# 用法: powershell -File scripts/notify_delivery.ps1 -ProjectDir <项目目录> [-DryRun]
param(
  [string]$ProjectDir = (Get-Location).Path,
  [string]$Recipient = "",
  [switch]$DryRun
)
$ErrorActionPreference = "Stop"

$qqCandidates = @(
  (Join-Path $env:USERPROFILE ".agents\skills\qq-email"),
  (Join-Path $env:USERPROFILE ".codex\skills\qq-email")
)
$qqEmailSkill = $qqCandidates | Where-Object { Test-Path -LiteralPath (Join-Path $_ "scripts\send.js") } | Select-Object -First 1
if (-not $qqEmailSkill) {
  Write-Warning "未找到 qq-email 技能(请安装到 ~/.agents/skills 或 ~/.codex/skills),跳过邮件通知(不阻塞交付)。"
  exit 0
}
$sendJs = Join-Path $qqEmailSkill "scripts\send.js"
$VideoAttachLimitMB = 35   # QQ 邮箱附件上限约 50MB,含 base64 开销,单文件安全阈值 35MB

# ---- 收集产物 ----
$out = Join-Path $ProjectDir "outputs"
if (-not (Test-Path -LiteralPath $out)) { Write-Warning ("未找到 outputs: " + $out); exit 0 }
$video = Get-ChildItem -LiteralPath $out -Filter *.mp4 -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $video) { Write-Warning ("outputs 中无成片 mp4,跳过邮件通知: " + $out); exit 0 }
$coverH = Get-ChildItem -LiteralPath $out -Filter "*cover_4x3*.png" -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $coverH) { $coverH = Get-ChildItem -LiteralPath $out -Filter "*封面*4x3*.png" -ErrorAction SilentlyContinue | Select-Object -First 1 }
$coverV = Get-ChildItem -LiteralPath $out -Filter "*cover_3x4*.png" -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $coverV) { $coverV = Get-ChildItem -LiteralPath $out -Filter "*封面*3x4*.png" -ErrorAction SilentlyContinue | Select-Object -First 1 }
if (-not $coverH -or -not $coverV) {
  $pngs = Get-ChildItem -LiteralPath $out -Filter *.png -ErrorAction SilentlyContinue | Select-Object -First 2
  $coverH = $pngs[0]; $coverV = $pngs[1]
}
$titles = Get-ChildItem -LiteralPath $out -Filter "titles.txt" -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $titles) { $titles = Get-ChildItem -LiteralPath $out -Filter "*标题*.txt" -ErrorAction SilentlyContinue | Select-Object -First 1 }

# 平台标题改为直接写进正文,不再作为附件
$titlesText = ""
if ($titles) { $titlesText = (Get-Content -LiteralPath $titles.FullName -Encoding UTF8 -Raw).Trim() }

# 视频按大小决定是否附带(QQ 邮箱附件上限)
$videoAttach = $null
$videoNote = ""
if ($video.Length -le ($VideoAttachLimitMB * 1MB)) {
  $videoAttach = $video.FullName
} else {
  $videoNote = "主视频约 " + [math]::Round($video.Length / 1MB, 1) + " MB,超出邮箱附件上限,未随邮件发送(文件名: " + $video.Name + ")。"
}
$attachLabel = "横版封面 / 竖版封面"
if ($videoAttach) { $attachLabel = "主视频 / 横版封面 / 竖版封面" }
$attachments = @($videoAttach, $coverH.FullName, $coverV.FullName) | Where-Object { $_ -and (Test-Path -LiteralPath $_) }

$proj = Split-Path -Leaf $ProjectDir
$date = Get-Date -Format "yyyy-MM-dd"
$subject = "✅ TryWorld 口播成片已交付 · $proj · $date"
$body = @"
成片已交付，产物已作为附件随邮件发送：

【附件】$attachLabel
$videoNote
【平台标题】
$titlesText

【四平台发布计划】
小红书：中午 12:30
抖音：晚上 19:30
B站：晚上 20:30
微信视频号：晚上 20:30

—— tryworld-koubo 自动通知
"@

if ($DryRun) {
  Write-Output "===== DRY RUN: 邮件内容预览 ====="
  Write-Output ("收件人: " + $(if ($Recipient) { $Recipient } else { "<QQ_EMAIL_ACCOUNT>" }))
  Write-Output ("主题: " + $subject)
  Write-Output "----- 附件 -----"
  $attachments | ForEach-Object { Write-Output ("  - " + $_) }
  Write-Output "----- 正文 -----"
  Write-Output $body
  exit 0
}

# ---- 凭证检查(进程环境变量 -> 注册表用户环境变量) ----
if (-not $env:QQ_EMAIL_ACCOUNT) {
  try { $reg = Get-ItemProperty -Path "HKCU:\Environment" -Name QQ_EMAIL_ACCOUNT -ErrorAction Stop; $env:QQ_EMAIL_ACCOUNT = $reg.QQ_EMAIL_ACCOUNT } catch { }
}
if (-not $env:QQ_EMAIL_AUTH_CODE) {
  try { $reg = Get-ItemProperty -Path "HKCU:\Environment" -Name QQ_EMAIL_AUTH_CODE -ErrorAction Stop; $env:QQ_EMAIL_AUTH_CODE = $reg.QQ_EMAIL_AUTH_CODE } catch { }
}
if (-not $env:QQ_EMAIL_ACCOUNT -or -not $env:QQ_EMAIL_AUTH_CODE) {
  Write-Warning "未配置 QQ_EMAIL_ACCOUNT / QQ_EMAIL_AUTH_CODE(环境变量或注册表均无),跳过邮件通知(不阻塞交付)。"
  Write-Warning "配置方法: setx QQ_EMAIL_ACCOUNT \"你的邮箱\" 和 setx QQ_EMAIL_AUTH_CODE \"IMAP/SMTP授权码\",重开终端生效。"
  exit 0
}
if (-not (Test-Path -LiteralPath $sendJs)) { Write-Warning ("qq-email send.js 不存在: " + $sendJs); exit 0 }
if ($Recipient -eq "") { $Recipient = $env:QQ_EMAIL_ACCOUNT }

Write-Output "正在发送成片通知邮件 ..."

# 用 .NET Process 直连 node：参数 UTF-16、正文 UTF-8 字节写 stdin、附件 --attach 传路径，避免 PowerShell 5.1 编码转换乱码
$node = (Get-Command node).Source
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $node
$psi.UseShellExecute = $false
$psi.RedirectStandardInput = $true
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.StandardOutputEncoding = [System.Text.Encoding]::UTF8
$psi.StandardErrorEncoding = [System.Text.Encoding]::UTF8
$attachArgs = ""
foreach ($a in $attachments) { $attachArgs += ' --attach "' + $a + '"' }
$psi.Arguments = '"' + $sendJs + '" "' + $Recipient + '" "' + $subject + '" --stdin' + $attachArgs
$proc = [System.Diagnostics.Process]::Start($psi)
$bytes = [System.Text.Encoding]::UTF8.GetBytes($body)
$proc.StandardInput.BaseStream.Write($bytes, 0, $bytes.Length)
$proc.StandardInput.Close()
$stdout = $proc.StandardOutput.ReadToEnd()
$stderr = $proc.StandardError.ReadToEnd()
$proc.WaitForExit()
if ($proc.ExitCode -ne 0) { Write-Error ("邮件发送失败: " + $stderr.Trim()); exit 1 }
Write-Output $stdout.Trim()
Write-Output "邮件通知完成。"