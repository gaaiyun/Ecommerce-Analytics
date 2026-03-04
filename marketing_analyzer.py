"""
营销分析模块 - Marketing Analyzer
功能：ROI 分析、转化率、活动效果、转化漏斗
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple


class MarketingAnalyzer:
    """营销分析器"""
    
    def __init__(self, campaigns_df: pd.DataFrame, orders_df: pd.DataFrame):
        self.campaigns_df = campaigns_df
        self.orders_df = orders_df
        
    def get_campaign_roi(self) -> pd.DataFrame:
        """活动 ROI 分析"""
        roi = self.campaigns_df.copy()
        roi['roi'] = ((roi['revenue'] - roi['budget']) / roi['budget'] * 100).round(2)
        roi['profit'] = (roi['revenue'] - roi['budget']).round(2)
        roi['cost_per_order'] = (roi['budget'] / roi['orders']).round(2)
        roi['revenue_per_order'] = (roi['revenue'] / roi['orders']).round(2)
        
        return roi.sort_values('roi', ascending=False)
    
    def get_conversion_metrics(self) -> pd.DataFrame:
        """转化率分析"""
        conversion = self.campaigns_df.copy()
        
        # 点击率 CTR
        conversion['ctr'] = (conversion['clicks'] / conversion['impressions'] * 100).round(2)
        
        # 转化率 CVR (点击到订单)
        conversion['cvr'] = (conversion['orders'] / conversion['clicks'] * 100).round(2)
        
        # 总转化率 (展示到订单)
        conversion['overall_conversion'] = (
            conversion['orders'] / conversion['impressions'] * 100
        ).round(2)
        
        # 单次点击成本 CPC
        conversion['cpc'] = (conversion['budget'] / conversion['clicks']).round(2)
        
        # 单次获客成本 CPA
        conversion['cpa'] = (conversion['budget'] / conversion['orders']).round(2)
        
        return conversion.sort_values('cvr', ascending=False)
    
    def get_channel_performance(self) -> pd.DataFrame:
        """渠道表现分析"""
        channel = self.campaigns_df.groupby('channel').agg({
            'budget': 'sum',
            'orders': 'sum',
            'revenue': 'sum',
            'impressions': 'sum',
            'clicks': 'sum'
        }).reset_index()
        
        channel['roi'] = ((channel['revenue'] - channel['budget']) / 
                         channel['budget'] * 100).round(2)
        channel['ctr'] = (channel['clicks'] / channel['impressions'] * 100).round(2)
        channel['cvr'] = (channel['orders'] / channel['clicks'] * 100).round(2)
        channel['cpc'] = (channel['budget'] / channel['clicks']).round(2)
        channel['cpa'] = (channel['budget'] / channel['orders']).round(2)
        
        return channel.sort_values('revenue', ascending=False)
    
    def get_conversion_funnel(self, campaign_id: str = None) -> Dict:
        """转化漏斗分析"""
        if campaign_id:
            data = self.campaigns_df[self.campaigns_df['campaign_id'] == campaign_id]
            if data.empty:
                return {}
            data = data.iloc[0]
        else:
            # 汇总所有活动
            data = self.campaigns_df.sum()
        
        impressions = int(data['impressions'])
        clicks = int(data['clicks'])
        orders = int(data['orders'])
        
        funnel = {
            'impressions': impressions,
            'clicks': clicks,
            'orders': orders,
            'ctr': round(clicks / impressions * 100, 2) if impressions > 0 else 0,
            'cvr': round(orders / clicks * 100, 2) if clicks > 0 else 0,
            'overall_conversion': round(orders / impressions * 100, 4) if impressions > 0 else 0
        }
        
        return funnel
    
    def get_campaign_efficiency_ranking(self) -> pd.DataFrame:
        """活动效率排名"""
        efficiency = self.campaigns_df.copy()
        
        # 综合效率得分
        efficiency['roi_score'] = efficiency['roi'] / efficiency['roi'].max() * 40
        efficiency['cvr_score'] = efficiency['cvr'] / efficiency['cvr'].max() * 30
        efficiency['ctr_score'] = efficiency['ctr'] / efficiency['ctr'].max() * 30
        efficiency['efficiency_score'] = (
            efficiency['roi_score'] + 
            efficiency['cvr_score'] + 
            efficiency['ctr_score']
        ).round(2)
        
        return efficiency.sort_values('efficiency_score', ascending=False)
    
    def get_budget_allocation_suggestions(self) -> Dict:
        """预算分配建议"""
        channel_perf = self.get_channel_performance()
        
        total_budget = self.campaigns_df['budget'].sum()
        
        suggestions = []
        for _, row in channel_perf.iterrows():
            if row['roi'] > 100:
                suggested_percent = min(40, row['roi'] / channel_perf['roi'].max() * 35)
                suggestion = f"增加预算 - 高 ROI 渠道"
            elif row['roi'] > 50:
                suggested_percent = 25
                suggestion = "保持预算 - 表现良好"
            else:
                suggested_percent = 15
                suggestion = "优化或减少预算 - ROI 偏低"
            
            suggestions.append({
                'channel': row['channel'],
                'current_roi': row['roi'],
                'suggested_budget_percent': round(suggested_percent, 1),
                'suggested_budget_amount': round(total_budget * suggested_percent / 100, 2),
                'recommendation': suggestion
            })
        
        return pd.DataFrame(suggestions)
    
    def get_time_series_performance(self) -> pd.DataFrame:
        """时间序列表现"""
        self.campaigns_df['start_date'] = pd.to_datetime(self.campaigns_df['start_date'])
        
        time_perf = self.campaigns_df.sort_values('start_date')[
            ['campaign_id', 'campaign_name', 'start_date', 'end_date', 
             'revenue', 'roi', 'cvr']
        ]
        
        time_perf['revenue_cumulative'] = time_perf['revenue'].cumsum()
        
        return time_perf
