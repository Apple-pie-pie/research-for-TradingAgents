# TradingAgents 通用部署指南

本文基于 TauricResearch/TradingAgents 官方仓库当前公开 README、Docker 配置、环境变量示例和 CLI 入口整理，目标是给出一份不依赖 A 股场景、面向通用研究部署的落地说明。

当前工作区已经把可直接执行的 Docker 部署入口放到了部署目录下：

- docker-compose.yml：统一从部署目录启动容器
- .env.example：通用环境变量模板
- data/：容器运行后自动生成的持久化目录
- .venv/：本地 Python 部署时的独立虚拟环境目录
- run-local.cmd：Windows 下推荐的本地启动脚本
- run-local.ps1：部署目录下的本地启动脚本

---

## 1. 部署目标

TradingAgents 本质上是一个多智能体金融研究框架。部署它的核心目标不是直接接券商实盘，而是先把下面这条链路稳定跑通：

1. 安装 Python 运行环境。
2. 安装 TradingAgents 及依赖。
3. 配置至少一组可用的大模型 API Key。
4. 可选配置金融数据 API Key。
5. 启动 CLI，完成一次分析任务。
6. 确认缓存、检查点、记忆日志能正常写入。

如果这 6 步跑通，说明“通用研究部署”已经完成。

---

## 2. 部署前提

### 2.1 最低要求

- Git
- Python 3.10 及以上
- 推荐使用 Python 3.12 或 3.13
- 一组可用的 LLM Provider API Key
- 联网环境

### 2.2 推荐环境

- 操作系统：Windows、Linux、macOS 均可
- Python 环境管理：conda 或 venv
- 容器部署：Docker Desktop 或 Docker Engine + Docker Compose

### 2.3 部署方式选择

建议先在本地 Python 环境完成首次部署，再决定是否切换到 Docker。

- 本地 Python 部署：最适合调试、改代码、看日志、跑测试
- Docker 部署：最适合隔离环境、快速启动、团队共享运行方式
- Ollama 部署：适合本地或远程自托管模型

---

## 3. 获取源码

官方仓库地址：

- https://github.com/TauricResearch/TradingAgents

克隆命令：

```bash
git clone https://github.com/TauricResearch/TradingAgents.git
cd TradingAgents
```

如果你当前使用的是本工作区整理版结构，则实际可运行代码位于 源代码 目录：

```bash
cd 源代码
```

如果你要按本仓库整理后的方式直接部署，推荐切换到部署目录执行：

```bash
cd 部署
```

---

## 4. 本地 Python 部署

这是最推荐的第一种部署方式，因为最容易定位依赖、环境变量和 CLI 问题。

如果你希望把“部署动作”和“可运行环境”都放在部署目录下，可直接使用本工作区提供的脚本：

```powershell
Set-Location .\部署
\.\run-local.cmd --install
```

脚本会在部署目录下创建 .venv，并从 ../源代码 安装项目。

### 4.1 创建虚拟环境

官方 README 使用 conda 示例：

```bash
conda create -n tradingagents python=3.13
conda activate tradingagents
```

如果你不使用 conda，也可以用 venv：

```bash
python -m venv .venv
```

Linux 或 macOS 激活：

```bash
source .venv/bin/activate
```

Windows PowerShell 激活：

```powershell
.\.venv\Scripts\Activate.ps1
```

如果你使用部署目录脚本，则不需要手工激活，直接执行：

```powershell
.\run-local.cmd
```

如果你更偏好 PowerShell 脚本，也可以使用 run-local.ps1；但在默认执行策略较严格的 Windows 环境中，优先建议使用 run-local.cmd。

### 4.2 安装依赖

在项目根目录执行：

```bash
pip install .
```

如果你当前位于部署目录，等价命令是：

```powershell
.\.venv\Scripts\python.exe -m pip install ..\源代码
```

这个命令会根据 pyproject.toml 安装项目以及依赖。当前关键依赖包括：

- langgraph
- langchain-openai
- langchain-google-genai
- langchain-anthropic
- questionary
- rich
- typer
- yfinance
- pandas
- backtrader

### 4.3 校验安装是否成功

安装完成后，至少确认这两个入口可用：

```bash
tradingagents --help
python -m cli.main --help
```

如果两者至少有一个可以正常输出帮助信息，说明 CLI 安装基本正常。

在部署目录中，也可以执行：

```powershell
.\.venv\Scripts\python.exe -m cli.main --help
```

