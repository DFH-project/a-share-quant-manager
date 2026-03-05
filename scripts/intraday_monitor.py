#!/usr/bin/env python3
"""
A股盘中监控脚本 - Intraday Monitor
使用多数据源获取真实数据
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_fetcher import data_fetcher
from core.watchlist_memory import WatchlistMemory
from core.monthly_strategy import MonthlyStrategy
from datetime import datetime

def main():
    """盘中监控主函数"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 执行A股盘中监控...")
    
    try:
        # 获取真实大盘数据
        print("获取大盘数据...")
        market_data = data_fetcher.get_index_data()
        sh = market_data.get('上证指数', {})
        print(f"上证指数: {sh.get('current', 0):.2f} ({sh.get('change_pct', 0):+.2f}%)")
        
        # 获取自选股数据
        watchlist = WatchlistMemory()
        codes = watchlist.get_codes()
        
        if codes:
            print(f"监控自选股: {len(codes)}只")
            stock_data = data_fetcher.get_stock_data(codes[:10])  # 最多10只
            
            for code, data in stock_data.items():
                print(f"  {data['name']}({code}): {data['current']:.2f} ({data['change_pct']:+.2f}%)")
        
        print("监控完成，数据真实有效")
        
    except Exception as e:
        print(f"❌ 监控失败: {e}")
        print("❌ 无法获取真实数据，不生成假数据")
        raise

if __name__ == '__main__':
    main()
