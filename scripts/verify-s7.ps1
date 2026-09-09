# demo/scripts/verify-s7.ps1
. "$PSScriptRoot\lib.ps1"
Set-Location "$PSScriptRoot\.."

# Build frontend
Push-Location frontend
npm run build
$buildOk = $LASTEXITCODE -eq 0
Pop-Location
Assert-True $buildOk "frontend build succeeds"
Assert-True (Test-Path "frontend\dist\index.html") "dist/index.html exists"

# CORS preflight on order-service
$code1 = curl.exe -s -o NUL -w "%{http_code}" -X OPTIONS localhost:8081/orders -H "Origin: http://localhost:5173" -H "Access-Control-Request-Method: POST"
Assert-True ($code1 -eq "200") "order-service CORS preflight 200"

# CORS preflight on ai-service /chat
$code2 = curl.exe -s -o NUL -w "%{http_code}" -X OPTIONS localhost:8000/chat -H "Origin: http://localhost:5173" -H "Access-Control-Request-Method: POST"
Assert-True ($code2 -eq "200") "ai-service CORS preflight 200"

Write-Host "SPRINT 7 GREEN" -ForegroundColor Green