如果你使用部署目录里默认的 DeepSeek 配置，则常用启动命令就是：

```powershell
.\run-local.cmd
```

即使你不通过 run-local.cmd，而是直接执行 tradingagents 或 python -m cli.main，当前代码也会在启动时自动把 certifi 证书复制到 LOCALAPPDATA 下的 ASCII 路径，并设置 SSL_CERT_FILE、REQUESTS_CA_BUNDLE、CURL_CA_BUNDLE，避免 Windows 中文路径环境下 yfinance 或 curl_cffi 报错找不到 CA 文件。

---

## 5. 环境变量配置

TradingAgents 支持多家模型供应商。你不需要同时配置全部，只需要配置你实际要使用的那一组。

### 5.1 推荐做法

先复制环境变量模板文件：

Linux 或 macOS：

```bash
cp .env.example .env
```

Windows PowerShell：

```powershell
Copy-Item .env.example .env
```

然后在 .env 中填写你要用的 API Key。

当前部署目录模板已经默认切到 DeepSeek。如果你就是要用 DeepSeek，只需要补上密钥即可：

```env
DEEPSEEK_API_KEY=你的密钥
TRADINGAGENTS_LLM_PROVIDER=deepseek
TRADINGAGENTS_DEEP_THINK_LLM=deepseek-v4-pro
TRADINGAGENTS_QUICK_THINK_LLM=deepseek-v4-flash
TRADINGAGENTS_LLM_BACKEND_URL=https://api.deepseek.com
TRADINGAGENTS_RESULTS_DIR=./data/tradingagents/logs
TRADINGAGENTS_CACHE_DIR=./data/tradingagents/cache
TRADINGAGENTS_MEMORY_LOG_PATH=./data/tradingagents/memory/trading_memory.md
```

这 3 个路径变量已经在部署模板中默认配置好，因此本地运行产生的日志、缓存、检查点和记忆文件都会落在部署目录下，而不是写到用户主目录。

另外，部署目录下的本地启动脚本会自动准备一份 ASCII 路径的 CA 证书文件，专门规避 Windows 中文路径环境下 yfinance / curl_cffi 的 SSL 证书定位错误。

### 5.2 可用的 LLM Provider 变量

官方示例支持以下常见变量：

```env
OPENAI_API_KEY=
GOOGLE_API_KEY=
ANTHROPIC_API_KEY=
XAI_API_KEY=
DEEPSEEK_API_KEY=
DASHSCOPE_API_KEY=
DASHSCOPE_CN_API_KEY=
ZHIPU_API_KEY=
ZHIPU_CN_API_KEY=
MINIMAX_API_KEY=
MINIMAX_CN_API_KEY=
OPENROUTER_API_KEY=
```

### 5.3 金融数据相关变量

如果你希望额外启用 Alpha Vantage，可配置：

```env
ALPHA_VANTAGE_API_KEY=
```

如果未配置，系统仍可使用 yfinance 作为默认数据源之一。

如果你所在网络对 Yahoo Finance 触发了限流，可以在 部署/.env 里直接把股票价格数据优先切到 Alpha Vantage：

```env
ALPHA_VANTAGE_API_KEY=你的密钥
TRADINGAGENTS_CORE_STOCK_VENDOR=alpha_vantage,yfinance
TRADINGAGENTS_GET_STOCK_DATA_VENDOR=alpha_vantage,yfinance
```

当前代码在 yfinance 返回限流错误时，也会自动继续尝试你配置的下一个 vendor，而不是直接让整条分析链路失败。

### 5.4 企业模型与本地模型

- 企业环境：可复制 .env.enterprise.example 到 .env.enterprise，再填写 Azure OpenAI 或其他企业提供商信息
- Ollama：默认地址是 http://localhost:11434/v1，也可以通过 OLLAMA_BASE_URL 指向远程 ollama-serve

例如：

```env
OLLAMA_BASE_URL=http://your-ollama-host:11434/v1
```

---

## 6. 配置覆盖机制

TradingAgents 支持用 TRADINGAGENTS_ 前缀环境变量覆盖默认配置，因此很多行为不需要改代码。

当前仓库已暴露的常见覆盖项包括：

```env
TRADINGAGENTS_LLM_PROVIDER=
TRADINGAGENTS_DEEP_THINK_LLM=
TRADINGAGENTS_QUICK_THINK_LLM=
TRADINGAGENTS_LLM_BACKEND_URL=
TRADINGAGENTS_OUTPUT_LANGUAGE=
TRADINGAGENTS_MAX_DEBATE_ROUNDS=
TRADINGAGENTS_MAX_RISK_ROUNDS=
TRADINGAGENTS_CHECKPOINT_ENABLED=
TRADINGAGENTS_BENCHMARK_TICKER=
```

