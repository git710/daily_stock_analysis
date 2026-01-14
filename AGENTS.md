# AGENTS.md - A股自选股智能分析系统开发指南

本文档为操作此代码库的智能代理提供全面指导，包括构建、测试、代码风格规范等关键信息。

## 📋 项目概述

**A股自选股智能分析系统** - 基于 AI 大模型的每日股票分析工具，自动生成决策仪表盘并推送通知。

- 🤖 AI 决策仪表盘（买卖点位 + 检查清单）
- 📊 大盘复盘分析
- 📰 实时新闻搜索
- 📱 多渠道推送（企业微信/飞书/Telegram/邮件/自定义Webhook）
- 🚀 GitHub Actions 零成本部署

## 🛠️ 构建、测试和代码质量命令

### 依赖安装
```bash
# 安装项目依赖
pip install -r requirements.txt

# 安装开发依赖（包含 Ruff 等工具）
pip install -r requirements.txt
uv sync  # 如果使用 uv 包管理器
```

### 代码质量检查
```bash
# 代码格式化和导入排序
ruff format .

# 代码检查（包括导入排序、类型检查等）
ruff check .

# 自动修复可修复的问题
ruff check . --fix

# 查看具体修复内容
ruff check . --show-fixes
```

### 测试运行
```bash
# 环境验证测试（推荐的主要测试）
python test_env.py              # 运行所有基础测试
python test_env.py --config     # 仅配置验证
python test_env.py --db         # 仅数据库检查
python test_env.py --llm        # 仅 LLM 调用测试
python test_env.py --fetch      # 仅数据获取测试
python test_env.py --notify     # 仅通知推送测试
python test_env.py --all        # 运行所有测试（包括 LLM）

# 运行单个股票查询测试
python test_env.py --stock 600519

# 传统单元测试（如果存在）
python -m pytest
python -m pytest tests/ -v
python -m pytest tests/test_specific.py::TestClass::test_method -v
```

### 运行和部署
```bash
# 本地运行
python main.py                    # 完整分析（股票+大盘）
python main.py --debug            # 调试模式（详细日志）
python main.py --dry-run          # 仅获取数据不分析
python main.py --market-review    # 仅大盘复盘
python main.py --stocks-only      # 仅股票分析
python main.py --schedule         # 定时任务模式

# Docker 部署
docker-compose up -d
docker-compose logs -f
docker-compose exec stock-analyzer python main.py
```

### 代码检查工具配置

项目使用 Ruff 作为主要代码质量工具，配置在 `pyproject.toml` 中：

```toml
[tool.ruff]
target-version = "py39"
line-length = 88
exclude = ["__pycache__", ".venv", "logs", "data", "sources"]

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP"]
ignore = ["E501", "B008", "UP007"]
fix = true
show-fixes = true

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
line-ending = "lf"
docstring-code-format = true
```

## 🎨 代码风格指南

### 1. 基本代码风格

#### 文件结构和命名
- **文件名**: 全小写，使用下划线分隔 (`stock_analyzer.py`, `data_provider/`)
- **类名**: PascalCase (`GeminiAnalyzer`, `DataFetcherManager`)
- **函数名**: snake_case (`get_config()`, `analyze_stock()`)
- **变量名**: snake_case (`stock_list`, `api_key`)
- **常量**: 全大写下划线分隔 (`LOG_FORMAT`, `DEFAULT_TIMEOUT`)

#### 导入组织
```python
# 标准库导入
import os
import sys
from pathlib import Path
from typing import Any, Optional

# 第三方库导入
import requests
from dotenv import load_dotenv

# 本地模块导入
from config import get_config
from analyzer import AnalysisResult
```

**导入分组顺序**（由 Ruff 自动排序）：
1. 标准库
2. 第三方库
3. 本地模块（按模块重要性排序）

### 2. 类型注解和文档

#### 函数签名
```python
def analyze_stock(
    stock_code: str,
    days: int = 30,
    use_cache: bool = True
) -> AnalysisResult:
    """
    分析指定股票的趋势和基本面

    Args:
        stock_code: 股票代码，如 '600519'
        days: 分析天数，默认30天
        use_cache: 是否使用缓存数据，默认True

    Returns:
        完整的分析结果对象

    Raises:
        ValueError: 当股票代码无效时
        ConnectionError: 当网络连接失败时
    """
```

