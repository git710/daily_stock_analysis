"""
===================================
数据源策略层 - 包初始化
===================================

本包实现策略模式管理多个数据源，实现：
1. 统一的数据获取接口
2. 自动故障切换
3. 防封禁流控策略
"""

from .akshare_fetcher import AkshareFetcher
from .baostock_fetcher import BaostockFetcher
from .base import BaseFetcher, DataFetcherManager
from .tushare_fetcher import TushareFetcher
from .yfinance_fetcher import YfinanceFetcher

__all__ = [
    "BaseFetcher",
    "DataFetcherManager",
    "AkshareFetcher",
    "TushareFetcher",
    "BaostockFetcher",
    "YfinanceFetcher",
]
