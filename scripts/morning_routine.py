#!/usr/bin/env python3
"""
A股早盘分析脚本 - Morning Routine
生成开盘前市场分析报告
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_fetcher import data_fetcher
from core.watchlist_memory import WatchlistMemory
from datetime import datetime

def main():
    """早盘分析主函数"""
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"\n{'='*60}")
    print(f"📊 A股早盘分析报告 - {today}")
    print(f"{'='*60}\n")
    
    try:
        # 获取大盘数据
        print("【大盘概况】")
        market_data = data_fetcher.get_index_data()
        for name, data in market_data.items():
            if data.get('current'):
                emoji = "🟢" if data.get('change_pct', 0) >= 0 else "🔴"
                print(f"  {emoji} {name}: {data['current']:.2f} ({data['change_pct']:+.2f}%)")
        
        # 获取自选股
        watchlist = WatchlistMemory()
        codes = watchlist.get_codes()
        
        if codes:
            print(f"\n【自选股关注】")
            stock_data = data_fetcher.get_stock_data(codes[:10])
            for code in codes[:10]:
                if code in stock_data:
                    data = stock_data[code]
                    emoji = "🟢" if data['change_pct'] >= 0 else "🔴"
                    print(f"  {emoji} {data['name']}({code}): {data['current']:.2f} ({data['change_pct']:+.2f}%)")
        
        print(f"\n{'='*60}")
        print(f"✅ 早盘分析完成 - 祝交易顺利！")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n❌ 分析失败: {e}")
        raise

if __name__ == '__main__':
    main()
