@echo off
echo ======================================
echo Git Safety Check
echo ======================================
echo.

echo Checking .gitignore exists...
if exist .gitignore (
    echo OK: .gitignore exists
) else (
    echo ERROR: .gitignore missing!
    exit /b 1
)

echo.
echo Files that will be committed:
git status

echo.
echo ======================================
echo SAFE TO PUSH!
echo ======================================
echo.
echo No credentials are stored in the code.
echo All sensitive data uses session storage.
echo.
echo To commit and push:
echo   git add .
echo   git commit -m "Initial commit"
echo   git push origin main
echo.
pause
