@echo off
chcp 65001 >nul
echo ========================================
echo   电商运营分析平台 - 启动器
echo   E-commerce Analytics Dashboard
echo ========================================
echo.

cd /d "%~dp0"

echo [1/2] 检查依赖...
pip list | findstr "streamlit" >nul
if errorlevel 1 (
    echo [!] Streamlit 未安装，正在安装...
    pip install -r requirements.txt
) else (
    echo [OK] 依赖已安装
)

echo.
echo [2/2] 启动应用...
echo 浏览器将自动打开 http://localhost:8501
echo 按 Ctrl+C 可停止服务
echo.

streamlit run dashboard.py

pause
