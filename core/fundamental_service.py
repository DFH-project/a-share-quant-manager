#!/usr/bin/env python3
"""
基本面数据服务 - Fundamental Data Service
使用AKShare获取真实基本面数据，带本地缓存
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
import time

CACHE_DIR = '/root/.openclaw/workspace/skills/a-share-quant-manager/data/fundamental_cache'
CACHE_FILE = os.path.join(CACHE_DIR, 'fundamental_data.json')

def ensure_cache_dir():
    """确保缓存目录存在"""
    os.makedirs(CACHE_DIR, exist_ok=True)

def is_cache_valid(timestamp: str) -> bool:
    """检查缓存是否有效（1天内）"""
    try:
        cache_time = datetime.fromisoformat(timestamp)
        return (datetime.now() - cache_time).days < 1
    except:
        return False

def get_fundamental_data(code: str) -> Optional[Dict]:
    """
    获取基本面数据 - 优先缓存，否则实时获取
    绝不生成假数据，获取失败返回None
    """
    ensure_cache_dir()
    
    # 1. 检查缓存
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cache = json.load(f)
            
            if code in cache and is_cache_valid(cache[code].get('timestamp', '')):
                print(f"  [基本面] {code} 使用缓存数据")
                return cache[code]['data']
    except Exception as e:
        print(f"  [基本面] 读取缓存失败: {e}")
    
    # 2. 实时获取
    try:
        import akshare as ak
        
        # 添加延迟避免请求过快
        time.sleep(0.5)
        
        df = ak.stock_individual_info_em(symbol=code)
        if df is None or df.empty:
            raise Exception("AKShare返回空数据")
        
        result = {}
        for _, row in df.iterrows():
            key = str(row.get('item', ''))
            value = row.get('value', '')
            
            if '市盈' in key or 'PE' in key:
                try:
                    result['pe'] = float(value)
                except:
                    pass
            elif '市净' in key or 'PB' in key:
                try:
                    result['pb'] = float(value)
                except:
                    pass
            elif 'ROE' in key or '净资产收益率' in key:
                try:
                    result['roe'] = float(value)
                except:
                    pass
            elif '总市值' in key:
                try:
                    result['market_cap'] = float(value)
                except:
                    pass
            elif '所属行业' in key:
                result['industry'] = str(value)
        
        if not result:
            raise Exception("基本面数据解析为空")
        
        # 保存缓存
        try:
            cache = {}
            if os.path.exists(CACHE_FILE):
                with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
            
            cache[code] = {
                'data': result,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"  [基本面] 保存缓存失败: {e}")
        
        print(f"  [基本面] {code} 获取成功: PE={result.get('pe')}, ROE={result.get('roe')}")
        return result
        
    except Exception as e:
        print(f"  [基本面] {code} 获取失败: {e}")
        return None

def batch_update_fundamental(codes: list) -> Dict[str, Dict]:
    """批量更新基本面数据"""
    results = {}
    for code in codes:
        data = get_fundamental_data(code)
        if data:
            results[code] = data
        else:
            results[code] = {'error': '获取失败'}
    return results

if __name__ == '__main__':
    # 测试
    print("测试获取中科曙光基本面数据...")
    data = get_fundamental_data('603019')
    print(json.dumps(data, ensure_ascii=False, indent=2))
