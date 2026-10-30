# Detector'ni ishga tushirish: backend + frontend + Cloudflare tezkor tunnel
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$be = Join-Path $root "detector-backend"
$fe = Join-Path $root "detector-frontend"

Write-Host "1/3 Backend ishga tushyapti (port 8000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit","-Command","cd '$be'; .\venv\Scripts\Activate.ps1; uvicorn app.main:app --host 127.0.0.1 --port 8000"

Write-Host "2/3 Frontend ishga tushyapti (port 3000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit","-Command","cd '$fe'; npm start"

Start-Sleep -Seconds 8
Write-Host "3/3 Cloudflare tunnel ochilyapti. Pastda chiqadigan https://...trycloudflare.com havolasini boshqalarga bering." -ForegroundColor Green
& "C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --url http://localhost:3000
