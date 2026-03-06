#!/usr/bin/env python3
"""
A股自动选股管理器 - Auto Watchlist Manager
自动扫描市场，根据信号动态管理自选池
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.data_fetcher import data_fetcher
from core.watchlist_memory import WatchlistMemory, get_watchlist_memory
from typing import List, Dict, Tuple
from datetime import datetime

class AutoWatchlistManager:
    """自动选股管理器"""
    
    def __init__(self):
        self.watchlist = get_watchlist_memory()
        self.buy_signals = []  # 买入信号池
        self.sector_leaders = {}  # 板块龙头
        
    def scan_buy_signals(self, stock_pool: List[str] = None) -> List[Dict]:
        """扫描买入信号
        
        检测条件：
        1. 量价齐升（成交量>5日均量1.5倍 + 涨幅>3%）
        2. 突破形态（突破近期高点 + MACD金叉）
        3. 板块联动（所属板块涨幅前5 + 个股领涨）
        """
        signals = []
        
        if stock_pool is None:
            # 默认扫描持仓+自选+热门板块
            stock_pool = self._get_default_scan_pool()
        
        try:
            stock_data = data_fetcher.get_stock_data(stock_pool[:50])  # 最多50只
            
            for code, data in stock_data.items():
                signal_score = 0
                reasons = []
                
                # 条件1: 量价齐升
                if data.get('volume_ratio', 0) > 1.5 and data.get('change_pct', 0) > 3:
                    signal_score += 30
                    reasons.append("量价齐升")
                
                # 条件2: 强势上涨
                if data.get('change_pct', 0) > 5:
                    signal_score += 25
                    reasons.append("强势上涨")
                
                # 条件3: 突破新高（简化判断）
                if data.get('high_20d', 0) > 0 and data.get('current', 0) >= data.get('high_20d', 0) * 0.98:
                    signal_score += 20
                    reasons.append("接近20日新高")
                
                # 条件4: 资金流入
                if data.get('main_force_flow', 0) > 0:
                    signal_score += 15
                    reasons.append("主力流入")
                
                if signal_score >= 50:
                    signals.append({
                        'code': code,
                        'name': data.get('name', code),
                        'price': data.get('current', 0),
                        'change_pct': data.get('change_pct', 0),
                        'score': signal_score,
                        'reasons': reasons,
                        'sector': data.get('sector', ''),
                        'time': datetime.now().strftime('%H:%M')
                    })
            
            # 按信号强度排序
            signals.sort(key=lambda x: x['score'], reverse=True)
            self.buy_signals = signals[:10]  # 保留前10
            
        except Exception as e:
            print(f"扫描买入信号失败: {e}")
        
        return self.buy_signals
    
    def scan_sector_leaders(self) -> Dict[str, List[str]]:
        """扫描板块龙头"""
        # 获取板块数据并找出领涨板块
        leaders = {}
        try:
            # 这里简化处理，实际应该从data_fetcher获取板块数据
            # 返回板块名称和领涨股列表
            pass
        except Exception as e:
            print(f"扫描板块龙头失败: {e}")
        return leaders
    
    def auto_add_to_watchlist(self, signals: List[Dict] = None) -> int:
        """自动将信号股加入自选（标记为重点监控）"""
        if signals is None:
            signals = self.buy_signals
        
        added_count = 0
        for signal in signals:
            code = signal['code']
            
            # 如果已存在，更新为重点关注
            if self.watchlist.exists(code):
                self.watchlist.update(
                    code,
                    category="重点监控",
                    priority=10,
                    notes=f"✳️买入信号:{signal['score']}分 {' '.join(signal['reasons'])} {signal['time']}"
                )
            else:
                # 新加入自选
                self.watchlist.add(
                    code=code,
                    name=signal['name'],
                    category="重点监控",
                    priority=10,
                    tags=["自动发现", "买入信号"],
                    notes=f"✳️{signal['score']}分 {' '.join(signal['reasons'])} 价格:{signal['price']}"
                )
                added_count += 1
        
        return added_count
    
    def auto_remove_from_watchlist(self) -> int:
        """自动移除走坏的股票"""
        removed_count = 0
        watchlist_items = self.watchlist.get_all()
        
        codes = [item.code for item in watchlist_items]
        if not codes:
            return 0
        
        try:
            stock_data = data_fetcher.get_stock_data(codes)
            
            for item in watchlist_items:
                code = item.code
                if code not in stock_data:
                    continue
                
                data = stock_data[code]
                change_pct = data.get('change_pct', 0)
                
                # 移除条件：
                # 1. 重点监控股票大跌（-5%以上）
                # 2. 形态走坏（跌破关键支撑位）
                should_remove = False
                remove_reason = ""
                
                if item.category == "重点监控" and change_pct < -5:
                    should_remove = True
                    remove_reason = f"大跌{change_pct:.2f}% 取消重点监控"
                
                if should_remove:
                    # 不移除，而是降级为普通观察
                    self.watchlist.update(
                        code,
                        category="观察",
                        priority=0,
                        notes=f"❌已降级-{remove_reason} {datetime.now().strftime('%H:%M')}"
                    )
                    removed_count += 1
        
        except Exception as e:
            print(f"自动移除检查失败: {e}")
        
        return removed_count
    
    def get_priority_watchlist(self) -> List[Dict]:
        """获取优先级排序的自选股（用于监控）"""
        items = self.watchlist.get_all()
        
        # 按优先级排序
        items.sort(key=lambda x: x.priority, reverse=True)
        
        result = []
        codes = [item.code for item in items]
        
        if codes:
            try:
                stock_data = data_fetcher.get_stock_data(codes)
                
                for item in items:
                    code = item.code
                    if code in stock_data:
                        data = stock_data[code]
                        result.append({
                            'code': code,
                            'name': item.name,
                            'category': item.category,
                            'priority': item.priority,
                            'price': data.get('current', 0),
                            'change_pct': data.get('change_pct', 0),
                            'notes': item.notes
                        })
            except Exception as e:
                print(f"获取优先自选失败: {e}")
        
        return result
    
    def _get_default_scan_pool(self) -> List[str]:
        """获取默认扫描池"""
        # 已有持仓+自选
        pool = set(self.watchlist.get_codes())
        
        # 这里可以加入热门股票池、板块成分股等
        # 简化处理，返回已有池
        return list(pool)
    
    def run_daily_scan(self) -> Dict:
        """每日全量扫描"""
        print("\n🔍 启动每日自选池扫描...")
        
        # 1. 扫描买入信号
        signals = self.scan_buy_signals()
        print(f"  发现 {len(signals)} 个买入信号")
        
        # 2. 自动加入自选
        added = self.auto_add_to_watchlist(signals)
        print(f"  新增 {added} 只到重点监控")
        
        # 3. 清理走坏的股票
        removed = self.auto_remove_from_watchlist()
        print(f"  降级 {removed} 只重点监控")
        
        return {
            'signals_found': len(signals),
            'added_to_watchlist': added,
            'removed_from_priority': removed,
            'top_signals': signals[:5]
        }


# 单例
_auto_manager = None

def get_auto_manager() -> AutoWatchlistManager:
    """获取自动管理器单例"""
    global _auto_manager
    if _auto_manager is None:
        _auto_manager = AutoWatchlistManager()
    return _auto_manager


if __name__ == '__main__':
    manager = AutoWatchlistManager()
    result = manager.run_daily_scan()
    print("\n扫描结果:", result)
