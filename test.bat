@echo off
REM VOIDLABS - Automated Test Script for Windows
REM This script runs the complete test suite

color 0A
title VOIDLABS Test Suite

echo.
echo ========================================================
echo   VOIDLABS - AUTOMATED TEST SUITE
echo ========================================================
echo.

REM Check if node is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo [INFO] Node.js found. Starting tests...
echo.

REM Run the test suite
node scripts/test.js

REM Check test result
if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] All tests passed! Ready for deployment.
    echo.
) else (
    echo.
    echo [FAILURE] Some tests failed. Review the output above.
    echo.
)

pause
