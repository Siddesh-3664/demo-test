# demo/scripts/demo.ps1
. "$PSScriptRoot\lib.ps1"
Set-Location "$PSScriptRoot\.."
docker compose up -d --build | Out-Null
Wait-Http http://localhost:8081/actuator/health 180 | Out-Null
Wait-Http http://localhost:8000/health 60 | Out-Null
Wait-Http http://localhost:16686 60 | Out-Null
Wait-Http http://localhost:3000/api/health 60 | Out-Null
.\scripts\load.ps1 -Count 20 | Out-Null
Write-Host ""
Write-Host "Demo ready!" -ForegroundColor Green
Write-Host "  Frontend:  http://localhost:5173  (run 'npm run dev' in frontend/)"
Write-Host "  Jaeger:    http://localhost:16686"
Write-Host "  Grafana:   http://localhost:3000/d/demo-services"
Write-Host "  AI API:    http://localhost:8000/health"
