"""
A-Share Quant Manager - 核心模块包
"""

from .data_fetcher import DataFetcher, data_fetcher
from .watchlist_memory import WatchlistMemory
from .monthly_strategy import MonthlyStrategy
from .smart_trader import SmartTrader

__all__ = ['DataFetcher', 'data_fetcher', 'WatchlistMemory', 'MonthlyStrategy', 'SmartTrader']
