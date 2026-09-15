@echo off
REM ============================================================
REM  render-win.bat — html-ppt 在 Windows 上的渲染/导出脚本
REM  替代原版 scripts/render.sh（Chrome 路径 mac 写死，Win 跑不了）
REM
REM  用法:
REM    render-win.bat <index.html>            出 PNG（第 1 页）
REM    render-win.bat <index.html> <N>        出 PNG（第 1..N 页）
REM    render-win.bat <index.html> pdf        导出 PDF（推荐，交付甲方用）
REM
REM  依赖: Google Chrome（自动探测常见安装路径）
REM ============================================================
setlocal enabledelayedexpansion

set "CHROME="
for %%P in (
  "C:\Program Files\Google\Chrome\Application\chrome.exe"
  "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
  "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
) do (
  if not defined CHROME if exist %%P set "CHROME=%%~P"
)
if not defined CHROME (
  echo [ERROR] 未找到 Chrome，请手动设置 CHROME 变量
  exit /b 1
)

set "FILE=%~1"
if "%FILE%"=="" (
  echo 用法: render-win.bat ^<index.html^> [N^|pdf]
  exit /b 1
)
if not exist "%FILE%" (
  echo [ERROR] 文件不存在: %FILE%
  exit /b 1
)

set "DIR=%~dp1"
set "STEM=%~n1"
set "MODE=%~2"
if "%MODE%"=="" set "MODE=1"

REM 独立 profile 目录，避免与本机 Chrome 冲突（关键！否则静默失败）
set "PROF=%DIR%.cprofile"

if /i "%MODE%"=="pdf" (
  set "OUT=%DIR%%STEM%.pdf"
  "%CHROME%" --headless=new --disable-gpu --no-sandbox ^
    --user-data-dir="%PROF%" --virtual-time-budget=5000 ^
    --no-pdf-header-footer --print-to-pdf="%OUT%" ^
    "file:///%FILE%" >nul 2>&1
  if exist "%OUT%" (echo [OK] PDF: %OUT%) else (echo [FAIL] PDF 未生成 & exit /b 1)
) else (
  set "OUTDIR=%DIR%png"
  if not exist "%OUTDIR%" mkdir "%OUTDIR%"
  set /a TOTAL=%MODE%
  set /a OK=0
  for /l %%i in (1,1,!TOTAL!) do (
    "%CHROME%" --headless=new --disable-gpu --hide-scrollbars --no-sandbox ^
      --user-data-dir="%PROF%" --virtual-time-budget=4500 ^
      --window-size=1920,1080 ^
      --screenshot="%OUTDIR%\%STEM%_%%i.png" ^
      "file:///%FILE%#/%%i" >nul 2>&1
    if exist "%OUTDIR%\%STEM%_%%i.png" (set /a OK+=1) else (echo [WARN] 第 %%i 页未生成)
  )
  echo [OK] PNG: !OK!/!TOTAL! 页 → %OUTDIR%
)

REM 清理临时 profile
if exist "%PROF%" rmdir /s /q "%PROF%" 2>nul

endlocal
