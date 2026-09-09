# demo/scripts/verify-s5.ps1
. "$PSScriptRoot\lib.ps1"
Set-Location "$PSScriptRoot\.."
docker compose up -d --build | Out-Null
Wait-Http http://localhost:8081/actuator/health 180 | Out-Null
Wait-Http http://localhost:8000/health 60 | Out-Null
Wait-Http http://localhost:9090/-/healthy 60 | Out-Null
Wait-Http http://localhost:3000/api/health 60 | Out-Null

# S5.1: Prometheus labels
$q = 'count by (service_name) (http_server_request_duration_seconds_count)'
$labels = (curl.exe -s -G localhost:9090/api/v1/query --data-urlencode "query=$q" | ConvertFrom-Json).data.result | % { $_.metric.service_name }
Assert-True ($labels -contains "order-service") "prometheus has order-service"
Assert-True ($labels -contains "processing-service") "prometheus has processing-service"
Assert-True ($labels -contains "persistence-service") "prometheus has persistence-service"

# S5.3: Grafana dashboard panels
docker compose restart grafana | Out-Null; Start-Sleep 8
$panels = (curl.exe -s localhost:3000/api/dashboards/uid/demo-services | ConvertFrom-Json).dashboard.panels.Count
Assert-True ($panels -eq 3) "grafana dashboard has 3 panels"

# S5.5: TREND chat
.\scripts\load.ps1 -Count 15 | Out-Null; Start-Sleep 20
$out = curl.exe -s -N -X POST localhost:8000/chat -H "Content-Type: application/json" -d '{"session_id":"t","question":"is processing-service getting slower over time?"}'
Assert-True ($out -match '"intent":\s*"TREND"') "intent TREND"
Assert-True ($out -match '"unverified_numbers":\s*\[\]') "no unverified numbers"

# S5.6: eval
Push-Location ai-service; .\.venv\Scripts\pytest eval -k trend -q; $ok = $LASTEXITCODE -eq 0; Pop-Location
Assert-True $ok "eval trend passes"

Write-Host "SPRINT 5 GREEN" -ForegroundColor Green
