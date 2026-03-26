---
name: investment-analyzer
description: Investment analysis tool for A-shares, US stocks, and HK stocks. Combines yfinance for global markets and akshare for Chinese markets. Provides technical analysis, portfolio tracking, and market monitoring capabilities. Use when user requests stock analysis, price queries, technical indicators, or investment research.
---

# Investment Analyzer - 投资分析官

## Overview

综合投资分析技能，支持：
- A股、美股、港股实时行情
- 技术分析指标计算
- 投资组合跟踪
- 市场监控与信号发现

## Data Sources

| 市场 | 数据源 | 状态 |
|------|--------|------|
| 美股/全球 | yfinance | ✅ 正常 |
| A股/港股 | akshare | ⚠️ 需网络检查 |
| 技术指标 | TA-Lib + pandas-ta | ✅ 正常 |

## Quick Start

### 美股查询
```python
import yfinance as yf

# 获取股票信息
ticker = yf.Ticker("AAPL")
info = ticker.info
current_price = info.get("currentPrice")

# 获取历史数据
hist = ticker.history(period="1mo")
```

### A股查询 (AkShare)
```python
import akshare as ak

# A股实时行情
df = ak.stock_zh_a_spot_em()

# 个股历史数据
df = ak.stock_zh_a_hist(symbol="000001", period="daily", 
                        start_date="20240101", end_date="20241231")
```

### 技术分析
```python
import pandas_ta as ta

# 计算 RSI
rsi = df.ta.rsi(length=14)

# 计算 MACD
macd = df.ta.macd()

# 布林带
bbands = df.ta.bbands(length=20)
```

## Features

### 1. 实时行情监控
- 多市场股票实时价格
- 涨跌幅、成交量监控
- 板块热点追踪

### 2. 技术分析
- 趋势指标：MA、MACD、ADX
- 动量指标：RSI、KDJ、CCI
- 波动指标：布林带、ATR
- 成交量指标：OBV、VWAP

### 3. 基本面分析
- 财务报表获取
- 估值指标计算
- 行业对比分析

### 4. 投资组合管理
- 持仓跟踪
- 收益率计算
- 风险分析（VaR、夏普比率）

## Common Tasks

### 获取股票当前价格
```python
def get_price(symbol, market="US"):
    if market == "US":
        return yf.Ticker(symbol).info.get("currentPrice")
    elif market == "CN":
        return ak.stock_zh_a_spot_em()[...]  # 筛选代码
```

### 计算技术指标
```python
def add_indicators(df):
    df["RSI"] = ta.rsi(df["close"], length=14)
    df["MA20"] = ta.sma(df["close"], length=20)
    df["MA60"] = ta.sma(df["close"], length=60)
    return df
```

### 生成交易信号
```python
def generate_signals(df):
    signals = []
    if df["RSI"].iloc[-1] < 30:
        signals.append("RSI超卖，关注反弹机会")
    if df["close"].iloc[-1] > df["MA20"].iloc[-1]:
        signals.append("价格上穿20日均线，短期趋势转强")
    return signals
```

## References

- [yahoo-finance skill](../yahoo-finance/SKILL.md)
- [akshare-stock skill](../akshare-stock/SKILL.md)
- [pandas-ta documentation](https://github.com/twopirllc/pandas-ta)
- [TA-Lib documentation](https://mrjbq7.github.io/ta-lib/)
