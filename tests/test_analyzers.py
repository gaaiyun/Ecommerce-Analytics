"""
电商运营分析平台 - 单元测试
Test Suite for E-commerce Analytics Platform
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from product_analyzer import ProductAnalyzer
from order_analyzer import OrderAnalyzer
from marketing_analyzer import MarketingAnalyzer


# ==================== 测试数据生成 ====================
@pytest.fixture
def sample_orders():
    """生成示例订单数据"""
    np.random.seed(42)
    n_orders = 100
    
    orders = {
        'order_id': [f'ORD{i:03d}' for i in range(1, n_orders + 1)],
        'customer_id': np.random.choice([f'C{i:03d}' for i in range(1, 51)], n_orders),
        'customer_name': [f'用户{i}' for i in range(1, n_orders + 1)],
        'product_id': np.random.choice([f'P{i:03d}' for i in range(1, 21)], n_orders),
        'product_name': [f'产品{i}' for i in range(1, n_orders + 1)],
        'category': np.random.choice(['电子产品', '办公用品', '家居用品'], n_orders),
        'quantity': np.random.randint(1, 10, n_orders),
        'unit_price': np.random.uniform(20, 500, n_orders).round(2),
        'cost_price': np.random.uniform(10, 300, n_orders).round(2),
        'order_date': [(datetime(2024, 1, 1) + timedelta(days=np.random.randint(0, 30))).strftime('%Y-%m-%d') 
                      for _ in range(n_orders)],
        'region': np.random.choice(['华东', '华北', '华南', '华西'], n_orders),
        'city': np.random.choice(['上海', '北京', '广州', '深圳', '成都'], n_orders),
        'payment_method': np.random.choice(['支付宝', '微信', '信用卡'], n_orders),
        'status': np.random.choice(['已完成', '已完成', '已完成', '已取消'], n_orders)
    }
    
    df = pd.DataFrame(orders)
    df['revenue'] = df['quantity'] * df['unit_price']
    df['cost'] = df['quantity'] * df['cost_price']
    df['profit'] = df['revenue'] - df['cost']
    
    return df


@pytest.fixture
def sample_products():
    """生成示例产品数据"""
    products = {
        'product_id': [f'P{i:03d}' for i in range(1, 21)],
        'product_name': [f'产品{i}' for i in range(1, 21)],
        'category': np.random.choice(['电子产品', '办公用品', '家居用品'], 20),
        'supplier': np.random.choice(['供应商 A', '供应商 B', '供应商 C'], 20),
        'cost_price': np.random.uniform(10, 300, 20).round(2),
        'sell_price': np.random.uniform(20, 500, 20).round(2),
        'stock_quantity': np.random.randint(50, 500, 20),
        'reorder_level': np.random.randint(20, 100, 20),
        'last_restock_date': '2024-01-01'
    }
    
    return pd.DataFrame(products)


@pytest.fixture
def sample_campaigns():
    """生成示例营销活动数据"""
    campaigns = {
        'campaign_id': [f'CMP{i:03d}' for i in range(1, 6)],
        'campaign_name': [f'活动{i}' for i in range(1, 6)],
        'start_date': ['2024-01-01', '2024-01-08', '2024-01-15', '2024-01-22', '2024-01-25'],
        'end_date': ['2024-01-07', '2024-01-14', '2024-01-21', '2024-01-28', '2024-01-31'],
        'channel': np.random.choice(['线上', '线下', '全渠道'], 5),
        'budget': np.random.uniform(1000, 5000, 5).round(2),
        'orders': np.random.randint(30, 100, 5),
        'revenue': np.random.uniform(5000, 15000, 5).round(2),
        'impressions': np.random.randint(50000, 200000, 5),
        'clicks': np.random.randint(3000, 15000, 5)
    }
    
    return pd.DataFrame(campaigns)


# ==================== ProductAnalyzer 测试 ====================
class TestProductAnalyzer:
    """商品分析器测试"""
    
    def test_sales_ranking(self, sample_orders, sample_products):
        """测试销售排名"""
        analyzer = ProductAnalyzer(sample_orders, sample_products)
        ranking = analyzer.get_sales_ranking(5)
        
        assert len(ranking) <= 5
        assert 'revenue' in ranking.columns
        assert 'quantity' in ranking.columns
        assert 'profit' in ranking.columns
        assert ranking['revenue'].is_monotonic_decreasing or len(ranking) == 0
    
    def test_profit_analysis(self, sample_orders, sample_products):
        """测试利润分析"""
        analyzer = ProductAnalyzer(sample_orders, sample_products)
        profit = analyzer.get_profit_analysis()
        
        assert 'profit_margin' in profit.columns
        assert all(profit['profit_margin'] >= 0) or all(profit['profit_margin'] <= 100)
        assert len(profit) > 0
    
    def test_category_performance(self, sample_orders, sample_products):
        """测试品类表现"""
        analyzer = ProductAnalyzer(sample_orders, sample_products)
        category = analyzer.get_category_performance()
        
        assert 'category' in category.columns
        assert 'revenue' in category.columns
        assert 'avg_order_value' in category.columns
        assert len(category) > 0
    
    def test_inventory_status(self, sample_orders, sample_products):
        """测试库存状态"""
        analyzer = ProductAnalyzer(sample_orders, sample_products)
        inventory = analyzer.get_inventory_status()
        
        assert 'stock_status' in inventory.columns
        assert all(inventory['stock_status'].isin(['低库存', '正常', '充足']))
        assert len(inventory) == len(sample_products)
    
    def test_restock_recommendations(self, sample_orders, sample_products):
        """测试补货建议"""
        analyzer = ProductAnalyzer(sample_orders, sample_products)
        recommendations = analyzer.get_restock_recommendations()
        
        if len(recommendations) > 0:
            assert 'recommendation' in recommendations.columns
            assert 'daily_sales' in recommendations.columns
            assert 'days_remaining' in recommendations.columns
    
    def test_price_optimization(self, sample_orders, sample_products):
        """测试价格优化建议"""
        analyzer = ProductAnalyzer(sample_orders, sample_products)
        suggestions = analyzer.get_price_optimization_suggestions()
        
        assert 'price_suggestion' in suggestions.columns
        assert 'profit_margin' in suggestions.columns
        assert len(suggestions) > 0


# ==================== OrderAnalyzer 测试 ====================
class TestOrderAnalyzer:
    """订单分析器测试"""
    
    def test_order_trend(self, sample_orders):
        """测试订单趋势"""
        analyzer = OrderAnalyzer(sample_orders)
        trend = analyzer.get_order_trend('D')
        
        assert 'order_count' in trend.columns
        assert 'revenue' in trend.columns
        assert 'avg_order_value' in trend.columns
        assert len(trend) > 0
    
    def test_regional_distribution(self, sample_orders):
        """测试地域分布"""
        analyzer = OrderAnalyzer(sample_orders)
        regional = analyzer.get_regional_distribution()
        
        assert 'region' in regional.columns
        assert 'order_percent' in regional.columns
        assert abs(regional['order_percent'].sum() - 100) < 0.1  # 允许浮点误差
    
    def test_city_analysis(self, sample_orders):
        """测试城市分析"""
        analyzer = OrderAnalyzer(sample_orders)
        cities = analyzer.get_city_analysis(10)
        
        assert len(cities) <= 10
        assert 'city' in cities.columns
        assert 'avg_order_value' in cities.columns
    
    def test_payment_method_analysis(self, sample_orders):
        """测试支付方式分析"""
        analyzer = OrderAnalyzer(sample_orders)
        payment = analyzer.get_payment_method_analysis()
        
        assert 'payment_method' in payment.columns
        assert len(payment) > 0
    
    def test_customer_analysis(self, sample_orders):
        """测试客户分析"""
        analyzer = OrderAnalyzer(sample_orders)
        customers = analyzer.get_customer_analysis(10)
        
        assert len(customers) <= 10
        assert 'customer_lifetime_value' in customers.columns
        assert 'avg_order_value' in customers.columns
    
    def test_repeat_purchase_analysis(self, sample_orders):
        """测试复购分析"""
        analyzer = OrderAnalyzer(sample_orders)
        repeat = analyzer.get_repeat_purchase_analysis()
        
        assert 'total_customers' in repeat
        assert 'repeat_rate' in repeat
        assert 0 <= repeat['repeat_rate'] <= 100
        assert repeat['total_customers'] > 0


# ==================== MarketingAnalyzer 测试 ====================
class TestMarketingAnalyzer:
    """营销分析器测试"""
    
    def test_campaign_roi(self, sample_campaigns, sample_orders):
        """测试活动 ROI"""
        analyzer = MarketingAnalyzer(sample_campaigns, sample_orders)
        roi = analyzer.get_campaign_roi()
        
        assert 'roi' in roi.columns
        assert 'profit' in roi.columns
        assert 'cost_per_order' in roi.columns
        assert len(roi) == len(sample_campaigns)
    
    def test_conversion_metrics(self, sample_campaigns, sample_orders):
        """测试转化指标"""
        analyzer = MarketingAnalyzer(sample_campaigns, sample_orders)
        conversion = analyzer.get_conversion_metrics()
        
        assert 'ctr' in conversion.columns
        assert 'cvr' in conversion.columns
        assert all(conversion['ctr'] >= 0)
        assert all(conversion['cvr'] >= 0)
    
    def test_channel_performance(self, sample_campaigns, sample_orders):
        """测试渠道表现"""
        analyzer = MarketingAnalyzer(sample_campaigns, sample_orders)
        channel = analyzer.get_channel_performance()
        
        assert 'channel' in channel.columns
        assert 'roi' in channel.columns
        assert len(channel) > 0
    
    def test_conversion_funnel(self, sample_campaigns, sample_orders):
        """测试转化漏斗"""
        analyzer = MarketingAnalyzer(sample_campaigns, sample_orders)
        funnel = analyzer.get_conversion_funnel()
        
        assert 'impressions' in funnel
        assert 'clicks' in funnel
        assert 'orders' in funnel
        assert 'ctr' in funnel
        assert 'cvr' in funnel
        assert funnel['impressions'] > 0
    
    def test_budget_allocation_suggestions(self, sample_campaigns, sample_orders):
        """测试预算分配建议"""
        analyzer = MarketingAnalyzer(sample_campaigns, sample_orders)
        suggestions = analyzer.get_budget_allocation_suggestions()
        
        if not suggestions.empty:
            assert 'channel' in suggestions.columns
            assert 'suggested_budget_percent' in suggestions.columns
            assert 'recommendation' in suggestions.columns


# ==================== 集成测试 ====================
class TestIntegration:
    """集成测试"""
    
    def test_full_analysis_pipeline(self, sample_orders, sample_products, sample_campaigns):
        """测试完整分析流程"""
        # 商品分析
        product_analyzer = ProductAnalyzer(sample_orders, sample_products)
        sales_rank = product_analyzer.get_sales_ranking(10)
        profit_analysis = product_analyzer.get_profit_analysis()
        
        # 订单分析
        order_analyzer = OrderAnalyzer(sample_orders)
        trend = order_analyzer.get_order_trend('D')
        regional = order_analyzer.get_regional_distribution()
        
        # 营销分析
        marketing_analyzer = MarketingAnalyzer(sample_campaigns, sample_orders)
        roi = marketing_analyzer.get_campaign_roi()
        funnel = marketing_analyzer.get_conversion_funnel()
        
        # 验证所有分析都返回了有效数据
        assert len(sales_rank) > 0
        assert len(profit_analysis) > 0
        assert len(trend) > 0
        assert len(regional) > 0
        assert len(roi) > 0
        assert funnel['impressions'] > 0


# ==================== 边界条件测试 ====================
class TestEdgeCases:
    """边界条件测试"""
    
    def test_empty_orders(self, sample_products):
        """测试空订单数据"""
        empty_orders = pd.DataFrame(columns=[
            'order_id', 'customer_id', 'product_id', 'quantity',
            'unit_price', 'cost_price', 'revenue', 'profit',
            'category', 'order_date', 'region', 'city', 'payment_method', 'status'
        ])
        
        analyzer = ProductAnalyzer(empty_orders, sample_products)
        ranking = analyzer.get_sales_ranking(10)
        
        assert len(ranking) == 0
    
    def test_single_order(self, sample_products):
        """测试单个订单"""
        single_order = pd.DataFrame({
            'order_id': ['ORD001'],
            'customer_id': ['C001'],
            'product_id': ['P001'],
            'quantity': [1],
            'unit_price': [100],
            'cost_price': [50],
            'revenue': [100],
            'profit': [50],
            'category': ['电子产品'],
            'order_date': ['2024-01-01'],
            'region': ['华东'],
            'city': ['上海'],
            'payment_method': ['支付宝'],
            'status': ['已完成']
        })
        
        analyzer = OrderAnalyzer(single_order)
        trend = analyzer.get_order_trend('D')
        
        assert len(trend) == 1
        assert trend.iloc[0]['order_count'] == 1


# ==================== 运行测试 ====================
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=.', '--cov-report=html'])
