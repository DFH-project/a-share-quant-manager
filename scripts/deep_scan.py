#!/usr/bin/env python3
"""
深度扫描脚本 - Deep Scan Script
板块轮动 + 五策略选股
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.sector_tracker import get_sector_tracker
from core.auto_watchlist_manager import get_auto_manager

def main():
    print("="*60)
    print("🔥 板块轮动扫描")
    print("="*60)
    
    # 板块扫描
    sector = get_sector_tracker()
    sector.run_sector_scan()
    print(sector.get_sector_summary())
    
    print("\n" + "="*60)
    print("✨ 五策略选股扫描")
    print("="*60)
    
    # 五策略扫描
    manager = get_auto_manager()
    result = manager.run_full_scan()
    
    print("\n" + "="*60)
    print("📊 扫描结果汇总")
    print("="*60)
    print(f"💧 低吸型: {result['dip']['found']} 个")
    print(f"🚀 追涨型: {result['chase']['found']} 个")
    print(f"💎 潜力型: {result['potential']['found']} 个")
    print(f"🎯 抄底型: {result['bottom']['found']} 个")
    print(f"⭐ 多维度: {result['multi']['found']} 个")
    
    # 显示重点监控股票
    if result['multi']['signals']:
        print("\n⭐ 多维度优选标的：")
        for s in result['multi']['signals']:
            print(f"  {s['name']}({s['code']}) 综合{s['score']:.0f}分 - {s['suggestion']}")

if __name__ == '__main__':
    main()
