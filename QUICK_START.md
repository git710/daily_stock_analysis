# 🚀 快速启动指南

## ✅ 安装状态检查

```bash
# 查看 uv 虚拟环境
dir .venv\Scripts\python.exe

# 查看已安装的包
.venv\Scripts\python.exe -m pip list
```

## 🎯 启动方式

### Windows (推荐)
```bash
# 双击运行
run_streamlit.bat

# 或命令行
run_streamlit.bat
```

### Linux/Mac
```bash
chmod +x run_streamlit.sh
./run_streamlit.sh
```

### 手动启动
```bash
# 基础版
.venv\Scripts\python.exe -m streamlit run streamlit_app.py --server.port 8501

# 专业版（推荐）
.venv\Scripts\python.exe -m streamlit run streamlit_dashboard.py --server.port 8501
```

## 📊 使用流程

### 1. 先运行分析程序（获取数据）
```bash
# 完整分析
.venv\Scripts\python.exe main.py

# 仅分析特定股票
.venv\Scripts\python.exe main.py --stocks 601899,518880
```

### 2. 启动 Web 界面
```bash
# 在另一个终端
run_streamlit.bat
```

### 3. 访问界面
- 打开浏览器访问：`http://localhost:8501`
- 选择股票代码
- 查看图表和分析结果

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `streamlit_app.py` | 基础版界面（快速查看） |
| `streamlit_dashboard.py` | 专业版界面（完整功能） |
| `requirements-complete.txt` | 完整依赖列表 |
| `run_streamlit.bat` | Windows 启动脚本 |
| `run_streamlit.sh` | Linux/Mac 启动脚本 |
| `README_STREAMLIT.md` | 详细文档 |
| `QUICK_START.md` | 本快速指南 |

## 🔧 常见问题

### 问题：找不到 streamlit
**原因**：使用了错误的 Python 解释器

**解决**：
```bash
# 使用虚拟环境的 Python
.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

### 问题：没有数据
**原因**：未运行分析程序

**解决**：
```bash
# 先运行分析
.venv\Scripts\python.exe main.py --stocks 601899
```

### 问题：端口被占用
**解决**：
```bash
# 指定其他端口
.venv\Scripts\python.exe -m streamlit run streamlit_app.py --server.port 8502
```

## 🎨 界面预览

### 基础版功能
- 📈 K线图（MA5/10/20）
- 🤖 AI分析结果
- 📊 关键指标卡片
- 📰 情报中心

### 专业版功能
- 📈 K线 + MACD + 成交量
- 🎯 筹码分析
- 📊 趋势分析
- 🤖 AI智能评分
- 🏢 大盘监控
- 🗂️ 数据管理

## 💡 使用技巧

1. **快速查看**：使用基础版，启动快
2. **深度分析**：使用专业版，功能全
3. **数据刷新**：点击界面"刷新数据"按钮
4. **缓存清理**：遇到问题时重启应用

## 📞 技术支持

如有问题，请查看：
- `README_STREAMLIT.md` - 完整文档
- `logs/` 目录 - 错误日志
- 项目 GitHub 页面

---

**祝使用愉快！** 🚀