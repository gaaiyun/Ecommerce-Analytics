"""
商品分析模块 - Product Analyzer
功能：销量分析、利润分析、库存分析、销售排名
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple


class ProductAnalyzer:
    """商品分析器"""
    
    def __init__(self, orders_df: pd.DataFrame, products_df: pd.DataFrame):
        self.orders_df = orders_df
        self.products_df = products_df
        
    def get_sales_ranking(self, top_n: int = 10) -> pd.DataFrame:
        """获取销售排名"""
        # 确保 product_id 类型一致
        sales = self.orders_df.groupby('product_id').agg({
            'quantity': 'sum',
            'revenue': 'sum',
            'profit': 'sum'
        }).reset_index()
        
        # 转换 product_id 为字符串类型
        sales['product_id'] = sales['product_id'].astype(str)
        products_copy = self.products_df.copy()
        products_copy['product_id'] = products_copy['product_id'].astype(str)
        
        sales = sales.merge(products_copy[['product_id', 'product_name', 'category']], 
                           on='product_id', how='left')
        
        sales = sales.sort_values('revenue', ascending=False)
        return sales.head(top_n)
    
    def get_profit_analysis(self) -> pd.DataFrame:
        """利润分析"""
        profit = self.orders_df.groupby('product_id').agg({
            'profit': 'sum',
            'revenue': 'sum',
            'quantity': 'sum'
        }).reset_index()
        
        profit['profit_margin'] = (profit['profit'] / profit['revenue'] * 100).round(2)
        
        # 转换类型
        profit['product_id'] = profit['product_id'].astype(str)
        products_copy = self.products_df.copy()
        products_copy['product_id'] = products_copy['product_id'].astype(str)
        
        profit = profit.merge(
            products_copy[['product_id', 'product_name', 'category']], 
            on='product_id', how='left'
        )
        
        return profit.sort_values('profit', ascending=False)
    
    def get_category_performance(self) -> pd.DataFrame:
        """品类表现分析"""
        category_perf = self.orders_df.groupby('category').agg({
            'quantity': 'sum',
            'revenue': 'sum',
            'profit': 'sum',
            'order_id': 'count'
        }).reset_index()
        
        category_perf.rename(columns={'order_id': 'order_count'}, inplace=True)
        category_perf['avg_order_value'] = (
            category_perf['revenue'] / category_perf['order_count']
        ).round(2)
        
        return category_perf.sort_values('revenue', ascending=False)
    
    def get_inventory_status(self) -> pd.DataFrame:
        """库存状态分析"""
        inventory = self.products_df.copy()
        inventory['stock_status'] = inventory.apply(
            lambda row: '低库存' if row['stock_quantity'] <= row['reorder_level'] 
            else ('充足' if row['stock_quantity'] > row['reorder_level'] * 2 else '正常'),
            axis=1
        )
        
        # 计算库存周转率（简化版）
        sales_qty = self.orders_df.groupby('product_id')['quantity'].sum().reset_index()
        sales_qty.rename(columns={'quantity': 'sold_qty'}, inplace=True)
        
        # 转换类型
        inventory['product_id'] = inventory['product_id'].astype(str)
        sales_qty['product_id'] = sales_qty['product_id'].astype(str)
        
        inventory = inventory.merge(sales_qty, on='product_id', how='left')
        inventory['sold_qty'] = inventory['sold_qty'].fillna(0)
        inventory['turnover_rate'] = (
            inventory['sold_qty'] / inventory['stock_quantity'] * 100
        ).round(2)
        
        return inventory
    
    def get_restock_recommendations(self) -> pd.DataFrame:
        """智能补货建议"""
        inventory = self.get_inventory_status()
        
        # 计算日均销量
        days_span = 25  # 示例数据 25 天
        inventory['daily_sales'] = (inventory['sold_qty'] / days_span).round(1)
        inventory['days_remaining'] = (
            inventory['stock_quantity'] / inventory['daily_sales']
        ).round(1)
        
        # 生成补货建议
        def get_recommendation(row):
            if row['stock_quantity'] <= row['reorder_level']:
                return f"立即补货！建议补货量：{int(row['daily_sales'] * 15)}"
            elif row['days_remaining'] < 10:
                return f"准备补货，预计{int(row['days_remaining'])}天后库存不足"
            else:
                return "库存充足"
        
        inventory['recommendation'] = inventory.apply(get_recommendation, axis=1)
        
        return inventory[inventory['stock_quantity'] <= inventory['reorder_level'] * 1.5]
    
    def get_price_optimization_suggestions(self) -> pd.DataFrame:
        """价格优化建议"""
        profit_analysis = self.get_profit_analysis()
        
        def suggest_price(row):
            margin = row['profit_margin']
            if pd.isna(margin):
                return "数据不足"
            elif margin < 30:
                return f"建议提价{int((35 - margin) / 10 * 5)}% 或优化成本"
            elif margin > 60:
                return "利润率优秀，可考虑促销扩大销量"
            else:
                return "价格策略合理"
        
        profit_analysis['price_suggestion'] = profit_analysis.apply(suggest_price, axis=1)
        
        return profit_analysis[['product_id', 'product_name', 'profit_margin', 'price_suggestion']]
    
    def get_competitor_analysis(self) -> Dict:
        """竞品监控分析（模拟）"""
        # 模拟竞品价格数据
        competitor_prices = {
            'P001': {'our_price': 89, 'competitor_avg': 95, 'market_share': 0.35},
            'P002': {'our_price': 299, 'competitor_avg': 310, 'market_share': 0.28},
            'P006': {'our_price': 199, 'competitor_avg': 189, 'market_share': 0.22},
        }
        
        analysis = []
        products_copy = self.products_df.copy()
        products_copy['product_id'] = products_copy['product_id'].astype(str)
        
        for pid, data in competitor_prices.items():
            product = products_copy[products_copy['product_id'] == pid]
            if not product.empty:
                price_diff = ((data['our_price'] - data['competitor_avg']) / 
                             data['competitor_avg'] * 100)
                analysis.append({
                    'product_id': pid,
                    'product_name': product.iloc[0]['product_name'],
                    'our_price': data['our_price'],
                    'competitor_avg_price': data['competitor_avg'],
                    'price_diff_percent': round(price_diff, 2),
                    'market_share': data['market_share'],
                    'strategy': '价格优势' if price_diff < 0 else '需优化定价'
                })
        
        return pd.DataFrame(analysis)
