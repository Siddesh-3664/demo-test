# demo/scripts/verify-s1.ps1
. "$PSScriptRoot\lib.ps1"
Set-Location "$PSScriptRoot\.."
docker compose up -d --build postgres persistence-service processing-service order-service | Out-Null
Wait-Http http://localhost:8081/actuator/health 180 | Out-Null
$before = Pg-Count
1..3 | ForEach-Object { $r = Post-Order -Scenario fast; Assert-True ($r.Status -eq 201) "order $_ -> 201" }
$after = Pg-Count
Assert-True ($after -eq $before + 3) "3 rows written ($before -> $after)"
$bad = Post-Order -Item "" -Quantity 0
Assert-True ($bad.Status -eq 400) "validation -> 400"
Write-Host "SPRINT 1 GREEN" -ForegroundColor Green
