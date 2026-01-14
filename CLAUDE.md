# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 📋 项目概述

**A股自选股智能分析系统** - 基于 AI 大模型的每日股票分析工具，自动生成决策仪表盘并推送通知。

核心功能：
- 🤖 AI 决策仪表盘（买卖点位 + 检查清单）
- 📊 大盘复盘分析
- 📰 实时新闻搜索
- 📱 多渠道推送（企业微信/飞书/Telegram/邮件/自定义Webhook）
- 🚀 GitHub Actions 零成本部署

## 🛠️ 开发命令

### 本地运行
```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API Key

# 运行模式
python main.py                    # 完整分析（股票+大盘）
python main.py --debug            # 调试模式（详细日志）
python main.py --dry-run          # 仅获取数据不分析
python main.py --market-review    # 仅大盘复盘
python main.py --stocks-only      # 仅股票分析
python main.py --schedule         # 定时任务模式
```

### 代码质量
```bash
# Ruff 代码检查 + 自动修复
ruff check .
ruff format .
ruff check . --fix

# 运行测试（如果有）
python -m pytest
```

### Docker 部署
```bash
# 一键启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 手动执行
docker-compose exec stock-analyzer python main.py
```

## 🏗️ 架构概览

### 核心模块关系
```
main.py (主调度器)
├── config.py (配置管理 - 单例模式)
├── data_provider/ (数据源策略层)
│   ├── BaseFetcher (抽象基类)
│   ├── AkshareFetcher (主数据源)
│   ├── TushareFetcher (备用)
│   ├── BaostockFetcher (备用)
│   └── YfinanceFetcher (备用)
├── stock_analyzer.py (趋势分析 - MA多头排列 + 乖离率)
├── search_service.py (新闻搜索 - Tavily/SerpAPI)
├── analyzer.py (AI分析 - Gemini API调用)
├── market_analyzer.py (大盘复盘)
├── storage.py (SQLite ORM)
└── notification.py (多渠道推送)
```

### 设计模式
- **策略模式**：`data_provider` 包实现多数据源自动切换
- **单例模式**：`Config` 配置管理、`storage` 数据库连接
- **模板方法**：`BaseFetcher` 定义数据获取流程

### 数据流
```
1. main.py 接收任务
2. data_provider 获取股票数据 → storage 缓存
3. stock_analyzer 计算技术指标（MA5/10/20, 乖离率）
4. search_service 获取相关新闻
5. analyzer.py 调用 AI 生成分析
6. notification.py 推送结果
```

## 📁 关键文件说明

| 文件 | 职责 |
|------|------|
| `main.py` | 主入口，线程池调度，异常处理 |
| `config.py` | 环境变量管理，类型安全配置 |
| `analyzer.py` | AI 分析器，封装 Gemini API |
| `stock_analyzer.py` | 趋势分析，MA 多头排列 + 乖离率计算 |
| `market_analyzer.py` | 大盘复盘，指数 + 板块分析 |
| `search_service.py` | 新闻搜索，多引擎支持 |
| `notification.py` | 多渠道推送，Markdown 生成 |
| `storage.py` | SQLite ORM，数据缓存 |
| `scheduler.py` | 定时任务调度 |
| `data_provider/` | 数据源适配器集合 |

## 🔧 配置管理

### 必需环境变量
```bash
# 股票列表
STOCK_LIST=600519,300750,002594

# AI 模型（二选一）
GEMINI_API_KEY=your_key
# 或
OPENAI_API_KEY=your_key
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat

# 通知渠道（至少一个）
WECHAT_WEBHOOK_URL=your_url
# 或 FEISHU_WEBHOOK_URL
# 或 TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID
# 或 EMAIL_SENDER + EMAIL_PASSWORD
# 或 CUSTOM_WEBHOOK_URLS
```

### 交易理念内置
- ❌ **严禁追高**：乖离率 > 5% 自动标记「危险」
- ✅ **趋势交易**：MA5 > MA10 > MA20 多头排列
- 📍 **精确点位**：买入价、止损价、目标价
- 📋 **检查清单**：每项条件用 ✅⚠️❌ 标记

## 🔄 工作流程

