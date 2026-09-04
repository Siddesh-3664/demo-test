# demo/scripts/verify-s3.ps1
. "$PSScriptRoot\lib.ps1"
Set-Location "$PSScriptRoot\.."
docker compose up -d --build | Out-Null
Wait-Http http://localhost:8081/actuator/health 180 | Out-Null
Wait-Http http://localhost:16686/api/services 60 | Out-Null
$r = Post-Order -Scenario slow
Assert-True ($r.Status -eq 201) "slow order -> 201"
Assert-True ($r.TraceId -match '^[0-9a-f]{32}$') "traceId returned ($($r.TraceId))"
Start-Sleep 6
$trace = (curl.exe -s "localhost:16686/api/traces/$($r.TraceId)" | ConvertFrom-Json).data[0]
Assert-True ($null -ne $trace) "trace found in Jaeger"
$services = $trace.processes.PSObject.Properties | ForEach-Object { $_.Value.serviceName } | Sort-Object -Unique
Assert-True ($services.Count -eq 3) "3 services in trace ($($services -join ','))"
$root = $trace.spans | Where-Object { $_.references.Count -eq 0 } | Select-Object -First 1
Assert-True ($root.duration -gt 2000000) "root span > 2s ($($root.duration) us)"
$wm = $trace.spans | Where-Object { ($_.tags | Where-Object { $_.key -eq 'server.address' -and $_.value -eq 'wiremock' }) }
Assert-True ($null -ne $wm) "client span to wiremock present"
Write-Host "SPRINT 3 GREEN" -ForegroundColor Green
