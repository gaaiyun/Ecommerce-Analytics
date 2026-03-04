"""
电商运营分析平台 - 主界面
E-commerce Analytics Dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

# 导入分析模块
from product_analyzer import ProductAnalyzer
from order_analyzer import OrderAnalyzer
from marketing_analyzer import MarketingAnalyzer


# ==================== 页面配置 ====================
st.set_page_config(
    page_title="电商运营分析平台",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS 样式
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
</style>
""", unsafe_allow_html=True)


# ==================== 数据加载缓存 ====================
@st.cache_data
def load_data():
    """加载示例数据"""
    orders_df = pd.read_csv('data/orders.csv')
    products_df = pd.read_csv('data/products.csv')
    campaigns_df = pd.read_csv('data/campaigns.csv')
    
    # 计算订单的营收和利润
    orders_df['revenue'] = orders_df['quantity'] * orders_df['unit_price']
    orders_df['cost'] = orders_df['quantity'] * orders_df['cost_price']
    orders_df['profit'] = orders_df['revenue'] - orders_df['cost']
    
    # 计算营销活动的 ROI
    campaigns_df['roi'] = ((campaigns_df['revenue'] - campaigns_df['budget']) / 
                          campaigns_df['budget'] * 100).round(2)
    campaigns_df['ctr'] = (campaigns_df['clicks'] / campaigns_df['impressions'] * 100).round(2)
    campaigns_df['cvr'] = (campaigns_df['orders'] / campaigns_df['clicks'] * 100).round(2)
    
    return orders_df, products_df, campaigns_df


# ==================== 侧边栏 ====================
st.sidebar.title("📊 电商运营分析平台")
st.sidebar.markdown("---")

# 数据上传选项
upload_option = st.sidebar.radio(
    "数据源选择",
    ["使用示例数据", "上传自定义数据"]
)

if upload_option == "上传自定义数据":
    st.sidebar.info("📁 请上传以下 CSV 文件：")
    orders_file = st.sidebar.file_uploader("订单数据 (orders.csv)", type=['csv'])
    products_file = st.sidebar.file_uploader("产品数据 (products.csv)", type=['csv'])
    campaigns_file = st.sidebar.file_uploader("营销活动数据 (campaigns.csv)", type=['csv'])
    
    if orders_file and products_file and campaigns_file:
        orders_df = pd.read_csv(orders_file)
        products_df = pd.read_csv(products_file)
        campaigns_df = pd.read_csv(campaigns_file)
        
        # 计算必要字段
        if 'revenue' not in orders_df.columns:
            orders_df['revenue'] = orders_df['quantity'] * orders_df['unit_price']
        if 'profit' not in orders_df.columns:
            orders_df['profit'] = orders_df['revenue'] - (orders_df['quantity'] * orders_df['cost_price'])
        
        st.sidebar.success("✅ 数据加载成功！")
    else:
        st.warning("📤 请上传所有必需的数据文件，或选择使用示例数据。")
        st.stop()
else:
    orders_df, products_df, campaigns_df = load_data()
    st.sidebar.success("✅ 示例数据已加载")

