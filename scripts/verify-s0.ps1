# demo/scripts/verify-s0.ps1
. "$PSScriptRoot\lib.ps1"
Set-Location "$PSScriptRoot\.."
docker compose config --quiet; Assert-True ($LASTEXITCODE -eq 0) "compose config valid"
docker compose up -d postgres | Out-Null
$health = docker compose ps postgres --format "{{.Health}}"
$deadline = (Get-Date).AddSeconds(60)
while ($health -ne "healthy" -and (Get-Date) -lt $deadline) { Start-Sleep 2; $health = docker compose ps postgres --format "{{.Health}}" }
Assert-True ($health -eq "healthy") "postgres healthy"
Assert-True (Test-Path "otel\opentelemetry-javaagent.jar") "otel agent jar present"
Write-Host "SPRINT 0 GREEN" -ForegroundColor Green
