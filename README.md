# TradingAgents 中文导读与学习索引

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-Agent%20Workflow-0F172A)
![Multi-Agent](https://img.shields.io/badge/Multi--Agent-Trading%20Research-0A7E8C)
![Status](https://img.shields.io/badge/Workspace-Research%20%26%20Learning-2E7D32)

</div>

<div align="center">

一个以多智能体交易研究为核心的仓库整理版文档。

本 README 优先回答三件事：怎么分析代码结构、怎么评估它离 A 股实盘还有多远、下一步应该怎么改进。

</div>

---

## 先看结论

> 这个仓库目前最适合的定位，不是“直接拿去 A 股实盘下单”，而是“作为多智能体交易研究框架的分析底座、实验底座、二次开发底座”。

### 1. 代码结构分析

项目的主轴不是单个脚本，而是一条由 LangGraph 驱动的多智能体决策流水线：

1. 分析师收集并解释市场证据。
2. 多空研究员进行观点对抗。
3. 研究经理把辩论收束成研究计划。
4. 交易员把研究计划翻译成交易提案。
5. 风险管理角色进行二次辩论。
6. 组合经理做最终批准与输出。

### 2. A 股实盘判断

这套系统可以作为 A 股实盘研究框架的雏形，但默认实现仍偏向美股/国际市场数据生态，距离真正的 A 股实盘还差三层关键能力：

1. A 股数据层：需要接入更适合 A 股的数据源，如 AkShare、Tushare、东方财富、同花顺或券商行情接口。
2. A 股交易执行层：需要把当前“研究输出”接到实盘下单接口，例如 QMT、Ptrade、恒生、掘金或券商开放平台。
3. 实盘风控层：需要增加交易时段、涨跌停、T+1、滑点、手续费、仓位约束、组合暴露等中国市场规则。

### 3. 改进方向

如果目标是把它改造成更接近 A 股可落地系统，优先顺序建议是：

1. 先替换数据源与 ticker 规范。
2. 再把最终决策结构化成真正可执行的信号对象。
3. 再接仿真撮合或券商接口。
4. 最后补齐回测、监控、审计日志和风控闭环。

---

## 仓库导航

```text
research-for-TradingAgents/
├─ README.md                # 当前这份总览文档
├─ 部署/                    # 通用部署说明、安装与运行文档
├─ 学习/                    # 学习笔记、结构讲解、阅读理解
└─ 源代码/                  # 可运行源代码、测试、CLI、资源文件
```

### 快速入口

- 源代码英文原始 README：[源代码/README.md](源代码/README.md)
- 通用部署文档：[部署/TradingAgents-通用部署指南.md](部署/TradingAgents-通用部署指南.md)
- 部署目录 Docker 入口：[部署/docker-compose.yml](部署/docker-compose.yml)
- 程序入口示例：[源代码/main.py](源代码/main.py)
- CLI 入口：[源代码/cli/main.py](源代码/cli/main.py)
- 默认配置：[源代码/tradingagents/default_config.py](源代码/tradingagents/default_config.py)
- 核心图编排：[源代码/tradingagents/graph/trading_graph.py](源代码/tradingagents/graph/trading_graph.py)
- 工作流搭建：[源代码/tradingagents/graph/setup.py](源代码/tradingagents/graph/setup.py)
- 新学习文档：[学习/2026-05-13-01-10-00-第三轮学习-运行周期回测与A股适配.md](学习/2026-05-13-01-10-00-第三轮学习-运行周期回测与A股适配.md)

---

## 项目是什么

TradingAgents 是一个多智能体金融交易研究框架。它通过多个角色分工，让大模型不再只给出一句“买/卖/观望”，而是先完成证据收集、观点辩论、交易规划和风险审议，再输出最终交易判断。

从工程角度看，它更像一个可编排的研究系统，而不是一个简单的问答脚本。

<p align="center">
  <img src="源代码/assets/schema.png" alt="TradingAgents 架构图" style="max-width: 100%; border-radius: 14px;" />
</p>

---

## 中文版源代码文档

### 核心能力概览

| 能力 | 说明 |
| --- | --- |
| 多智能体分工 | 将分析、辩论、交易、风控、批准拆成不同角色 |
| LangGraph 编排 | 用状态机和条件跳转控制完整流程 |
| 多模型接入 | 支持 OpenAI、Google、Anthropic、DeepSeek、Qwen、GLM、MiniMax、Ollama、Azure 等 |
| 多数据源接入 | 默认以 yfinance、Alpha Vantage 等为主 |
| 检查点恢复 | 中断后可从最近节点恢复 |
| 决策记忆 | 记录历史决策并生成后续反思 |
| CLI 交互 | 可通过命令行选择 ticker、日期、模型和研究深度 |

### 中文化架构说明

#### 1. 启动层

- [源代码/main.py](源代码/main.py) 是最小运行样例，直接创建图对象并调用一次传播。
- [源代码/cli/main.py](源代码/cli/main.py) 是面向真实使用的交互入口，负责收集参数、展示过程与输出结果。

这两层本身不负责交易判断，它们只是把输入送到真正的图编排系统。

#### 2. 配置层

[源代码/tradingagents/default_config.py](源代码/tradingagents/default_config.py) 决定了系统运行边界，包括：

1. 模型提供商与模型名称。
2. 输出语言。
3. 辩论轮数与风险讨论轮数。
4. 数据缓存、日志、记忆路径。
5. 数据供应商配置。
6. 通过 TRADINGAGENTS_* 环境变量覆盖默认参数。

这意味着系统是“配置优先”的，很多行为不需要改代码，只需要改环境变量或配置项。

#### 3. 图编排层

[源代码/tradingagents/graph/trading_graph.py](源代码/tradingagents/graph/trading_graph.py) 是系统中枢，[源代码/tradingagents/graph/setup.py](源代码/tradingagents/graph/setup.py) 负责搭建节点和边。

整体执行顺序可以概括为：

1. Analyst Team 形成证据空间。
2. Bull / Bear Researcher 进行多空辩论。
3. Research Manager 输出投资计划。
4. Trader 生成交易提案。
5. 风险角色继续做立场式风控辩论。
6. Portfolio Manager 输出最终决策。

#### 4. 共享状态层

[源代码/tradingagents/graph/propagation.py](源代码/tradingagents/graph/propagation.py) 负责创建一次分析任务的初始状态。所有 agent 不是互相直接调用，而是通过共享状态读写中间结果。

这就是为什么它更接近“状态机系统”，而不是“脚本串函数”。

#### 5. 条件控制层

[源代码/tradingagents/graph/conditional_logic.py](源代码/tradingagents/graph/conditional_logic.py) 负责决定：

1. 分析师是否还要继续调用工具。
2. 多空辩论是否继续。
3. 风险讨论是否继续。

系统不会让模型无限自由发挥，而是用程序显式设置上限，保证成本和流程可控。

#### 6. 持久化能力

这个项目内置两种长期能力：

1. 决策记忆：把历史决策写入记忆文件，下一次同类分析会带着反思上下文继续运行。
2. 检查点恢复：启用后，每个图节点完成后都能存档，中断后可继续跑。

这两点决定了它更适合研究迭代，而不是一次性脚本执行。

---

## 多个 Agents 分别做什么

### Analyst Team

| Agent | 作用 |
| --- | --- |
| Market Analyst | 从价格、指标、趋势中提炼技术面结论 |
| Sentiment Analyst | 汇总新闻标题、StockTwits、Reddit 等情绪信号 |
| News Analyst | 解释公司新闻与全球宏观新闻对交易环境的影响 |
| Fundamentals Analyst | 分析财务、现金流、资产负债与基本面质量 |

这组角色的本质是建立证据，而不是直接拍板交易。

### Researcher Team

| Agent | 作用 |
| --- | --- |
| Bull Researcher | 强化看多逻辑，挖掘上行空间 |
| Bear Researcher | 强化看空逻辑，拆解潜在风险 |

它们不是为了消除分歧，而是为了把分歧显式化，再交给上层角色裁决。

### Manager / Trader / Risk Team

| Agent | 作用 |
| --- | --- |
| Research Manager | 将多空辩论收束为结构化研究计划 |
| Trader | 把研究计划翻译成交易提案 |
| Aggressive Debator | 从高收益角度为激进方案辩护 |
| Conservative Debator | 从风险保护角度约束过度激进交易 |
| Neutral Debator | 尝试平衡收益与风险 |
| Portfolio Manager | 汇总所有上游输入并给出最终投资决策 |

---

## 运行方式

以下命令默认在 [源代码](源代码) 目录内执行。

如果你希望直接从部署目录启动 Docker 版通用环境，也可以执行：

```powershell
Set-Location .\部署
Copy-Item .env.example .env
docker compose run --rm tradingagents
```

这套入口会自动使用 [部署/docker-compose.yml](部署/docker-compose.yml) 指向 [源代码](源代码) 作为构建上下文，并把运行数据保存在 部署/data 目录下。

如果这台机器没有 Docker，也可以直接在部署目录执行本地脚本：

```powershell
Set-Location .\部署
.\run-local.cmd --install
```

脚本会在部署目录创建 .venv，从 [源代码](源代码) 安装项目，并默认读取 [部署/.env.example](部署/.env.example) 复制出的 .env。

当前部署模板默认使用 DeepSeek，预设模型为 deepseek-v4-pro 和 deepseek-v4-flash。实际运行前只需要把部署目录 .env 里的 DEEPSEEK_API_KEY 填上即可。

本地运行的日志、缓存和记忆文件也已经默认重定向到 部署/data/tradingagents，下次排查运行结果时直接看这个目录即可。

部署目录下的本地启动脚本还会自动准备一份 ASCII 路径的 CA 证书文件，用来规避 Windows 中文路径环境里 yfinance / curl_cffi 的 SSL 证书错误。

### 环境安装

```bash
conda create -n tradingagents python=3.13
conda activate tradingagents
pip install .
```

### CLI 启动

```bash
tradingagents
```

或者：

```bash
python -m cli.main
```

### 最小 Python 调用示例

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

config = DEFAULT_CONFIG.copy()
ta = TradingAgentsGraph(debug=True, config=config)
_, decision = ta.propagate("NVDA", "2024-05-10")
print(decision)
```

### 常见环境变量

```bash
TRADINGAGENTS_LLM_PROVIDER=openai
TRADINGAGENTS_DEEP_THINK_LLM=gpt-5.4
TRADINGAGENTS_QUICK_THINK_LLM=gpt-5.4-mini
TRADINGAGENTS_OUTPUT_LANGUAGE=Chinese
TRADINGAGENTS_CHECKPOINT_ENABLED=true
```

---

## A 股实盘改造建议

### 当前差距

当前默认实现更偏向“美股研究与通用金融分析框架”，主要原因有：

1. 默认 ticker 与 benchmark 规则以海外市场为主。
2. 数据抓取主要围绕 yfinance、Alpha Vantage 等国际接口。
3. 输出结果更偏研究建议，不是直接下单对象。
4. 风控逻辑尚未嵌入 A 股的市场规则与交易制度。

### 推荐落地路线

#### 第一阶段：改成 A 股研究版

1. 统一股票代码格式，例如 600519.SH、000001.SZ。
2. 将 market、fundamentals、news 数据流替换为 AkShare、Tushare 等。
3. 补充 A 股新闻源、公告源、研报源、北向资金、龙虎榜等特色信号。
4. 把 benchmark 替换成沪深 300、中证 500、上证指数等中国市场基准。

#### 第二阶段：改成 A 股仿真交易版

1. 给 Trader 输出增加更严格的结构化字段。
2. 加入撮合、滑点、手续费、涨跌停和 T+1 限制。
3. 对接本地数据库或事件总线，保存信号、订单、成交和复盘结果。

#### 第三阶段：改成 A 股实盘版

1. 接入券商交易终端或量化交易平台。
2. 增加盘前、盘中、盘后不同工作流。
3. 增加账户级风控、行业暴露、仓位上限、撤单与异常告警。
4. 增加人工确认开关，避免 LLM 直接自动下单。

---

## 我建议优先改哪些模块

如果后续要继续改仓库，优先阅读并改造这些位置：

| 模块 | 原因 |
| --- | --- |
| [源代码/tradingagents/dataflows](源代码/tradingagents/dataflows) | 决定数据质量，是 A 股化改造的第一入口 |
| [源代码/tradingagents/agents/analysts](源代码/tradingagents/agents/analysts) | 决定分析报告如何消费市场数据 |
| [源代码/tradingagents/agents/trader/trader.py](源代码/tradingagents/agents/trader/trader.py) | 决定交易建议是否可执行 |
| [源代码/tradingagents/agents/managers/portfolio_manager.py](源代码/tradingagents/agents/managers/portfolio_manager.py) | 决定最终决策结构与风控口径 |
| [源代码/tradingagents/graph/signal_processing.py](源代码/tradingagents/graph/signal_processing.py) | 适合承接“研究结论 → 可消费交易信号”的结构化转换 |

---

## 学习内容索引

仓库中已附加两轮学习文档，适合按顺序阅读：

### 第一轮学习

- 文档：[学习/2026-05-13-00-01-55-第一轮学习-程序逻辑讲解.md](学习/2026-05-13-00-01-55-第一轮学习-程序逻辑讲解.md)
- 重点：从入口、配置、图编排、传播、条件控制、记忆与恢复机制理解整个程序主逻辑。
- 适合谁：刚开始接触这个项目，想知道“程序到底怎么跑起来”的人。

### 第二轮学习

- 文档：[学习/2026-05-13-00-07-24-第二轮学习-多个Agents的功能与系统核心能力.md](学习/2026-05-13-00-07-24-第二轮学习-多个Agents的功能与系统核心能力.md)
- 重点：拆解多个 Agents 的职责边界，以及 agents 之外的系统核心能力。
- 适合谁：已经明白流程主线，想进一步理解“每个角色具体负责什么”的人。

### 推荐阅读顺序

1. 先读本 README，把全局图景建立起来。
2. 再读第一轮学习，理解程序主轴与调用链。
3. 再读第二轮学习，理解 agent 分工与系统能力。
4. 最后回到 [源代码/tradingagents](源代码/tradingagents) 对照源码逐个模块深入。

---

## 测试与工程信息

- 包名：tradingagents
- 当前版本：[源代码/pyproject.toml](源代码/pyproject.toml) 中记录为 0.2.5
- 测试目录：[源代码/tests](源代码/tests)
- 命令行入口：tradingagents -> cli.main:app

如需运行测试，可在 [源代码](源代码) 下执行：

```bash
pytest
```

---

## 适合怎样使用这个仓库

### 适合

1. 学习多智能体交易研究系统如何设计。
2. 作为金融 Agent 工作流的二次开发底座。
3. 做策略研究、报告生成、流程编排、风险讨论实验。

### 不适合直接开箱即用的场景

1. 直接接入 A 股账户全自动下单。
2. 在没有风控、撮合、监控、告警的情况下上线实盘。
3. 把 LLM 输出直接视为投资建议而不做人工复核。

---

## 一句话总结

如果把这个项目看成一句话，它不是“一个会预测涨跌的模型”，而是“一个把市场分析、观点冲突、交易规划和风险审议编排成完整流水线的多智能体研究框架”。

如果把这个仓库的下一步方向看成一句话，那么最现实的路线是：先做 A 股研究版，再做仿真交易版，最后才谈实盘自动化。