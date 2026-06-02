@echo off
setlocal

cd /d "%~dp0"

git rev-parse --is-inside-work-tree >nul 2>nul
if errorlevel 1 (
    echo This folder is not a Git repository.
    pause
    exit /b 1
)

echo.
echo Recent commits:
git --no-pager log --oneline -8
echo.

git diff --quiet
if errorlevel 1 (
    echo Working tree has uncommitted changes.
    echo Please commit or save your changes before rollback.
    pause
    exit /b 1
)

git diff --cached --quiet
if errorlevel 1 (
    echo Git index has staged changes.
    echo Please commit or unstage your changes before rollback.
    pause
    exit /b 1
)

set "TARGET=HEAD"
set /p TARGET_INPUT=Enter commit hash to revert, or press Enter to revert the latest commit: 
if not "%TARGET_INPUT%"=="" set "TARGET=%TARGET_INPUT%"

echo.
echo This will create a NEW commit that reverts:
echo %TARGET%
echo.
set /p CONFIRM=Continue? Type Y to continue: 
if /i not "%CONFIRM%"=="Y" (
    echo Cancelled.
    pause
    exit /b 0
)

git revert --no-edit %TARGET%
if errorlevel 1 (
    echo Rollback failed. Please check Git conflict messages above.
    pause
    exit /b 1
)

echo.
echo Rollback commit created successfully.
set /p PUSH_NOW=Push rollback to origin/main now? Type Y to push: 
if /i "%PUSH_NOW%"=="Y" (
    git push origin main
    if errorlevel 1 (
        echo Push failed. You can run "git push origin main" later.
        pause
        exit /b 1
    )
)

echo Done.
pause
