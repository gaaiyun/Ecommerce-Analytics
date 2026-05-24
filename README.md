# Ecommerce-Analytics

电商数据分析平台：Streamlit 仪表板（v1）+ headless CLI（v2）。

v1 提供 3 个 analyzer（订单 / 产品 / 营销）+ Streamlit 仪表板 + 20 个测试。
3 个 analyzer 已经是纯 pandas（不依赖 Streamlit），但数据预处理（计算
`revenue` / `profit` 列）混在 dashboard.py 里，外部脚本想用很别扭。

v2 在不动 v1 任何代码的前提下补：

- **`data_prep.py`** — 把数据预处理抽出来，幂等的纯函数，让 CLI 和外部脚本能复用
- **`__main__.py`** — 4 子命令 CLI 覆盖 overview / orders / products / marketing

## v2 新增

| 文件 | 干什么 |
|---|---|
| `data_prep.py` | `load_orders` / `prepare_orders`（补 revenue/cost/profit）+ `overview_metrics` KPI |
| `__main__.py` | CLI 4 子命令 |
| `tests/test_data_prep.py` | 12 测试：补列幂等 / 空数据 / 实样本加载 |

总测试 32 个（20 v1 + 12 v2），200ms 跑完。

## v1 仍保留（已经是纯 pandas）

| 模块 | 干什么 |
|---|---|
| `dashboard.py` | Streamlit 交互式主界面 |
| `order_analyzer.py` | 订单趋势 / 地域 / 城市 / 时段 |
| `product_analyzer.py` | 品类 / 畅销 / 库存预警 |
| `marketing_analyzer.py` | ROI / 转化率 / 渠道 |
| `data/{orders,products,campaigns}.csv` | 示例数据 |

## 安装

```bash
pip install -r requirements.txt
```

## 快速开始

### v2 headless CLI

```bash
# 整体 KPI
python __main__.py overview --orders data/orders.csv

# 订单趋势 + 地域分布 + Top 城市
python __main__.py orders --orders data/orders.csv --period D --top-n 5

# 产品品类 + 畅销 + 库存预警
python __main__.py products --orders data/orders.csv \
    --products data/products.csv --top-n 5

# 营销 ROI + 转化率 + 渠道
python __main__.py marketing --orders data/orders.csv \
    --campaigns data/campaigns.csv

# 所有命令都支持 -o report.json 导出
python __main__.py overview --orders data/orders.csv -o kpi.json
```

### v1 Streamlit 仪表板

```bash
streamlit run dashboard.py
```

### 库调用

```python
from data_prep import load_orders, load_products, load_campaigns, overview_metrics
from order_analyzer import OrderAnalyzer
from product_analyzer import ProductAnalyzer
from marketing_analyzer import MarketingAnalyzer

orders = load_orders("data/orders.csv")      # 自动补 revenue/profit
products = load_products("data/products.csv")
campaigns = load_campaigns("data/campaigns.csv")

# 整体 KPI
print(overview_metrics(orders))
# {'n_orders': 50, 'total_revenue': 11538.0, 'total_profit': 5527.0,
#  'profit_margin_pct': 47.9, 'avg_order_value': 230.76,
#  'unique_customers': 43}

# 详细分析
oa = OrderAnalyzer(orders)
print(oa.get_regional_distribution())

pa = ProductAnalyzer(orders, products)
print(pa.get_top_sellers(top_n=5))

ma = MarketingAnalyzer(campaigns, orders)
print(ma.get_campaign_roi())
```

## 真实输出例子

```
$ python __main__.py overview --orders data/orders.csv

{
  "n_orders": 50,
  "total_revenue": 11538.0,
  "total_profit": 5527.0,
  "profit_margin_pct": 47.9,
  "avg_order_value": 230.76,
  "unique_customers": 43
}
```

## 数据 schema

### orders.csv（必需）
| 列 | 必需 |
|---|---|
| order_id | 否 |
| customer_id | 否（影响 unique_customers）|
| product_id | 否 |
| category | 否 |
| quantity | **是** |
| unit_price | **是** |
| cost_price | 否（影响 profit 计算）|
| order_date | **是** |
| region | 否 |
| city | 否 |

`revenue` = `quantity * unit_price`；`cost` = `quantity * cost_price`；
`profit` = `revenue - cost`。已存在则不覆盖（幂等）。

### products.csv（可选）
| 列 | 用途 |
|---|---|
| product_id / product_name | 关联订单 |
| category / supplier | 分类统计 |
| stock_quantity / reorder_level | 低库存告警 |

### campaigns.csv（用于 marketing 命令）
| 列 | 用途 |
|---|---|
| campaign_id / campaign_name | 标识 |
| channel | 渠道分类 |
| budget / revenue | ROI 计算 |
| impressions / clicks / orders | 转化率 |

## 设计取舍

- **`prepare_orders` 幂等**：CSV 里已经有 `revenue` 列时不覆盖（用户可能预先算
  好了或想用自己的口径）。
- **CLI 命令独立、不复用全局状态**：每个子命令各自 `load_orders` 一遍，避免
  CSV 改动时缓存不一致。
- **products 命令可选 `--products` CSV**：没传时只算品类 / 畅销，不算低库存。
- **DataFrame → JSON**：日期列统一转 `YYYY-MM-DD` 字符串，让输出 JSON 干净。

## 项目结构

```
Ecommerce-Analytics/
├── __main__.py                  # v2 CLI
├── data_prep.py                 # v2 数据预处理
├── dashboard.py                 # v1 Streamlit
├── order_analyzer.py            # v1 订单分析
├── product_analyzer.py          # v1 产品分析
├── marketing_analyzer.py        # v1 营销分析
├── tests/                       # 32 测试
│   ├── test_analyzers.py        # v1
│   └── test_data_prep.py        # v2 新增
├── data/{orders,products,campaigns}.csv
├── start.bat
└── requirements.txt
```

## 测试

```bash
pytest tests/ --no-cov
```

32 个测试，200ms 跑完。

## 已知限制

- 没有 LLM commentary 层 —— ecommerce 场景非常依赖具体业务上下文（行业 /
  品类 / 季节），通用 LLM 给的洞察容易偏假大空，本仓库不强行加。需要的话
  可以参考 Sales-Dashboard 的 `llm_commentary.py` 模式自己接。
- 没有时间序列预测 —— 单独的事情，参考 Quant-Strategy-Backtester / Sales-Dashboard
  的 `forecast.py`。
- `product_analyzer.get_low_stock_products` 需要 products.csv 含 `stock_quantity`
  和 `reorder_level` 列；缺时该报告字段为空。

## 许可

MIT
