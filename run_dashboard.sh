#!/bin/bash

# A股智能分析系统 - Web界面启动脚本 (Linux/Mac)

echo "========================================"
echo "  A股智能分析系统 - Web界面启动器"
echo "========================================"
echo ""

# 检查是否安装了streamlit
if ! python -c "import streamlit" 2>/dev/null; then
    echo "❌ 未检测到Streamlit，正在安装..."
    pip install streamlit plotly pandas
    echo ""
fi

# 检查是否有日志文件
if [ ! -f logs/stock_analysis_*.log ]; then
    echo "⚠️  警告: 未找到分析日志"
    echo ""
    echo "建议先运行分析程序:"
    echo "    python main.py --stocks 601899,518880"
    echo ""
    echo "或直接启动界面查看空数据"
    echo ""
    read -p "按回车键继续..."
fi

echo "启动Streamlit界面..."
echo ""
echo "选择要启动的版本:"
echo "[1] 基础版 (streamlit_app.py)"
echo "[2] 专业版 (streamlit_dashboard.py) - 推荐"
echo ""
read -p "请输入选择 (1/2): " choice

if [ "$choice" = "1" ]; then
    echo ""
    echo "启动基础版界面..."
    python -m streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
elif [ "$choice" = "2" ]; then
    echo ""
    echo "启动专业版界面..."
    python -m streamlit run streamlit_dashboard.py --server.port 8501 --server.address 0.0.0.0
else
    echo ""
    echo "无效选择，启动专业版..."
    python -m streamlit run streamlit_dashboard.py --server.port 8501 --server.address 0.0.0.0
fi