此外，还有几个直接影响部署落地的重要路径变量：

```env
TRADINGAGENTS_RESULTS_DIR=
TRADINGAGENTS_CACHE_DIR=
TRADINGAGENTS_MEMORY_LOG_PATH=
```

这意味着你可以在不修改源码的情况下控制：

1. 使用哪家模型供应商。
2. 用哪个深度推理模型和快速模型。
3. 输出语言是什么。
4. 辩论轮数是多少。
5. 是否默认启用检查点恢复。
6. 日志、缓存、记忆文件写到哪里。

---

## 7. 首次启动方式

### 7.1 交互式 CLI 启动

官方推荐入口：

```bash
tradingagents
```

如果你是从源码目录直接运行，也可以：

```bash
python -m cli.main
```

CLI 启动后，通常会让你选择：

1. ticker
2. 分析日期
3. LLM provider
4. 模型名称
5. 研究深度
6. 参与的 analyst 类型

### 7.2 显式使用 analyze 子命令

仓库当前还提供 analyze 子命令，适合更明确地控制检查点行为：

```bash
tradingagents analyze --checkpoint
```

如果要在运行前清空历史检查点：

```bash
tradingagents analyze --clear-checkpoints
```

这两个参数很适合长流程分析任务。

---

## 8. Docker 部署

如果你希望隔离本地环境，官方仓库已经提供 Dockerfile 和 docker-compose.yml。

### 8.1 Docker 部署前提

- 已安装 Docker
- 已安装 Docker Compose
- 已准备 .env 文件

### 8.2 启动默认容器

本工作区推荐直接在部署目录执行，compose 会自动以 ../源代码 作为构建上下文。

Linux 或 macOS：

```bash
cd 部署
cp .env.example .env
docker compose run --rm tradingagents
```

Windows PowerShell：

```powershell
Set-Location .\部署
Copy-Item .env.example .env
docker compose run --rm tradingagents
```

### 8.3 Docker 当前行为说明

根据仓库里的 compose 配置，默认服务包含这些特点：

1. 通过 .env 注入环境变量。
2. 将容器内 /home/appuser/.tradingagents 绑定到部署目录下的 data/tradingagents。
3. 以交互模式运行，适合 CLI 界面。
4. 容器入口命令直接是 tradingagents。

这样部署的直接好处是运行产物都留在部署目录附近，便于查看日志、缓存和检查点。

因此，执行 docker compose run --rm tradingagents 后，本质上是在容器里启动 CLI。

### 8.4 Dockerfile 当前行为说明

当前 Dockerfile 主要做了这些事：

1. 在构建阶段安装项目依赖。
2. 运行阶段复制虚拟环境。
3. 创建 appuser 用户。
4. 预创建 /home/appuser/.tradingagents 目录。
5. 以非 root 用户运行 tradingagents。

这套设计的直接好处是：

- 缓存和记忆目录权限更稳定。
- 容器默认更安全。
- 交互式 CLI 的运行体验更接近本地安装。

---

## 9. Ollama 部署

如果你不想依赖云端模型，可以使用 Ollama。

### 9.1 Docker Compose 方式

仓库已经提供 ollama profile：

```bash
cd 部署
docker compose --profile ollama run --rm tradingagents-ollama
```

### 9.2 关键注意点

当前 compose 中：

1. ollama 服务使用官方镜像 ollama/ollama:latest。
2. tradingagents-ollama 服务会设置 TRADINGAGENTS_LLM_PROVIDER=ollama。
3. 仍然会把 TradingAgents 的持久化目录挂载到部署目录下。

### 9.3 模型准备

如果是本机或远端 Ollama，需要先拉取模型：

```bash
ollama pull your-model-name
```

如果 CLI 默认列表中没有你要的模型，可以选择自定义模型 ID。

---

## 10. 持久化目录与运行产物

TradingAgents 默认会在用户主目录下维护自己的运行数据。

默认根目录：

```text
~/.tradingagents
```

如果你使用本工作区在部署目录下提供的 docker-compose.yml，则宿主机上的对应目录为：

```text
部署/data/tradingagents
```

其中最重要的几类内容是：

### 10.1 日志目录

