# Download Inter fonts
Write-Host "Downloading fonts..." -ForegroundColor Cyan
$dir = "public/fonts"
New-Item -ItemType Directory -Path $dir -Force | Out-Null

Invoke-WebRequest "https://github.com/rsms/inter/raw/master/docs/font-files/Inter-Regular.woff2" -OutFile "$dir/Inter-Regular.woff2" -UseBasicParsing
Invoke-WebRequest "https://github.com/rsms/inter/raw/master/docs/font-files/Inter-Medium.woff2" -OutFile "$dir/Inter-Medium.woff2" -UseBasicParsing
Invoke-WebRequest "https://github.com/rsms/inter/raw/master/docs/font-files/Inter-Bold.woff2" -OutFile "$dir/Inter-Bold.woff2" -UseBasicParsing

Write-Host "Fonts downloaded!" -ForegroundColor Green