### 完整分析流程
```
1. 获取自选股列表
2. 并行获取数据（低并发，max_workers=3）
   ├─ Akshare (主) → 失败自动切换
   ├─ Tushare (备)
   ├─ Baostock (备)
   └─ Yfinance (备)
3. 计算技术指标
   ├─ MA5/10/20/60
   ├─ 乖离率 (Close - MA5) / MA5
   └─ 量能分析
4. 搜索新闻（Tavily/SerpAPI）
5. AI 分析（Gemini/OpenAI）
   ├─ 技术面 + 筹码 + 舆情
   └─ 生成决策仪表盘
6. 大盘复盘（可选）
7. 推送通知（多渠道）
```

### GitHub Actions 流程
```yaml
# .github/workflows/daily_analysis.yml
schedule: UTC 1:00 (北京时间 9:00) 周一到周五
workflow_dispatch: 手动触发
env: 从 Secrets 读取配置
steps:
  1. 检出代码
  2. 设置 Python 3.11
  3. 安装依赖
  4. 执行 main.py
```

## ⚠️ 重要注意事项

### 防封禁策略
- 请求间隔：`GEMINI_REQUEST_DELAY` (默认 3秒)
- 重试机制：指数退避，最大 5 次
- 低并发：`MAX_WORKERS=3` 防止 API 限流
- 多 Key 轮询：Tavily/SerpAPI 支持多个 Key

### 数据源优先级
1. **Akshare** (主) - 免费，东方财富数据
2. **Tushare** (备) - 需要 Token
3. **Baostock** (备) - 证券宝数据
4. **Yfinance** (备) - 国际市场数据

### AI 模型降级
- 主模型：`GEMINI_MODEL` (默认 gemini-3-flash-preview)
- 备选：`GEMINI_MODEL_FALLBACK` (默认 gemini-2.5-flash)
- 备用方案：OpenAI 兼容 API

### 通知渠道
支持同时配置多个，会推送到所有渠道：
- 企业微信 Webhook
- 飞书 Webhook
- Telegram Bot
- 邮件 SMTP（自动识别服务商）
- 自定义 Webhook（钉钉/Discord/Slack/Bark等）

## 🐛 常见问题

### 1. 数据获取失败
- 检查网络代理配置（main.py 第 27-31 行）
- 查看日志确认具体失败的数据源
- 系统会自动切换到备用数据源

### 2. AI 分析失败
- 确认 API Key 配置正确
- 检查配额是否用完
- 查看是否触发 429 限流（日志中有重试信息）

### 3. 推送失败
- 检查 Webhook URL 是否正确
- 确认网络可以访问目标服务
- 邮件推送需确认 SMTP 授权码

### 4. GitHub Actions 运行失败
- 检查 Secrets 配置是否完整
- 确认 Actions 已启用
- 查看 Actions 日志详情

## 📊 数据库结构

### 表：stock_daily
```sql
id | code | date | open | high | low | close | volume | amount | pct_chg
ma5 | ma10 | ma20 | ma60 | rsi | macd | boll_upper | boll_lower
```

### 缓存策略
- 本地 SQLite 缓存历史数据
- 断点续传：失败时可从上次位置继续
- 数据去重：code + date 唯一约束

## 🔗 相关资源

- **GitHub**: https://github.com/ZhuLinsen/daily_stock_analysis
- **Gemini API**: https://aistudio.google.com/ (免费额度)
- **Tavily**: https://tavily.com/ (每月 1000 次免费)
- **SerpAPI**: https://serpapi.com/ (每月 100 次免费)

## 🚀 Roadmap (功能规划)

### 已完成 ✅
- [x] AI 决策仪表盘
- [x] 大盘复盘
- [x] 多数据源支持
- [x] 新闻搜索
- [x] 多渠道推送
- [x] GitHub Actions 部署
- [x] Docker 支持
- [x] OpenAI 兼容 API
- [x] 自定义 Webhook

### 计划中 📋
- [ ] Web 管理界面
- [ ] 自选股动态管理 API
- [ ] 历史分析回测
- [ ] 多策略支持
- [ ] 港股/美股支持
- [ ] iOS/Android 推送（Pushover）
- [ ] Claude 模型支持
- [ ] 文心一言支持