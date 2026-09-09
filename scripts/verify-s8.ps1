# demo/scripts/verify-s8.ps1
. "$PSScriptRoot\lib.ps1"
Set-Location "$PSScriptRoot\.."
docker compose up -d --build | Out-Null
Wait-Http http://localhost:8081/actuator/health 180 | Out-Null
Wait-Http http://localhost:8000/health 60 | Out-Null
.\scripts\load.ps1 -Count 20 | Out-Null; Start-Sleep 20

# Run eval 5 times
Push-Location ai-service
$allOk = $true
1..5 | % {
    .\.venv\Scripts\pytest eval -q
    if ($LASTEXITCODE -ne 0) { Write-Host "RUN $_ FAILED" -ForegroundColor Red; $allOk = $false }
}
Pop-Location
Assert-True $allOk "eval passes 5x"

Write-Host "SPRINT 8 GREEN" -ForegroundColor Green
