# demo/scripts/load.ps1  — usage: .\scripts\load.ps1 -Count 20
param([int]$Count = 20, [int]$SlowPct = 20, [int]$FailPct = 10)
. "$PSScriptRoot\lib.ps1"
$results = @()
1..$Count | ForEach-Object {
  $roll = Get-Random -Minimum 0 -Maximum 100
  $scenario = if ($roll -lt $FailPct) { "fail" } elseif ($roll -lt $FailPct + $SlowPct) { "slow" } else { "fast" }
  $r = Post-Order -Scenario $scenario
  $results += [pscustomobject]@{ Scenario = $scenario; Status = $r.Status; Ms = $r.ElapsedMs; TraceId = $r.TraceId }
  Write-Host ("{0,-5} {1} {2,6} ms {3}" -f $scenario, $r.Status, $r.ElapsedMs, $r.TraceId)
}
$results | ConvertTo-Json | Set-Content "$PSScriptRoot\last-load.json"
