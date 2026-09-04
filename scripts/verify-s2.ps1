# demo/scripts/verify-s2.ps1
. "$PSScriptRoot\lib.ps1"
Set-Location "$PSScriptRoot\.."
docker compose up -d --build wiremock processing-service order-service | Out-Null
Wait-Http http://localhost:8081/actuator/health 180 | Out-Null
$f = Post-Order -Scenario fast;  Assert-True ($f.Status -eq 201 -and $f.ElapsedMs -lt 1500) "fast -> 201 in $($f.ElapsedMs)ms"
$s = Post-Order -Scenario slow;  Assert-True ($s.Status -eq 201 -and $s.ElapsedMs -ge 2000) "slow -> 201 in $($s.ElapsedMs)ms"
$x = Post-Order -Scenario fail;  Assert-True ($x.Status -eq 502) "fail -> 502"
$log = docker compose logs --since 2m processing-service | Select-String "Third-party enrich failed"
Assert-True ($null -ne $log) "ERROR log line present"
Write-Host "SPRINT 2 GREEN" -ForegroundColor Green