# 分析模块选择
st.sidebar.markdown("---")
analysis_module = st.sidebar.selectbox(
    "选择分析模块",
    ["📈 总览仪表盘",
     "🛍️ 商品分析",
     "📦 订单分析",
     "🎯 营销分析",
     "⚠️ 库存预警",
     "💰 价格优化",
     "📊 报告导出"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**关于**")
st.sidebar.markdown("版本：v1.0.0")
st.sidebar.markdown("技术栈：Streamlit + Plotly")


# ==================== 主界面 ====================

# 标题
st.title("📊 电商运营分析平台")
st.markdown("---")


# ==================== 总览仪表盘 ====================
if analysis_module == "📈 总览仪表盘":
    st.header("📈 运营总览")
    
    # 关键指标卡片
    col1, col2, col3, col4 = st.columns(4)
    
    total_revenue = orders_df['revenue'].sum()
    total_profit = orders_df['profit'].sum()
    total_orders = len(orders_df)
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    with col1:
        st.metric(
            label="💰 总营收",
            value=f"¥{total_revenue:,.2f}",
            delta="+12.5%"
        )
    
    with col2:
        st.metric(
            label="📊 总利润",
            value=f"¥{total_profit:,.2f}",
            delta=f"{(total_profit/total_revenue*100):.1f}% 利润率"
        )
    
    with col3:
        st.metric(
            label="📦 订单总数",
            value=f"{total_orders:,}",
            delta="+8.3%"
        )
    
    with col4:
        st.metric(
            label="🛒 客单价",
            value=f"¥{avg_order_value:.2f}",
            delta="+4.2%"
        )
    
    st.markdown("---")
    
    # 图表行 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📅 订单趋势")
        orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
        daily_orders = orders_df.groupby('order_date').agg({
            'order_id': 'count',
            'revenue': 'sum'
        }).reset_index()
        daily_orders.rename(columns={'order_id': 'order_count'}, inplace=True)
        
        fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
        fig_trend.add_trace(
            go.Bar(x=daily_orders['order_date'], y=daily_orders['order_count'],
                   name='订单数', marker_color='#636EFA'),
            secondary_y=False
        )
        fig_trend.add_trace(
            go.Scatter(x=daily_orders['order_date'], y=daily_orders['revenue'],
                       name='营收', marker_color='#EF553B', mode='lines+markers'),
            secondary_y=True
        )
        fig_trend.update_layout(
            height=400,
            xaxis_title="日期",
            showlegend=True,
            hovermode='x unified'
        )
        fig_trend.update_yaxes(title_text="订单数", secondary_y=False)
        fig_trend.update_yaxes(title_text="营收 (¥)", secondary_y=True)
        st.plotly_chart(fig_trend, use_container_width=True)
    
    with col2:
        st.subheader("🗺️ 地域分布")
        regional = orders_df.groupby('region').agg({
            'revenue': 'sum',
            'order_id': 'count'
        }).reset_index()
        regional.rename(columns={'order_id': 'order_count'}, inplace=True)
        
        fig_region = px.pie(
            regional,
            values='revenue',
            names='region',
            title='各区域营收占比',
            color_discrete_sequence=px.colors.qualitative.Set3,
            hole=0.4
        )
        fig_region.update_traces(textposition='inside', textinfo='percent+label')
        fig_region.update_layout(height=400)
        st.plotly_chart(fig_region, use_container_width=True)
    
    # 图表行 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏷️ 品类表现")
        category_perf = orders_df.groupby('category').agg({
            'revenue': 'sum',
            'profit': 'sum'
        }).reset_index()
        
        fig_category = px.bar(
            category_perf,
            x='category',
            y='revenue',
            color='profit',
            title='各品类营收与利润',
            color_continuous_scale='RdYlGn',
            labels={'revenue': '营收 (¥)', 'profit': '利润 (¥)', 'category': '品类'}
        )
        fig_category.update_layout(height=400)
        st.plotly_chart(fig_category, use_container_width=True)
    
    with col2:
        st.subheader("🎯 营销活动 ROI")
        fig_campaign = px.bar(
            campaigns_df,
            x='campaign_name',
            y='roi',
            color='roi',
            title='各活动投资回报率',
            color_continuous_scale='RdYlGn',
            labels={'roi': 'ROI (%)', 'campaign_name': '活动名称'}
        )
        fig_campaign.update_layout(height=400)
        st.plotly_chart(fig_campaign, use_container_width=True)


# ==================== 商品分析 ====================
elif analysis_module == "🛍️ 商品分析":
    st.header("🛍️ 商品分析")
    
    analyzer = ProductAnalyzer(orders_df, products_df)
    
    # 选项卡
    tab1, tab2, tab3, tab4 = st.tabs([
        "销售排名", "利润分析", "品类表现", "竞品监控"
    ])
    
    with tab1:
        st.subheader("🏆 商品销售排名 TOP 10")
        sales_rank = analyzer.get_sales_ranking(10)
        
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(
                sales_rank.sort_values('revenue'),
                y='product_name',
                x='revenue',
                orientation='h',
                title='营收排名',
                color='revenue',
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                sales_rank.sort_values('quantity', ascending=False),
                y='product_name',
                x='quantity',
                orientation='h',
                title='销量排名',
                color='quantity',
                color_continuous_scale='Greens'
            )
            fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(
            sales_rank[['product_id', 'product_name', 'category', 'quantity', 'revenue', 'profit']],
            use_container_width=True
        )
    
    with tab2:
        st.subheader("💰 利润分析")
        profit_analysis = analyzer.get_profit_analysis()
        
        fig = px.scatter(
            profit_analysis,
            x='revenue',
            y='profit_margin',
            size='quantity',
            color='profit_margin',
            hover_name='product_name',
            title='产品利润矩阵（气泡大小=销量）',
            color_continuous_scale='RdYlGn',
            labels={'revenue': '营收 (¥)', 'profit_margin': '利润率 (%)'}
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(
            profit_analysis[['product_id', 'product_name', 'revenue', 'profit', 'profit_margin']],
            use_container_width=True
        )
    
    with tab3:
        st.subheader("🏷️ 品类表现")
        category_perf = analyzer.get_category_performance()
        
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(
                category_perf,
                x='category',
                y='revenue',
                title='各品类营收',
                color='revenue',
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                category_perf,
                x='category',
                y='avg_order_value',
                title='各品类平均订单价值',
                color='avg_order_value',
                color_continuous_scale='Greens'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(category_perf, use_container_width=True)
    
    with tab4:
        st.subheader("🔍 竞品价格监控")
        competitor = analyzer.get_competitor_analysis()
        
        if not competitor.empty:
            fig = px.bar(
                competitor,
                x='product_name',
                y=['our_price', 'competitor_avg_price'],
                barmode='group',
                title='我们与竞品价格对比',
                labels={'value': '价格 (¥)', 'product_name': '产品'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(competitor, use_container_width=True)
        else:
            st.info("暂无竞品数据")


# ==================== 订单分析 ====================
elif analysis_module == "📦 订单分析":
    st.header("📦 订单分析")
    
    analyzer = OrderAnalyzer(orders_df)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "订单趋势", "地域分析", "客户分析", "支付方式", "复购分析"
    ])
    
    with tab1:
        st.subheader("📅 订单趋势分析")
        trend = analyzer.get_order_trend('D')
        
        col1, col2 = st.columns(2)
        with col1:
            fig = px.line(
                trend,
                x='order_date',
                y='order_count',
                title='每日订单数趋势',
                markers=True
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.line(
                trend,
                x='order_date',
                y='revenue',
                title='每日营收趋势',
                markers=True,
                color_discrete_sequence=['#EF553B']
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(trend, use_container_width=True)
    
    with tab2:
        st.subheader("🗺️ 地域分布分析")
        regional = analyzer.get_regional_distribution()
        city_analysis = analyzer.get_city_analysis(10)
        
        col1, col2 = st.columns(2)
        with col1:
            fig = px.choropleth(
                regional,
                locations=['CN-SH', 'CN-BJ', 'CN-GD', 'CN-ZJ', 'CN-TJ', 'CN-SC', 'CN-JS', 'CN-CQ', 'CN-HE', 'CN-FJ'],
                locationmode="ISO-3166-2",
                color='revenue',
                scope="asia",
                title='中国区域营收分布',
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                city_analysis,
                x='city',
                y='revenue',
                title='城市 TOP 10',
                color='revenue',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(regional, use_container_width=True)
    
    with tab3:
        st.subheader("👥 客户分析")
        customer_analysis = analyzer.get_customer_analysis(15)
        
        fig = px.scatter(
            customer_analysis,
            x='order_count',
            y='total_revenue',
            size='total_quantity',
            hover_name='customer_name',
            title='客户价值矩阵',
            labels={'order_count': '订单数', 'total_revenue': '总消费 (¥)'}
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(customer_analysis, use_container_width=True)
    
    with tab4:
        st.subheader("💳 支付方式分析")
        payment_analysis = analyzer.get_payment_method_analysis()
        
        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(
                payment_analysis,
                values='order_count',
                names='payment_method',
                title='支付方式订单占比',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                payment_analysis,
                x='payment_method',
                y='revenue',
                title='各支付方式营收',
                color='revenue',
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(payment_analysis, use_container_width=True)
    
    with tab5:
        st.subheader("🔄 复购分析")
        repeat_analysis = analyzer.get_repeat_purchase_analysis()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总客户数", f"{repeat_analysis['total_customers']}")
        with col2:
            st.metric("复购客户数", f"{repeat_analysis['repeat_customers']}")
        with col3:
            st.metric("复购率", f"{repeat_analysis['repeat_rate']}%")
        
        st.info(f"💡 平均每个客户下单 {repeat_analysis['avg_orders_per_customer']} 次")


# ==================== 营销分析 ====================
elif analysis_module == "🎯 营销分析":
    st.header("🎯 营销效果分析")
    
    analyzer = MarketingAnalyzer(campaigns_df, orders_df)
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "活动 ROI", "转化漏斗", "渠道分析", "预算建议"
    ])
    
    with tab1:
        st.subheader("📊 活动 ROI 分析")
        roi_analysis = analyzer.get_campaign_roi()
        
        fig = px.bar(
            roi_analysis,
            x='campaign_name',
            y='roi',
            color='roi',
            title='各活动投资回报率',
            color_continuous_scale='RdYlGn',
            labels={'roi': 'ROI (%)', 'campaign_name': '活动名称'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(
            roi_analysis[['campaign_id', 'campaign_name', 'budget', 'revenue', 'roi', 'profit']],
            use_container_width=True
        )
    
    with tab2:
        st.subheader("🔻 转化漏斗")
        
        # 总体漏斗
        funnel_data = analyzer.get_conversion_funnel()
        
        fig = go.Figure(go.Funnel(
            y = ["展示量", "点击量", "订单量"],
            x = [funnel_data['impressions'], funnel_data['clicks'], funnel_data['orders']],
            textposition = "inside",
            textinfo = "value+percent initial"
        ))
        fig.update_layout(
            title="整体转化漏斗",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 各活动转化率
        col1, col2 = st.columns(2)
        with col1:
            conversion_metrics = analyzer.get_conversion_metrics()
            fig = px.bar(
                conversion_metrics,
                x='campaign_name',
                y='cvr',
                title='各活动转化率 (CVR)',
                color='cvr',
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                conversion_metrics,
                x='campaign_name',
                y='ctr',
                title='各活动点击率 (CTR)',
                color='ctr',
                color_continuous_scale='Greens'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(conversion_metrics, use_container_width=True)
    
    with tab3:
        st.subheader("📱 渠道表现分析")
        channel_perf = analyzer.get_channel_performance()
        
        fig = px.bar(
            channel_perf,
            x='channel',
            y=['budget', 'revenue'],
            barmode='group',
            title='各渠道预算 vs 营收',
            labels={'value': '金额 (¥)', 'channel': '渠道'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(channel_perf, use_container_width=True)
    
    with tab4:
        st.subheader("💡 预算分配建议")
        budget_suggestions = analyzer.get_budget_allocation_suggestions()
        
        if not budget_suggestions.empty:
            fig = px.bar(
                budget_suggestions,
                x='channel',
                y='suggested_budget_percent',
                color='current_roi',
                title='建议预算分配比例',
                labels={'suggested_budget_percent': '建议预算占比 (%)', 'channel': '渠道'},
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(budget_suggestions, use_container_width=True)


# ==================== 库存预警 ====================
elif analysis_module == "⚠️ 库存预警":
    st.header("⚠️ 库存预警与补货建议")
    
    analyzer = ProductAnalyzer(orders_df, products_df)
    inventory = analyzer.get_inventory_status()
    restock_rec = analyzer.get_restock_recommendations()
    
    # 库存状态概览
    col1, col2, col3 = st.columns(3)
    
    low_stock_count = len(inventory[inventory['stock_quantity'] <= inventory['reorder_level']])
    normal_stock_count = len(inventory[(inventory['stock_quantity'] > inventory['reorder_level']) & 
                                       (inventory['stock_quantity'] <= inventory['reorder_level'] * 2)])
    sufficient_stock_count = len(inventory[inventory['stock_quantity'] > inventory['reorder_level'] * 2])
    
    with col1:
        st.metric("🔴 低库存商品", f"{low_stock_count} 款")
    with col2:
        st.metric("🟡 正常库存商品", f"{normal_stock_count} 款")
    with col3:
        st.metric("🟢 库存充足商品", f"{sufficient_stock_count} 款")
    
    st.markdown("---")
    
    # 库存状态可视化
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(
            inventory,
            names='stock_status',
            title='库存状态分布',
            color='stock_status',
            color_discrete_map={'低库存': '#EF553B', '正常': '#FFA15A', '充足': '#636EFA'}
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            inventory.sort_values('turnover_rate', ascending=False).head(10),
            x='product_name',
            y='turnover_rate',
            title='库存周转率 TOP 10',
            color='turnover_rate',
            color_continuous_scale='Reds'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # 补货建议
    st.subheader("📋 智能补货建议")
    if not restock_rec.empty:
        st.warning(f"⚠️ 共有 {len(restock_rec)} 款商品需要关注库存")
        
        for _, row in restock_rec.iterrows():
            with st.expander(f"{row['product_name']} - {row['recommendation']}"):
                st.write(f"**当前库存**: {row['stock_quantity']}")
                st.write(f"**安全库存**: {row['reorder_level']}")
                st.write(f"**日均销量**: {row['daily_sales']}")
                st.write(f"**预计可售天数**: {row['days_remaining']} 天")
        
        st.dataframe(
            restock_rec[['product_id', 'product_name', 'stock_quantity', 'reorder_level', 
                        'daily_sales', 'days_remaining', 'recommendation']],
            use_container_width=True
        )
    else:
        st.success("✅ 所有商品库存充足，无需补货")
    
    # 完整库存表
    st.subheader("📦 完整库存状态")
    st.dataframe(
        inventory[['product_id', 'product_name', 'stock_quantity', 'reorder_level', 
                  'stock_status', 'turnover_rate']],
        use_container_width=True
    )


# ==================== 价格优化 ====================
elif analysis_module == "💰 价格优化":
    st.header("💰 价格优化建议")
    
    analyzer = ProductAnalyzer(orders_df, products_df)
    price_suggestions = analyzer.get_price_optimization_suggestions()
    
    # 价格策略矩阵
    fig = px.scatter(
        price_suggestions,
        x='profit_margin',
        y='product_name',
        color='profit_margin',
        color_continuous_scale='RdYlGn',
        title='产品利润率分布',
        labels={'profit_margin': '利润率 (%)', 'product_name': '产品'}
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # 价格建议表
    st.subheader("💡 价格优化建议")
    
    # 按利润率分组显示
    col1, col2, col3 = st.columns(3)
    
    low_margin = price_suggestions[price_suggestions['profit_margin'] < 30]
    mid_margin = price_suggestions[(price_suggestions['profit_margin'] >= 30) & 
                                   (price_suggestions['profit_margin'] <= 60)]
    high_margin = price_suggestions[price_suggestions['profit_margin'] > 60]
    
    with col1:
        st.subheader("🔴 低利润产品 (<30%)")
        if not low_margin.empty:
            for _, row in low_margin.iterrows():
                st.warning(f"{row['product_name']}: {row['price_suggestion']}")
        else:
            st.info("无")
    
    with col2:
        st.subheader("🟡 中等利润产品 (30-60%)")
        if not mid_margin.empty:
            for _, row in mid_margin.head(5).iterrows():
                st.info(f"{row['product_name']}: {row['price_suggestion']}")
        else:
            st.info("无")
    
    with col3:
        st.subheader("🟢 高利润产品 (>60%)")
        if not high_margin.empty:
            for _, row in high_margin.iterrows():
                st.success(f"{row['product_name']}: {row['price_suggestion']}")
        else:
            st.info("无")
    
    st.dataframe(price_suggestions, use_container_width=True)


# ==================== 报告导出 ====================
elif analysis_module == "📊 报告导出":
    st.header("📊 报告导出")
    
    # 生成日报/周报
    report_type = st.radio("选择报告类型", ["运营日报", "运营周报"])
    
    if st.button("📥 生成报告"):
        # 计算关键指标
        total_revenue = orders_df['revenue'].sum()
        total_profit = orders_df['profit'].sum()
        total_orders = len(orders_df)
        avg_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        # 生成报告内容
        report_content = f"""
# {report_type}

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 一、核心指标概览

| 指标 | 数值 |
|------|------|
| 总营收 | ¥{total_revenue:,.2f} |
| 总利润 | ¥{total_profit:,.2f} |
| 订单总数 | {total_orders} |
| 平均利润率 | {avg_margin:.2f}% |
| 客单价 | ¥{total_revenue/total_orders:.2f} |

## 二、商品表现

### 销售 TOP 5
"""
        
        analyzer = ProductAnalyzer(orders_df, products_df)
        top_products = analyzer.get_sales_ranking(5)
        
        for i, row in top_products.iterrows():
            report_content += f"{i+1}. {row['product_name']} - 营收：¥{row['revenue']:.2f}\n"
        
        report_content += """
## 三、订单分析

### 地域分布
"""
        
        order_analyzer = OrderAnalyzer(orders_df)
        regional = order_analyzer.get_regional_distribution()
        
        for _, row in regional.iterrows():
            report_content += f"- {row['region']}: ¥{row['revenue']:.2f} ({row['revenue_percent']}%)\n"
        
        report_content += """
## 四、营销效果

"""
        
        mkt_analyzer = MarketingAnalyzer(campaigns_df, orders_df)
        campaign_roi = mkt_analyzer.get_campaign_roi()
        
        for _, row in campaign_roi.iterrows():
            report_content += f"- {row['campaign_name']}: ROI {row['roi']}%, 营收 ¥{row['revenue']:.2f}\n"
        
        report_content += """
## 五、库存预警

"""
        
        inventory = analyzer.get_inventory_status()
        low_stock = inventory[inventory['stock_quantity'] <= inventory['reorder_level']]
        
        if not low_stock.empty:
            report_content += "以下商品需要补货：\n"
            for _, row in low_stock.iterrows():
                report_content += f"- {row['product_name']}: 当前库存 {row['stock_quantity']}, 安全库存 {row['reorder_level']}\n"
        else:
            report_content += "所有商品库存充足。\n"
        
        report_content += """
---
*报告由电商运营分析平台自动生成*
"""
        
        st.download_button(
            label="📥 下载报告 (Markdown)",
            data=report_content,
            file_name=f"{report_type}_{datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown"
        )
        
        # 显示报告预览
        st.markdown("---")
        st.subheader("📖 报告预览")
        st.markdown(report_content)


# ==================== 页脚 ====================
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>电商运营分析平台 v1.0.0 | Powered by Streamlit + Plotly</p>
    </div>
    """,
    unsafe_allow_html=True
)
