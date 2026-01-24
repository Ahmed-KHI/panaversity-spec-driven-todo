# Inter Font Files

## Download Instructions

Download the following Inter font files from https://rsms.me/inter/ or use the direct links below:

### Required Files:
1. **Inter-Regular.woff2** (Regular 400)
   - Direct link: https://github.com/rsms/inter/raw/master/docs/font-files/Inter-Regular.woff2

2. **Inter-Medium.woff2** (Medium 500)
   - Direct link: https://github.com/rsms/inter/raw/master/docs/font-files/Inter-Medium.woff2

3. **Inter-Bold.woff2** (Bold 700)
   - Direct link: https://github.com/rsms/inter/raw/master/docs/font-files/Inter-Bold.woff2

### Quick Download (PowerShell):
```powershell
# Run from the frontend directory
Invoke-WebRequest -Uri "https://github.com/rsms/inter/raw/master/docs/font-files/Inter-Regular.woff2" -OutFile "public/fonts/Inter-Regular.woff2"
Invoke-WebRequest -Uri "https://github.com/rsms/inter/raw/master/docs/font-files/Inter-Medium.woff2" -OutFile "public/fonts/Inter-Medium.woff2"
Invoke-WebRequest -Uri "https://github.com/rsms/inter/raw/master/docs/font-files/Inter-Bold.woff2" -OutFile "public/fonts/Inter-Bold.woff2"
```

### Alternative: Variable Font (Smaller Size)
```powershell
# Download the variable font (recommended - single file for all weights)
Invoke-WebRequest -Uri "https://github.com/rsms/inter/raw/master/docs/font-files/InterVariable.woff2" -OutFile "public/fonts/InterVariable.woff2"
```

## License
Inter is licensed under the SIL Open Font License 1.1
https://github.com/rsms/inter/blob/master/LICENSE.txt
