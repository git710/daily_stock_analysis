# 📊 A股智能分析系统 - Web 界面指南

基于 Streamlit 的可视化展示平台，为你的股票分析系统提供友好的 Web 界面。

## 🎯 功能特性

### 核心功能
- ✅ **实时仪表盘**：股票关键指标一目了然
- ✅ **K线图表**：交互式图表，支持MA均线、MACD、成交量
- ✅ **筹码分析**：可视化筹码分布和成本分析
- ✅ **AI分析展示**：智能分析结果直观呈现
- ✅ **大盘监控**：市场概览和热点追踪
- ✅ **数据管理**：数据库状态和日志导出

### 界面亮点
- 🎨 **现代化UI**：深色主题，专业金融风格
- 📱 **响应式设计**：支持桌面和移动端
- ⚡ **智能缓存**：5分钟数据缓存，快速响应
- 🔄 **实时刷新**：一键刷新数据
- 📊 **交互图表**：支持缩放、悬停查看详细信息

## 🚀 快速开始

### 1. 安装依赖

```bash
# 方式一：安装完整依赖（推荐）
pip install -r requirements-streamlit.txt

# 方式二：仅安装 Streamlit 相关依赖
pip install streamlit plotly pandas
```

### 2. 运行界面

```bash
# 运行基础版（推荐新手）
python -m streamlit run streamlit_app.py

# 运行专业版（功能更丰富）
python -m streamlit run streamlit_dashboard.py
```

### 3. 访问界面

程序启动后会显示类似以下信息：
```
You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.100:8501
```

在浏览器中打开 `http://localhost:8501` 即可访问。

## 📱 界面说明

### 基础版 (`streamlit_app.py`)

适合快速查看分析结果：

```
📊 仪表盘概览
├── 关键指标卡片（价格、量比、换手率、均线状态）
├── K线图表（MA5/10/20均线）
├── AI分析结果（操作建议、评分）
├── 情报中心（新闻、风险、业绩）
└── 历史数据表格
```

### 专业版 (`streamlit_dashboard.py`)

功能更全面的高级界面：

```
💹 完整视图
├── 实时指标（5个维度）
├── K线 + MACD + 成交量（三合一图表）
├── 趋势分析（均线排列、乖离率、量能）
├── 筹码分析（获利比例、集中度）
├── AI智能分析（从日志解析）
├── 大盘监控（涨跌统计、复盘内容）
└── 数据管理（数据库状态、日志下载）
```

## 🔧 使用流程

### 第一步：运行分析程序

```bash
# 完整分析
python main.py

# 仅分析特定股票
python main.py --stocks 600519,000001

# 调试模式（查看详细日志）
python main.py --debug
```

### 第二步：启动 Web 界面

```bash
# 在另一个终端启动
python -m streamlit run streamlit_dashboard.py
```

### 第三步：查看结果

1. **选择股票**：侧边栏选择要查看的股票代码
2. **切换视图**：选择"完整视图"、"仅图表"等模式
3. **刷新数据**：点击"刷新数据"按钮更新缓存

## 📊 数据流说明

```
┌─────────────────┐
│  main.py 运行    │  ← 生成分析结果和日志
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  SQLite 数据库   │  ← 存储历史K线数据
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  日志文件        │  ← 存储AI分析结果
│  (logs/*.log)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Streamlit 界面  │  ← 读取并展示
└─────────────────┘
```

## 🎨 界面定制

### 修改股票列表

在 `streamlit_app.py` 或 `streamlit_dashboard.py` 中：

```python
# 修改默认股票列表
default_stocks = ["600519", "000001", "300750"]
```

### 自定义样式

在代码开头的 CSS 部分修改：

```css
.main-header {
    font-size: 2.5rem;
    color: #667eea;  /* 修改颜色 */
}
```

### 调整缓存时间

```python
@st.cache_data(ttl=300)  # 300秒 = 5分钟
def get_stock_data(code: str, days: int = 60):
    ...
```

## 🐛 常见问题

### 1. 界面显示"暂无数据"

**原因**：未运行分析程序或数据库为空

**解决**：
```bash
# 先运行分析
python main.py --stocks 601899

# 再刷新界面
```

### 2. 图表不显示

**原因**：缺少 plotly 依赖

**解决**：
```bash
pip install plotly
```

### 3. 界面加载慢

**原因**：数据量大或网络慢

**解决**：
- 减少查看天数（默认60天，可改为30天）
- 等待缓存生效（第二次访问会很快）

### 4. 实时行情获取失败

**原因**：akshare 接口限制或网络问题

**解决**：
- 检查网络代理配置
- 等待几分钟后重试
- 查看终端错误信息

## 📦 部署方案

### 本地部署（推荐）

```bash
# 启动服务
python -m streamlit run streamlit_dashboard.py --server.port 8501 --server.address 0.0.0.0
```

### 内网访问

```bash
# 允许局域网访问
python -m streamlit run streamlit_dashboard.py --server.address 0.0.0.0
```

### 云服务器部署

```bash
# 使用 nohup 后台运行
nohup python -m streamlit run streamlit_dashboard.py --server.port 8501 &
```

### Docker 部署（可选）

创建 `Dockerfile.streamlit`：

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements-streamlit.txt .
RUN pip install --no-cache-dir -r requirements-streamlit.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

运行：
```bash
docker build -f Dockerfile.streamlit -t stock-dashboard .
docker run -p 8501:8501 -v $(pwd)/data:/app/data -v $(pwd)/logs:/app/logs stock-dashboard
```

## 🔗 相关文件

| 文件 | 说明 |
|------|------|
| `streamlit_app.py` | 基础版界面（适合新手） |
| `streamlit_dashboard.py` | 专业版界面（功能完整） |
| `requirements-streamlit.txt` | 界面依赖包 |
| `README_STREAMLIT.md` | 本说明文档 |

## 💡 使用技巧

### 1. 快速查看
```bash
# 一键启动（分析 + 界面）
python main.py && python -m streamlit run streamlit_dashboard.py
```

### 2. 开发调试
```bash
# 自动重载（开发时）
streamlit run streamlit_dashboard.py --server.port 8501
```

### 3. 数据对比
- 在界面中切换不同股票
- 观察均线排列和筹码分布
- 对比AI评分和操作建议

### 4. 历史回溯
- 修改日期范围滑块
- 查看不同时间点的形态
- 验证分析准确性

## 📊 界面截图预览

### 仪表盘概览
```
┌─────────────────────────────────────────┐
│  💹 A股智能分析仪表盘 Pro                │
├─────────────────────────────────────────┤
│  紫金矿业 (601899)                       │
├─────────────────────────────────────────┤
│  [价格] [量比] [换手率] [PE] [PB]       │
├─────────────────────────────────────────┤
│  📈 K线图 (MA5/10/20)                   │
├─────────────────────────────────────────┤
│  🤖 AI建议: 观望 | 评分: 68             │
├─────────────────────────────────────────┤
│  🎯 筹码: 获利97.5% | 集中度35.6%       │
└─────────────────────────────────────────┘
```

## 🎯 最佳实践

1. **定时运行**：每天收盘后运行分析程序
2. **定期查看**：启动界面查看分析结果
3. **数据备份**：定期备份 `data/` 和 `logs/` 目录
4. **缓存清理**：遇到问题时清除缓存 `st.cache_data.clear()`

---

**祝你使用愉快！** 🚀

如有问题，请查看日志或在 GitHub 提交 Issue。