#### 类定义
```python
@dataclass
class StockAnalysisResult:
    """股票分析结果数据类"""

    # 必需字段（无默认值，必须在前）
    code: str
    name: str
    analysis_date: date

    # 可选字段（有默认值，必须在后）
    confidence_score: int = 50
    risk_level: str = "medium"
    recommendation: Optional[str] = None
```

### 3. 错误处理和日志

#### 异常处理模式
```python
try:
    result = api_call_with_retry()
    logger.info(f"API 调用成功: {result}")
    return result
except ConnectionError as e:
    logger.error(f"网络连接失败: {e}")
    raise
except ValueError as e:
    logger.warning(f"参数验证失败: {e}")
    return None
except Exception as e:
    logger.error(f"未预期的错误: {e}", exc_info=True)
    raise
```

#### 日志级别使用
- `DEBUG`: 详细的调试信息，仅开发环境
- `INFO`: 重要操作的成功完成
- `WARNING`: 可恢复的错误或警告
- `ERROR`: 需要关注的功能性错误
- `CRITICAL`: 系统级严重错误

### 4. 代码组织原则

#### 单职责原则
每个模块、类、函数都有明确的单一职责：

```python
# analyzer.py - 专门处理 AI 分析
class GeminiAnalyzer:
    """AI 分析器，封装 Gemini API 调用"""

# stock_analyzer.py - 专门处理技术分析
class StockTrendAnalyzer:
    """技术指标分析器，计算 MA、乖离率等"""

# notification.py - 专门处理消息推送
class NotificationService:
    """多渠道通知服务"""
```

#### 配置管理
```python
# 使用单例模式的配置管理
@dataclass
class Config:
    """系统配置类"""

    # 使用类方法实现单例
    _instance: Optional['Config'] = None

    @classmethod
    def get_instance(cls) -> 'Config':
        if cls._instance is None:
            cls._instance = cls._load_from_env()
        return cls._instance

# 全局访问函数
def get_config() -> Config:
    return Config.get_instance()
```

### 5. 异步和并发

#### 线程池使用
```python
from concurrent.futures import ThreadPoolExecutor, as_completed

# 低并发设计，防止 API 限流
with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
    futures = [
        executor.submit(process_stock, code)
        for code in stock_list
    ]

    for future in as_completed(futures):
        try:
            result = future.result(timeout=30)
            logger.info(f"股票 {result.code} 处理完成")
        except Exception as e:
            logger.error(f"股票处理失败: {e}")
```

### 6. 数据验证和安全

#### 输入验证
```python
def validate_stock_code(code: str) -> bool:
    """验证股票代码格式"""
    if not isinstance(code, str):
        return False

    # A股代码规则：6位数字，沪市以6开头，深市以0/3开头
    if not re.match(r'^\d{6}$', code):
        return False

    return code.startswith(('0', '3', '6'))
```

#### 敏感信息处理
```python
# API Key 等敏感信息从环境变量读取
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY 环境变量未设置")

# 日志中隐藏敏感信息
logger.info(f"API Key: {api_key[:8]}...")  # 只显示前8位
```

### 7. 测试编写指南

#### 环境测试模式
项目主要使用环境验证测试而非传统单元测试：

```python
# test_env.py 中的测试模式
def test_config():
    """测试配置加载"""
    config = get_config()
    assert config.stock_list, "股票列表不能为空"
    assert config.gemini_api_key, "Gemini API Key 必须配置"

def test_llm():
    """测试 LLM 调用"""
    analyzer = GeminiAnalyzer()
    result = analyzer.analyze(test_context)
    assert result.success, f"分析失败: {result.error_message}"
```

#### 测试数据准备
```python
# 使用固定的测试数据确保可重现
test_context = {
    "code": "600519",
    "today": {
        "close": 1428.0,
        "ma5": 1425.0,
        "pct_chg": 0.56,
        # ... 其他测试数据
    }
}
```

## 🏗️ 架构模式和设计原则

