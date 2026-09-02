# AIHOT 口播选题 · 数据拉取脚本（Windows PowerShell）
# 拉最近 N 天精选 + 最新日报，落盘 UTF-8 报告与原始 JSON。
param(
  [int]$Days = 7,
  [int]$Take = 100,
  [string]$OutDir = "work/aihot",
  [string]$BaseUrl = "https://aihot.virxact.com"
)
$ErrorActionPreference = "Stop"
$UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
$base = $BaseUrl

function Get-U8($url) {
  for ($try = 1; $try -le 3; $try++) {
    try {
      $wc = New-Object System.Net.WebClient
      $wc.Headers.Add("User-Agent", $UA)
      $wc.Encoding = [System.Text.Encoding]::UTF8
      return ($wc.DownloadString($url) | ConvertFrom-Json)
    } catch {
      $status = 0
      if ($_.Exception.Response) { $status = [int]$_.Exception.Response.StatusCode }
      if (($try -lt 3) -and ($status -eq 429 -or $status -ge 500)) {
        Write-Warning ("限流/服务端错误($status)，{0}s 后重试..." -f ($try * 2))
        Start-Sleep -Seconds ($try * 2)
      } else {
        throw
      }
    }
  }
}

New-Item -ItemType Directory -Path $OutDir -Force | Out-Null

$daily = $null
try { $daily = Get-U8 "$base/api/public/daily" } catch { Write-Warning "daily 拉取失败: $($_.Exception.Message)" }
$since = (Get-Date).AddDays(-$Days).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$items = $null
try { $items = Get-U8 "$base/api/public/items?mode=selected&since=$since&take=$Take" } catch { Write-Warning "items 拉取失败: $($_.Exception.Message)" }

if ($daily) { $daily | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $OutDir "daily.json") -Encoding UTF8 }
if ($items) { $items | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $OutDir "items.json") -Encoding UTF8 }

$sb = New-Object System.Text.StringBuilder
[void]$sb.AppendLine("AIHOT 口播选题素材 | 拉取时间: " + (Get-Date).ToString("yyyy-MM-dd HH:mm") + "（北京时间）")
[void]$sb.AppendLine("时间窗: 最近 $Days 天 | 精选条数: " + @($items.items).Count)
if ($daily -and $daily.date) {
  [void]$sb.AppendLine("最新日报: " + $daily.date)
  if ($daily.lead) { [void]$sb.AppendLine("头条: " + $daily.lead.title) }
  foreach ($sec in @($daily.sections)) {
    [void]$sb.AppendLine("[" + $sec.label + "]")
    foreach ($it in @($sec.items)) { [void]$sb.AppendLine("  - " + $it.title + " | " + $it.sourceName) }
  }
  foreach ($f in @($daily.flashes)) { [void]$sb.AppendLine("  快讯: " + $f.title) }
}
[void]$sb.AppendLine("")
[void]$sb.AppendLine("== 精选条目（最近 $Days 天）==")
foreach ($it in @($items.items)) { [void]$sb.AppendLine("[" + $it.category + "] " + $it.title + " | " + $it.source) }
$report = Join-Path $OutDir "report.txt"
[System.IO.File]::WriteAllText($report, $sb.ToString(), (New-Object System.Text.UTF8Encoding $false))
Write-Output ("done | " + $report + " | 精选 " + @($items.items).Count + " 条")
