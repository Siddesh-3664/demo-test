# demo/scripts/verify-s6.ps1
. "$PSScriptRoot\lib.ps1"
Set-Location "$PSScriptRoot\.."
docker compose up -d --build | Out-Null
Wait-Http http://localhost:8081/actuator/health 180 | Out-Null
Wait-Http http://localhost:8000/health 60 | Out-Null
Wait-Http http://localhost:3100/ready 60 | Out-Null

# S6.1: Loki has the ERROR line for a failed trace
$r = Post-Order -Scenario fail; Start-Sleep 10
$q = '{service_name="processing-service"} | trace_id="' + $r.TraceId + '"'
$res = curl.exe -s -G localhost:3100/loki/api/v1/query_range --data-urlencode "query=$q" --data-urlencode "since=10m" | ConvertFrom-Json
$found = $res.data.result.values | % { $_[1] } | Select-String "Third-party enrich failed"
Assert-True ($null -ne $found) "loki has the ERROR line"

# S6.4: WHY_FAIL chat
$out = curl.exe -s -N -X POST localhost:8000/chat -H "Content-Type: application/json" -d ('{"session_id":"f","question":"why did ' + $r.TraceId + ' fail?"}')
Assert-True ($out -match "processing-service") "answer names processing-service"
Assert-True ($out -match '"intent":\s*"WHY_FAIL"') "intent WHY_FAIL"
Assert-True ($out -match '"unverified_numbers":\s*\[\]') "no unverified numbers"

# S6.5: eval
Push-Location ai-service; .\.venv\Scripts\pytest eval -k "fail or trace or slowest or trend" -q; $ok = $LASTEXITCODE -eq 0; Pop-Location
Assert-True $ok "eval passes"

Write-Host "SPRINT 6 GREEN" -ForegroundColor Green
