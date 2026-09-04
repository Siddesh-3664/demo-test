# demo/scripts/lib.ps1
$ErrorActionPreference = "Stop"

function Wait-Http {
  param([string]$Url, [int]$TimeoutSec = 90)
  $deadline = (Get-Date).AddSeconds($TimeoutSec)
  while ((Get-Date) -lt $deadline) {
    try { $r = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 3; if ($r.StatusCode -lt 500) { return $true } } catch {}
    Start-Sleep 2
  }
  throw "Timeout waiting for $Url"
}

function Post-Order {
  param([string]$Scenario = "fast", [string]$Item = "widget", [int]$Quantity = 2)
  $body = @{ item = $Item; quantity = $Quantity } | ConvertTo-Json -Compress
  $headers = @{ "Content-Type" = "application/json"; "X-Scenario" = $Scenario }
  $sw = [Diagnostics.Stopwatch]::StartNew()
  try {
    $r = Invoke-WebRequest -Uri "http://localhost:8081/orders" -Method POST -Body $body -Headers $headers -UseBasicParsing -TimeoutSec 30
    $status = $r.StatusCode; $content = $r.Content
  } catch {
    $status = [int]$_.Exception.Response.StatusCode
    $content = (New-Object IO.StreamReader($_.Exception.Response.GetResponseStream())).ReadToEnd()
  }
  $sw.Stop()
  $json = $null; try { $json = $content | ConvertFrom-Json } catch {}
  return [pscustomobject]@{ Status = $status; ElapsedMs = $sw.ElapsedMilliseconds; TraceId = $json.traceId; OrderId = $json.orderId; Raw = $content }
}

function Assert-True {
  param([bool]$Condition, [string]$Message)
  if (-not $Condition) { Write-Host "FAIL: $Message" -ForegroundColor Red; exit 1 }
  Write-Host "ok: $Message" -ForegroundColor Green
}

function Pg-Count {
  $out = docker compose exec -T postgres psql -U demo -d demo -tAc "select count(*) from orders"
  return [int]($out.Trim())
}