- 默认结果目录：~/.tradingagents/logs
- 可通过 TRADINGAGENTS_RESULTS_DIR 覆盖

### 10.2 缓存与检查点

- 默认缓存目录：~/.tradingagents/cache
- 检查点数据库位于：~/.tradingagents/cache/checkpoints/<TICKER>.db
- 可通过 TRADINGAGENTS_CACHE_DIR 覆盖

### 10.3 决策记忆

- 默认记忆文件：~/.tradingagents/memory/trading_memory.md
- 可通过 TRADINGAGENTS_MEMORY_LOG_PATH 覆盖

这三个目录是否能正常写入，基本决定了部署是否稳定。

---

## 11. 首次部署建议的最小验证流程

建议不要一上来就追求复杂配置，先按最小闭环验证。

### 11.1 验证步骤

1. 激活虚拟环境。
2. 执行 pip install .。
3. 配置一组可用 API Key。
4. 执行 tradingagents --help。
5. 执行 tradingagents 或 python -m cli.main。
6. 在 CLI 中选择一个通用 ticker，例如 NVDA、AAPL、TSLA 或 BTC-USD。
7. 观察是否正常进入分析流程。
8. 分析完成后检查 ~/.tradingagents 下是否生成日志、缓存或记忆文件。

如果你走的是部署目录里的 Docker 入口，则第 8 步改为检查 部署/data/tradingagents。

### 11.2 成功判定标准

满足下面任意 3 项，通常就说明部署成功：

1. CLI 能正常启动。
2. 模型请求没有因为缺少 API Key 而报错。
3. 能产出 analyst / researcher / portfolio manager 的过程输出。
4. 任务结束后写入了日志或记忆文件。
5. 启用 --checkpoint 后能生成检查点数据库。

---

## 12. 常见部署问题

### 12.1 tradingagents 命令不存在

通常原因：

1. 没有在正确的虚拟环境中安装。
2. pip install . 没有成功完成。
3. 当前 shell 没有加载虚拟环境路径。

处理方式：

```bash
python -m cli.main --help
```

如果这个命令能运行，说明项目本身大概率已经安装好，只是脚本入口未进入 PATH。

### 12.2 API Key 已填写但仍然报认证错误

常见原因：

1. .env 没有被当前运行方式加载。
2. 选用的 provider 与实际填写的 API Key 不匹配。
3. 使用了 Docker，但 .env 文件不在 compose 识别的位置。
4. 同时配置了多个 provider，但 CLI 选择了另一个未配置的 provider。

### 12.3 Windows 下复制命令不兼容

官方 README 多数示例使用：

```bash
cp .env.example .env
```

在 Windows PowerShell 中应改为：

```powershell
Copy-Item .env.example .env
```

### 12.4 检查点或记忆日志无法写入

优先排查：

1. 目标目录权限。
2. Docker 挂载卷权限。
3. 自定义的 TRADINGAGENTS_CACHE_DIR 或 TRADINGAGENTS_MEMORY_LOG_PATH 是否可写。

### 12.5 Ollama 模型无法连接

优先排查：

1. Ollama 服务是否已启动。
2. OLLAMA_BASE_URL 是否配置正确。
3. 模型是否已执行 ollama pull。
4. 远程主机的端口是否可访问。

---

## 13. 推荐的部署顺序

如果你是第一次接触 TradingAgents，建议按这个顺序推进：

1. 本地 Python 环境跑通 CLI。
2. 只配置一个最熟悉的 LLM provider。
3. 完成一次最小分析闭环。
4. 再启用 checkpoint。
5. 再切 Docker。
6. 最后才考虑接 Ollama、企业模型或自定义后端地址。

这个顺序的好处是每一步的故障面都很小，容易定位问题。

---

## 14. 通用部署结论

从当前公开仓库来看，TradingAgents 的通用部署难点并不在“怎么启动程序”，而在下面三件事是否一次性理顺：

1. 你选择哪一家模型供应商。
2. 你是否把环境变量放在了当前运行方式能读取到的位置。
3. 你是否确认了日志、缓存、检查点和记忆目录是可写的。

只要这三件事处理清楚，本地 Python 部署和 Docker 部署都不复杂。

对大多数用户，最稳妥的起点仍然是：

```bash
cd 部署
cp .env.example .env
docker compose run --rm tradingagents
```

先跑通研究型 CLI，再逐步增加模型、数据和持久化配置。本部署方式不绑定任何 A 股数据源或 A 股交易约束，适合作为通用市场研究环境。
