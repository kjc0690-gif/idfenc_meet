@echo off
chcp 65001 >nul
echo ============================================
echo   GitHub 저장소 연결 시작합니다!
echo ============================================
echo.

REM 현재 배치파일이 있는 폴더에서 작업
cd /d "%~dp0"

if exist "idfenc_meet" (
    echo 이미 idfenc_meet 폴더가 있습니다. 최신 코드를 받습니다...
    cd idfenc_meet
    git pull
) else (
    echo GitHub에서 코드를 받는 중...
    git clone https://github.com/kjc0690-gif/idfenc_meet.git
    cd idfenc_meet
)

echo.
echo ============================================
echo   완료! 이제 클로드 코드를 실행합니다.
echo ============================================
echo.
claude
pause
