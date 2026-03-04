# 📊 电商运营分析平台

一个功能强大的电商数据分析和运营优化平台，帮助电商运营人员快速洞察业务数据、优化运营策略。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32.0-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ 功能特性

### 🛍️ 商品分析
- **销售排名**: 实时查看商品销售 TOP 榜
- **利润分析**: 多维度利润分析，识别高利润产品
- **品类表现**: 各品类销售对比，优化品类结构
- **竞品监控**: 价格对比，市场份额分析

### 📦 订单分析
- **订单趋势**: 日/周/月订单趋势可视化
- **地域分布**: 销售地域分布热力图
- **客户分析**: 客户价值分层，识别 VIP 客户
- **复购分析**: 复购率统计，客户忠诚度分析

### 🎯 营销分析
- **ROI 分析**: 各营销活动投资回报率
- **转化漏斗**: 展示→点击→订单转化分析
- **渠道对比**: 多渠道效果对比
- **预算建议**: 智能预算分配建议

### ⚠️ 库存管理
- **库存预警**: 低库存自动预警
- **补货建议**: 基于销量的智能补货建议
- **周转分析**: 库存周转率分析

### 💰 价格优化
- **动态定价**: 基于利润率的定价建议
- **价格策略**: 差异化价格策略推荐

### 📊 报告导出
- **运营日报**: 一键生成运营日报
- **运营周报**: 周期性业务总结
- **自定义报告**: 支持 Markdown 格式导出

## 🚀 快速开始

### 1. 安装依赖

```bash
cd ecommerce-analytics
pip install -r requirements.txt
```

### 2. 运行应用

```bash
streamlit run dashboard.py
```

### 3. 访问应用

浏览器打开：http://localhost:8501

## 📁 项目结构

```
ecommerce-analytics/
├── dashboard.py              # 主界面
├── product_analyzer.py       # 商品分析模块
├── order_analyzer.py         # 订单分析模块
├── marketing_analyzer.py     # 营销分析模块
├── requirements.txt          # 依赖列表
├── README.md                 # 项目说明
├── data/                     # 数据目录
│   ├── orders.csv           # 订单数据
│   ├── products.csv         # 产品数据
│   └── campaigns.csv        # 营销活动数据
└── tests/                    # 测试目录
    └── test_analyzers.py    # 单元测试
```

## 📊 数据格式

### 订单数据 (orders.csv)
```csv
order_id,customer_id,customer_name,product_id,product_name,category,quantity,unit_price,cost_price,order_date,region,city,payment_method,status
ORD001,C001，张三，P001，无线鼠标，电子产品，2,89.00,45.00,2024-01-01，华东，上海，支付宝，已完成
```

### 产品数据 (products.csv)
```csv
product_id,product_name,category,supplier,cost_price,sell_price,stock_quantity,reorder_level,last_restock_date
P001，无线鼠标，电子产品，供应商 A,45.00,89.00,150,50,2024-01-01
```

### 营销活动数据 (campaigns.csv)
```csv
campaign_id,campaign_name,start_date,end_date,channel,budget,orders,revenue,impressions,clicks
CMP001，新年促销，2024-01-01,2024-01-07，全渠道，5000.00,85,12500.00,150000,8500
```

## 🧪 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行测试并生成覆盖率报告
pytest tests/ -v --cov=. --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html  # macOS/Linux
start htmlcov\index.html  # Windows
```

## 💡 使用技巧

### 1. 使用示例数据快速体验
- 启动应用后默认加载示例数据
- 包含 50 条订单、29 款产品、5 个营销活动

### 2. 上传自定义数据
- 在侧边栏选择"上传自定义数据"
- 按照数据格式要求上传 CSV 文件
- 支持实时数据更新

### 3. 导出分析报告
- 进入"报告导出"模块
- 选择日报或周报
- 点击下载按钮获取 Markdown 格式报告

### 4. 库存预警设置
- 在"库存预警"模块查看低库存商品
- 系统自动计算日均销量和补货建议
- 支持导出补货清单

## 📈 核心指标说明

| 指标 | 说明 | 计算公式 |
|------|------|----------|
| ROI | 投资回报率 | (营收 - 预算) / 预算 × 100% |
| CTR | 点击率 | 点击量 / 展示量 × 100% |
| CVR | 转化率 | 订单量 / 点击量 × 100% |
| 客单价 | 平均订单价值 | 总营收 / 订单数 |
| 复购率 | 重复购买客户占比 | 复购客户数 / 总客户数 × 100% |
| 毛利率 | 利润占营收比例 | 利润 / 营收 × 100% |
| 库存周转率 | 库存销售速度 | 销量 / 库存 × 100% |

## 🔧 自定义配置

### 修改主题颜色
编辑 `dashboard.py` 中的 Plotly 颜色配置：
```python
color_discrete_sequence=px.colors.qualitative.Set3
```

### 添加新的分析维度
在对应的 analyzer 模块中添加新方法：
```python
def get_custom_analysis(self):
    # 自定义分析逻辑
    pass
```

### 调整预警阈值
在 `product_analyzer.py` 中修改库存预警逻辑：
```python
if row['stock_quantity'] <= row['reorder_level']:
    return "立即补货"
```

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 更新日志

### v1.0.0 (2024-01)
- ✨ 初始版本发布
- 🎯 商品分析、订单分析、营销分析核心功能
- 📊 交互式数据可视化
- 📥 报告导出功能
- 🧪 完整单元测试覆盖

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 👨‍💻 技术栈

- **前端**: Streamlit
- **数据处理**: Pandas, NumPy
- **可视化**: Plotly
- **机器学习**: Scikit-learn (价格优化建议)
- **测试**: Pytest

## 🙏 致谢

感谢以下开源项目：
- [Streamlit](https://streamlit.io/)
- [Plotly](https://plotly.com/)
- [Pandas](https://pandas.pydata.org/)

---

**Made with ❤️ by 电商运营分析团队**

如有问题或建议，欢迎联系！
