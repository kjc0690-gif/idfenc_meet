@echo off
chcp 65001 >nul
title Claude 작업기록 동기화

echo ========================================
echo   Claude 작업기록 자동 동기화
echo   %date% %time%
echo ========================================

set LOCAL_WORK=C:\Users\note\Desktop\클로드_작업기록
set LOCAL_SKILLS=C:\Users\note\.claude\skills
set GDRIVE_WORK=G:\내 드라이브\클로드작업기록
set PATH=%PATH%;C:\Program Files\GitHub CLI;C:\Program Files\Git\cmd

cd /d "%LOCAL_WORK%"

echo.
echo [1/4] GitHub에서 최신 자료 가져오기...
git pull origin master 2>nul
if %errorlevel% neq 0 (
    echo   경고: Pull 실패 - 네트워크 확인 필요
) else (
    echo   완료: GitHub Pull 성공
)

echo.
echo [2/4] G드라이브 → 로컬 동기화...
if exist "%GDRIVE_WORK%" (
    robocopy "%GDRIVE_WORK%\스킬백업" "%LOCAL_WORK%\스킬백업" /E /XO /NFL /NDL /NJH /NJS >nul 2>nul
    robocopy "%GDRIVE_WORK%\TBM" "%LOCAL_WORK%\TBM" /E /XO /NFL /NDL /NJH /NJS >nul 2>nul
    echo   완료: G드라이브 동기화 성공
) else (
    echo   건너뜀: G드라이브 미마운트
)

echo.
echo [3/4] 스킬 활성화...
set SKILL_COUNT=0
for /d %%D in ("%LOCAL_WORK%\스킬백업\*") do (
    xcopy "%%D" "%LOCAL_SKILLS%\%%~nxD" /E /Y /Q >nul 2>nul
    set /a SKILL_COUNT+=1
)
if exist "%LOCAL_WORK%\skills" (
    for /d %%D in ("%LOCAL_WORK%\skills\*") do (
        xcopy "%%D" "%LOCAL_SKILLS%\%%~nxD" /E /Y /Q >nul 2>nul
        set /a SKILL_COUNT+=1
    )
)
echo   완료: 스킬 활성화됨

echo.
echo [4/4] 로컬 → G드라이브 백업...
if exist "%GDRIVE_WORK%" (
    robocopy "%LOCAL_WORK%" "%GDRIVE_WORK%" /E /XO /NFL /NDL /NJH /NJS /XD .git >nul 2>nul
    for /d %%D in ("%LOCAL_SKILLS%\*") do (
        xcopy "%%D" "%GDRIVE_WORK%\스킬백업\%%~nxD" /E /Y /Q >nul 2>nul
    )
    echo   완료: G드라이브 백업 성공
) else (
    echo   건너뜀: G드라이브 미마운트
)

echo.
echo ========================================
echo   동기화 완료! %date% %time%
echo ========================================
echo.
echo 이 창은 10초 후 자동으로 닫힙니다...
timeout /t 10 /nobreak >nul
