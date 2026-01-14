@echo off
chcp 65001 >nul
echo ========================================
echo  A股智能分析系统 - Streamlit 启动器
echo  使用 uv 虚拟环境
echo ========================================
echo.

REM 检查虚拟环境是否存在
if not exist ".venv\Scripts\python.exe" (
    echo  ❌ 虚拟环境不存在，请先运行: uv pip install -r requirements-complete.txt
    pause
    exit /b 1
)

REM 检查是否有日志文件
if not exist "logs\stock_analysis_*.log" (
    echo  ⚠️  警告: 未找到分析日志
    echo.
    echo  建议先运行分析程序:
    echo     .venv\Scripts\python.exe main.py --stocks 601899,518880
    echo.
    echo  或直接启动界面查看空数据
    echo.
    pause
)

echo  选择要启动的版本:
echo  [1] 基础版 (streamlit_app.py)
echo  [2] 专业版 (streamlit_dashboard.py) - 推荐
echo.
set /p choice="请输入选择 (1/2): "

if "%choice%"=="1" (
    echo.
    echo  启动基础版界面...
    .venv\Scripts\python.exe -m streamlit run streamlit_app.py --server.port 8501
) else if "%choice%"=="2" (
    echo.
    echo  启动专业版界面...
    .venv\Scripts\python.exe -m streamlit run streamlit_dashboard.py --server.port 8501
) else (
    echo.
    echo  无效选择，启动专业版...
    .venv\Scripts\python.exe -m streamlit run streamlit_dashboard.py --server.port 8501
)

pause