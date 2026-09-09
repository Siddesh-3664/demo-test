# demo/scripts/verify-s4.ps1
. "$PSScriptRoot\lib.ps1"
Set-Location "$PSScriptRoot\.."
docker compose up -d --build | Out-Null
Wait-Http http://localhost:8081/actuator/health 180 | Out-Null
Wait-Http http://localhost:8000/health 60 | Out-Null
$tags = curl.exe -s localhost:11434/api/tags
Assert-True ($tags -match "qwen3:8b") "ollama has qwen3:8b"
$r = Post-Order -Scenario slow; Start-Sleep 6
$out = curl.exe -s -N -X POST localhost:8000/chat -H "Content-Type: application/json" -d ('{"session_id":"v","question":"why was ' + $r.TraceId + ' slow?"}')
Assert-True ($out -match "processing-service") "answer names processing-service"
Assert-True ($out -match '"intent":\s*"WHY_SLOW"') "intent WHY_SLOW"
Assert-True ($out -match '"unverified_numbers":\s*\[\]') "no unverified numbers"
Push-Location ai-service; .\.venv\Scripts\pytest eval -q -k "trace or slowest or unknown or budget"; $ok = $LASTEXITCODE -eq 0; Pop-Location
Assert-True $ok "eval v0 passes"
Write-Host "SPRINT 4 GREEN" -ForegroundColor Green
