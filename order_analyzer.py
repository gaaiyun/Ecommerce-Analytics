"""
订单分析模块 - Order Analyzer
功能：订单趋势、地域分布、时段分析、客户分析
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple


class OrderAnalyzer:
    """订单分析器"""
    
    def __init__(self, orders_df: pd.DataFrame):
        self.orders_df = orders_df
        self.orders_df['order_date'] = pd.to_datetime(self.orders_df['order_date'])
        
    def get_order_trend(self, period: str = 'D') -> pd.DataFrame:
        """订单趋势分析"""
        # 确保日期格式正确
        orders_copy = self.orders_df.copy()
        orders_copy['order_date'] = pd.to_datetime(orders_copy['order_date'], errors='coerce')
        orders_copy = orders_copy.dropna(subset=['order_date'])
        
        if len(orders_copy) == 0:
            return pd.DataFrame()
        
        trend = orders_copy.groupby(
            pd.Grouper(key='order_date', freq=period)
        ).agg({
            'order_id': 'count',
            'quantity': 'sum',
            'revenue': 'sum',
            'profit': 'sum'
        }).reset_index()
        
        trend.rename(columns={'order_id': 'order_count'}, inplace=True)
        trend['avg_order_value'] = (
            trend['revenue'] / trend['order_count']
        ).round(2)
        
        return trend
    
    def get_regional_distribution(self) -> pd.DataFrame:
        """地域分布分析"""
        regional = self.orders_df.groupby('region').agg({
            'order_id': 'count',
            'quantity': 'sum',
            'revenue': 'sum',
            'profit': 'sum'
        }).reset_index()
        
        regional.rename(columns={'order_id': 'order_count'}, inplace=True)
        regional['order_percent'] = (
            regional['order_count'] / regional['order_count'].sum() * 100
        ).round(2)
        regional['revenue_percent'] = (
            regional['revenue'] / regional['revenue'].sum() * 100
        ).round(2)
        
        return regional.sort_values('revenue', ascending=False)
    
    def get_city_analysis(self, top_n: int = 10) -> pd.DataFrame:
        """城市分析"""
        city_analysis = self.orders_df.groupby('city').agg({
            'order_id': 'count',
            'quantity': 'sum',
            'revenue': 'sum'
        }).reset_index()
        
        city_analysis.rename(columns={'order_id': 'order_count'}, inplace=True)
        city_analysis['avg_order_value'] = (
            city_analysis['revenue'] / city_analysis['order_count']
        ).round(2)
        
        return city_analysis.sort_values('revenue', ascending=False).head(top_n)
    
    def get_hourly_analysis(self) -> pd.DataFrame:
        """时段分析（模拟数据）"""
        # 模拟时段分布
        hourly_data = {
            'hour': list(range(24)),
            'order_count': np.random.randint(5, 50, 24),
            'revenue': np.random.randint(500, 5000, 24)
        }
        
        hourly_df = pd.DataFrame(hourly_data)
        hourly_df['avg_order_value'] = (
            hourly_df['revenue'] / hourly_df['order_count']
        ).round(2)
        
        return hourly_df
    
    def get_payment_method_analysis(self) -> pd.DataFrame:
        """支付方式分析"""
        payment = self.orders_df.groupby('payment_method').agg({
            'order_id': 'count',
            'revenue': 'sum',
            'profit': 'sum'
        }).reset_index()
        
        payment.rename(columns={'order_id': 'order_count'}, inplace=True)
        payment['order_percent'] = (
            payment['order_count'] / payment['order_count'].sum() * 100
        ).round(2)
        
        return payment.sort_values('order_count', ascending=False)
    
    def get_customer_analysis(self, top_n: int = 10) -> pd.DataFrame:
        """客户分析"""
        customer = self.orders_df.groupby(['customer_id', 'customer_name']).agg({
            'order_id': 'count',
            'quantity': 'sum',
            'revenue': 'sum',
            'profit': 'sum',
            'order_date': ['min', 'max']
        }).reset_index()
        
        customer.columns = [
            'customer_id', 'customer_name', 'order_count', 
            'total_quantity', 'total_revenue', 'total_profit',
            'first_order', 'last_order'
        ]
        
        customer['avg_order_value'] = (
            customer['total_revenue'] / customer['order_count']
        ).round(2)
        customer['customer_lifetime_value'] = customer['total_revenue']
        
        return customer.sort_values('total_revenue', ascending=False).head(top_n)
    
    def get_order_status_summary(self) -> pd.DataFrame:
        """订单状态汇总"""
        status = self.orders_df.groupby('status').agg({
            'order_id': 'count',
            'revenue': 'sum'
        }).reset_index()
        
        status.rename(columns={'order_id': 'order_count'}, inplace=True)
        status['order_percent'] = (
            status['order_count'] / status['order_count'].sum() * 100
        ).round(2)
        
        return status
    
    def get_repeat_purchase_analysis(self) -> Dict:
        """复购分析"""
        customer_orders = self.orders_df.groupby('customer_id').size()
        
        total_customers = len(customer_orders)
        repeat_customers = len(customer_orders[customer_orders > 1])
        repeat_rate = (repeat_customers / total_customers * 100) if total_customers > 0 else 0
        
        return {
            'total_customers': total_customers,
            'repeat_customers': repeat_customers,
            'repeat_rate': round(repeat_rate, 2),
            'avg_orders_per_customer': round(customer_orders.mean(), 2)
        }