### 策略模式 - 数据源适配器
```python
# data_provider/ 包实现多数据源切换
class DataFetcherManager:
    """数据获取管理器，自动切换数据源"""

    def __init__(self):
        self.fetchers = [
            AkshareFetcher(),  # 主数据源
            TushareFetcher(),  # 备选
            BaostockFetcher(), # 备选
        ]

    def get_daily_data(self, code: str) -> tuple[pd.DataFrame, str]:
        """自动切换数据源获取数据"""
        for fetcher in self.fetchers:
            try:
                return fetcher.get_daily_data(code), fetcher.name
            except Exception as e:
                logger.warning(f"{fetcher.name} 获取失败: {e}")
                continue
        raise RuntimeError("所有数据源都获取失败")
```

### 模板方法模式 - 基础数据获取器
```python
class BaseFetcher(ABC):
    """数据获取器抽象基类"""

    @abstractmethod
    def get_daily_data(self, code: str, days: int = 30) -> pd.DataFrame:
        """获取日线数据"""
        pass

    def _validate_code(self, code: str) -> None:
        """模板方法：验证股票代码"""
        if not self._is_valid_code(code):
            raise ValueError(f"无效的股票代码: {code}")

    @abstractmethod
    def _is_valid_code(self, code: str) -> bool:
        """子类实现具体验证逻辑"""
        pass
```

### 单例模式 - 配置管理
```python
@dataclass
class Config:
    """配置单例类"""
    _instance: Optional['Config'] = None

    @classmethod
    def get_instance(cls) -> 'Config':
        if cls._instance is None:
            cls._instance = cls._load_from_env()
        return cls._instance
```

## 🔧 开发环境配置

### 环境变量
```bash
# 必需
STOCK_LIST=600519,300750,002594
GEMINI_API_KEY=your_key

# 推荐
TAVILY_API_KEYS=key1,key2
WECHAT_WEBHOOK_URL=https://qyapi...

# 可选
TUSHARE_TOKEN=your_token
OPENAI_API_KEY=your_key
```

### IDE 配置
- **Python 版本**: 3.9+
- **推荐 IDE**: VS Code + Python 扩展
- **推荐插件**: Ruff, Pylance, Python Docstring Generator

## 🚀 GitHub Actions 工作流

### 定时分析工作流
```yaml
# .github/workflows/daily_analysis.yml
schedule:
  - cron: '0 10 * * 1-5'  # 北京时间 18:00
workflow_dispatch:  # 手动触发支持多种模式
```

### 支持的运行模式
- `full`: 完整分析（股票+大盘）
- `market-only`: 仅大盘复盘
- `stocks-only`: 仅股票分析

## 📊 数据库设计

### 股票日线表结构
```sql
CREATE TABLE stock_daily (
    id INTEGER PRIMARY KEY,
    code TEXT NOT NULL,
    date DATE NOT NULL,
    open REAL, high REAL, low REAL, close REAL,
    volume INTEGER, amount REAL, pct_chg REAL,
    ma5 REAL, ma10 REAL, ma20 REAL, ma60 REAL,
    rsi REAL, macd REAL, boll_upper REAL, boll_lower REAL,
    UNIQUE(code, date)
);
```

### 数据缓存策略
- SQLite 本地缓存
- 断点续传支持
- 数据去重约束
- 自动清理过期数据

## ⚠️ 重要注意事项

### API 限流防护
- **请求间隔**: Gemini API 至少 3 秒间隔
- **最大并发**: 线程池最大 3 个工作线程
- **重试机制**: 指数退避，最大 5 次重试
- **备用方案**: 多数据源自动切换

### 交易理念内置
- ❌ **严禁追高**: 乖离率 > 5% 自动标记危险
- ✅ **趋势交易**: MA5 > MA10 > MA20 多头排列
- 📍 **精确点位**: 买入价、止损价、目标价
- 📋 **检查清单**: 每项条件用 ✅⚠️❌ 标记

### 错误处理原则
- 网络错误自动重试
- 单股失败不影响整体分析
- 详细的错误日志记录
- 用户友好的错误提示

---

*本文档基于项目代码分析自动生成，最后更新: 2026-01-14*</content>
<parameter name="filePath">AGENTS.md