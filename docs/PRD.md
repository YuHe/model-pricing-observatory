# Model Pricing Observatory — 完整可执行PRD V3.0

## 总体范围

| 包含 | 不包含 |
|---|---|
| 所有海外+国内厂商爬虫 | 用户注册/登录/收藏/订阅 |
| 所有渠道价格 | 用户相关功能 |
| 套餐价格 | |
| Redis缓存 | |
| Celery任务队列 | |
| 告警通知（邮件+Webhook） | |
| SEO完整实现 | |
| 全栈单测100%功能覆盖 | |
| Admin认证（简单API Key） | |

---

## 技术栈

| 层 | 选型 |
|---|---|
| Frontend | Next.js 14 + TypeScript + Tailwind + Shadcn UI + ECharts + Framer Motion |
| Frontend Testing | Vitest + React Testing Library + MSW |
| Backend | FastAPI + SQLAlchemy 2 async + PostgreSQL 16 |
| Backend Testing | pytest + pytest-asyncio + httpx (AsyncClient) + factory_boy |
| 爬虫 | httpx (API类) + Playwright (JS渲染类) + BeautifulSoup |
| 缓存 | Redis 7 |
| 任务队列 | Celery + Redis (broker) + Celery Beat |
| 告警 | Email (SMTP) + Webhook (HTTP POST) |
| 部署 | Docker Compose (7 containers) |

---

## 产品原则

1. **全自动采集** — 所有数据来源于自动采集，禁止人工录入，禁止后台修改价格
2. **历史不可变** — 所有价格按日快照存储，永不覆盖历史记录
3. **统一计价** — 所有价格统一换算成 人民币/百万Token，同时保留原币种价格
4. **故障自愈** — 爬虫失败必须告警，通过修复代码解决，不允许人工补数据

---

## 数据覆盖范围

### 海外模型厂商
OpenAI, Anthropic, Google Gemini, xAI, Meta, Mistral, Cohere

### 国内模型厂商
DeepSeek, Qwen, GLM, Doubao, Seed, MiniMax, ERNIE, Hunyuan, Kimi, Xiaomi MiMo

### API渠道
OpenRouter, SiliconFlow, Together, Fireworks, Groq, 百炼, 火山方舟, 腾讯云, 华为云

### 套餐产品
Claude Pro/Max, Cursor, GitHub Copilot, Windsurf, Augment, Devin

---

## 数据模型

```sql
-- provider: 厂商和渠道统一表
CREATE TABLE provider (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    type VARCHAR(20) NOT NULL,            -- "official" | "channel"
    country VARCHAR(10),                  -- "US" | "CN" | "EU"
    official_url TEXT,
    logo_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- model
CREATE TABLE model (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id UUID NOT NULL REFERENCES provider(id),
    name VARCHAR(200) NOT NULL,
    family VARCHAR(100),
    release_date DATE,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(provider_id, name)
);

-- model_capability
CREATE TABLE model_capability (
    model_id UUID PRIMARY KEY REFERENCES model(id),
    context_window INT,
    max_output_tokens INT,
    vision BOOLEAN DEFAULT FALSE,
    reasoning BOOLEAN DEFAULT FALSE,
    tool_calling BOOLEAN DEFAULT FALSE,
    structured_output BOOLEAN DEFAULT FALSE,
    json_mode BOOLEAN DEFAULT FALSE,
    batch_api BOOLEAN DEFAULT FALSE,
    fine_tuning BOOLEAN DEFAULT FALSE,
    prompt_caching BOOLEAN DEFAULT FALSE
);

-- model_alias: 名称映射
CREATE TABLE model_alias (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_id UUID NOT NULL REFERENCES model(id),
    alias_name VARCHAR(300) NOT NULL,
    source VARCHAR(100) NOT NULL,
    UNIQUE(alias_name, source)
);

-- price_snapshot: 每日不可变快照
CREATE TABLE price_snapshot (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    model_id UUID NOT NULL REFERENCES model(id),
    channel_id UUID NOT NULL REFERENCES provider(id),
    currency VARCHAR(10) NOT NULL,
    input_price_per_m DECIMAL(12,6),
    output_price_per_m DECIMAL(12,6),
    input_price_cny DECIMAL(12,6),
    output_price_cny DECIMAL(12,6),
    exchange_rate DECIMAL(10,4),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(date, model_id, channel_id)
);

-- subscription_plan
CREATE TABLE subscription_plan (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider VARCHAR(100) NOT NULL,
    plan_name VARCHAR(200) NOT NULL,
    monthly_price DECIMAL(10,2),
    annual_price DECIMAL(10,2),
    currency VARCHAR(10) NOT NULL,
    monthly_price_cny DECIMAL(10,2),
    features JSONB,
    source_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(provider, plan_name)
);

-- subscription_snapshot: 套餐历史
CREATE TABLE subscription_snapshot (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    plan_id UUID NOT NULL REFERENCES subscription_plan(id),
    monthly_price DECIMAL(10,2),
    monthly_price_cny DECIMAL(10,2),
    exchange_rate DECIMAL(10,4),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(date, plan_id)
);

-- exchange_rate
CREATE TABLE exchange_rate (
    date DATE PRIMARY KEY,
    usd_cny DECIMAL(10,4) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- crawl_job
CREATE TABLE crawl_job (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,          -- "pending"|"running"|"success"|"failed"
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    models_synced INT DEFAULT 0,
    error_message TEXT,
    stack_trace TEXT,
    retry_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- alert_config
CREATE TABLE alert_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(20) NOT NULL,            -- "email" | "webhook"
    endpoint TEXT NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- alert_log
CREATE TABLE alert_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_config_id UUID REFERENCES alert_config(id),
    job_id UUID REFERENCES crawl_job(id),
    sent_at TIMESTAMPTZ DEFAULT NOW(),
    status VARCHAR(20),                   -- "sent" | "failed"
    error_message TEXT
);
```

---

## 爬虫规格

### API类爬虫（httpx，无需浏览器）

| 源 | URL | 认证 | 提取逻辑 |
|---|---|---|---|
| OpenRouter | `GET https://openrouter.ai/api/v1/models` | 无 | `data[].id`, `pricing.prompt*1e6`, `pricing.completion*1e6`, `context_length` |
| SiliconFlow | `GET https://api.siliconflow.cn/v1/models` | 无 | 类OpenAI格式 |
| Together | `GET https://api.together.xyz/v1/models` | API Key (free tier) | `pricing.input`, `pricing.output` |
| Groq | `GET https://api.groq.com/openai/v1/models` + 定价页 | 无 | 模型列表+定价解析 |
| 汇率 | `GET https://api.exchangerate-api.com/v4/latest/USD` | 无 | `rates.CNY` |

### Playwright类爬虫（JS渲染）

| 源 | URL | wait_selector |
|---|---|---|
| OpenAI | `https://openai.com/api/pricing/` | 价格表格容器 |
| Anthropic | `https://docs.anthropic.com/en/docs/about-claude/models` | 模型表格 |
| Google Gemini | `https://ai.google.dev/pricing` | pricing cards |
| xAI | `https://docs.x.ai/docs/models#models-and-pricing` | 定价表格 |
| Mistral | `https://docs.mistral.ai/getting-started/models/models_overview/` | 模型表格 |
| Cohere | `https://cohere.com/pricing` | 定价卡片 |
| DeepSeek | `https://api-docs.deepseek.com/zh-cn/quick_start/pricing` | 表格 |
| Qwen (通义/百炼) | `https://help.aliyun.com/zh/model-studio/getting-started/models` | 表格 |
| GLM (智谱) | `https://open.bigmodel.cn/pricing` | 价格卡片 |
| Doubao (豆包/火山方舟) | `https://www.volcengine.com/docs/82379/1099320` | 文档表格 |
| MiniMax | `https://platform.minimaxi.com/document/Price` | 表格 |
| Kimi (月之暗面) | `https://platform.moonshot.cn/docs/intro#计费` | 内容区 |
| Hunyuan (混元) | `https://cloud.tencent.com/document/product/1729/97731` | 文档表格 |
| ERNIE (文心) | `https://cloud.baidu.com/doc/WENXINWORKSHOP/s/hlrk4akp7` | 文档表格 |

### Playwright爬虫统一模式

```python
async def crawl_with_playwright(url: str, wait_selector: str, extract_fn):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_selector(wait_selector, timeout=30000)
        html = await page.content()
        await browser.close()
    return extract_fn(html)
```

### 套餐爬虫

| 套餐 | URL |
|---|---|
| Claude Pro/Max | `https://claude.ai/pricing` |
| Cursor | `https://www.cursor.com/pricing` |
| GitHub Copilot | `https://github.com/features/copilot#pricing` |
| Windsurf | `https://windsurf.com/pricing` |
| Augment | `https://www.augmentcode.com/pricing` |
| Devin | `https://devin.ai/pricing` |

---

## API Schema

### 公开API

| 端点 | 参数 | 返回 |
|---|---|---|
| `GET /api/v1/stats` | 无 | `{provider_count, model_count, channel_count, today_updated, price_drops: [{model,percent}], price_increases: [{model,percent}]}` |
| `GET /api/v1/models` | provider, family, channel, vision, reasoning, tool_calling, structured_output, batch_api, fine_tuning, prompt_caching, min_context, max_context, min_price, max_price, sort_by, sort_order, page, page_size, search | 分页模型列表+最新价格+涨跌幅 |
| `GET /api/v1/models/{id}` | 无 | 完整模型信息+能力+最新价格+渠道价格对比+最近30天历史 |
| `GET /api/v1/models/{id}/history` | days(default 90) | `[{date, input_price_cny, output_price_cny, channel}]` |
| `GET /api/v1/compare` | ids=uuid1,uuid2,...(max 10) | 模型数组含全字段+能力+价格 |
| `GET /api/v1/providers` | type(official/channel) | `[{id, name, type, country, model_count, min_price_cny, avg_price_cny}]` |
| `GET /api/v1/providers/{id}` | 无 | 厂商详情+全部模型 |
| `GET /api/v1/channels` | 无 | 渠道列表+模型数+价格统计 |
| `GET /api/v1/channels/{id}/prices` | 无 | 该渠道全部模型价格 |
| `GET /api/v1/plans` | 无 | 全部套餐最新价格 |
| `GET /api/v1/plans/{id}` | 无 | 套餐详情+历史价格 |
| `GET /api/v1/plans/{id}/history` | days(default 90) | 套餐历史价格 |
| `GET /api/v1/price-changes` | direction(up/down), limit(default 20) | 价格变化排行 |

### Admin API（需Header: `X-Admin-Key: <key>`）

| 端点 | 说明 |
|---|---|
| `GET /api/v1/admin/jobs` | 全部爬虫任务列表 |
| `GET /api/v1/admin/jobs/{id}` | 任务详情含stack_trace |
| `POST /api/v1/admin/jobs/{source}/retry` | 重试指定源爬虫 |
| `GET /api/v1/admin/alerts` | 告警配置列表 |
| `POST /api/v1/admin/alerts` | 新增告警配置 |
| `PUT /api/v1/admin/alerts/{id}` | 修改告警配置 |
| `DELETE /api/v1/admin/alerts/{id}` | 删除告警配置 |
| `GET /api/v1/admin/alert-logs` | 告警发送记录 |

---

## 前端页面规格

### / (Home)
- 统计卡片：Provider数、Model数、Channel数、今日更新数
- 降价榜 Top 5（绿色 ▼）
- 涨价榜 Top 5（红色 ▲）
- 最近更新的10个模型
- 最近同步状态指示灯

### /models
- 左侧筛选面板：Provider多选、Family多选、能力Toggle×8、价格Range滑块、Context Range
- 搜索框（模型名模糊搜索）
- 列表/卡片模式切换
- 排序：input_price_cny / output_price_cny / context_window / price_change / updated_at × asc/desc
- 分页
- 每行：模型名、Provider、input/output CNY、涨跌幅标签、能力图标

### /models/[id]
- 模型基础信息卡片
- 能力标签组
- 渠道价格对比表
- ECharts 90天价格折线图（双线：input/output）

### /compare
- 顶部模型搜索添加（最多10个）
- 横向对比表：价格+能力+context全字段
- 最低价格高亮

### /providers
- 卡片网格：厂商名、国家、模型数、最低价格
- 点击进入详情

### /providers/[id]
- 厂商信息 + 全部模型列表

### /channels
- 渠道卡片网格 + 同模型跨渠道价差展示

### /channels/[id]
- 渠道全部模型价格表

### /plans
- 套餐卡片：产品名、价格、特点、历史价格小图

### /plans/[id]
- 套餐详情 + ECharts历史价格折线图

### /admin
- Admin Key认证
- 任务列表+状态+重试按钮
- 告警配置管理 + 告警日志
- **手动触发爬取按钮**：点击后立即触发一次全量爬取任务
- **爬取进度实时展示**：触发后轮询显示各爬虫执行状态（pending/running/success/failed），已完成数/总数进度条
- **错误详情弹窗**：某爬虫失败时点击可弹窗查看完整报错信息和堆栈
- **按天删除数据**：选择日期，删除该天所有 price_snapshot 和 subscription_snapshot 数据
- 以上操作均需 Admin Key 认证

---

## UI风格

- 深色模式优先（参考 OpenRouter / Linear / Vercel）
- 实时交互，无刷新筛选
- 响应式设计
- Framer Motion 动画过渡

---

## 汇率系统

- 每日同步 USD → CNY
- 计算：`price_cny = price_usd × daily_exchange_rate`
- 历史价格保留当时汇率，禁止回算
- 国内厂商原始CNY的，exchange_rate = 1

---

## Redis缓存策略

| Key Pattern | TTL | 说明 |
|---|---|---|
| `stats` | 5min | 首页统计 |
| `models:list:{hash(params)}` | 5min | 模型列表 |
| `models:{id}` | 10min | 模型详情 |
| `providers:list` | 30min | 厂商列表 |
| `plans:list` | 30min | 套餐列表 |
| `price_changes` | 5min | 涨跌榜 |

爬虫完成后清除所有缓存。

---

## 告警系统

### 触发条件
- 任何 crawl_job status = "failed"
- 同一源连续失败2次升级告警

### 通知方式
- Email: SMTP发送
- Webhook: HTTP POST `{source, error, timestamp, job_id}`

---

## SEO规格

| 页面 | Meta Title模板 | URL |
|---|---|---|
| 模型详情 | `{model_name} Pricing - Model Pricing Observatory` | `/models/{slug}` |
| 厂商 | `{provider_name} Models & Pricing` | `/providers/{slug}` |
| 套餐 | `{plan_name} Pricing History` | `/plans/{slug}` |

- 自动生成 sitemap.xml / robots.txt
- OpenGraph tags
- JSON-LD (Product schema)
- 覆盖长尾词：Claude Sonnet Price, GPT Price, DeepSeek Price, Cursor Pricing 等

---

## 部署配置

### 域名
- 生产域名：`price.ihope.cc`
- 服务器 Nginx 已配好反代 → `localhost:${APP_PORT}`
- frontend 容器内 Nginx 同时反代 `/api` → backend:3722

### Docker Compose 服务

```yaml
services:
  postgres:       # expose 5432 (内部), 不映射host
  redis:          # expose 6379 (内部), 不映射host
  backend:        # expose 3722 (内部), FastAPI
  celery-worker:  # 无端口
  celery-beat:    # 无端口
  frontend:       # ports: ${APP_PORT:-8194}:80 (唯一对外端口)
  playwright:     # expose 3723 (内部)
```

### 端口策略

| 服务 | 对外映射 | 说明 |
|---|---|---|
| frontend | `${APP_PORT:-8194}:80` | 唯一对外端口，服务器nginx反代到此 |
| backend | expose 3722 | 仅Docker内部网络，frontend nginx反代 `/api` |
| postgres | expose 5432 | 仅Docker内部网络 |
| redis | expose 6379 | 仅Docker内部网络 |
| playwright | expose 3723 | 仅Docker内部网络 |

服务器Nginx配置（已有）：`price.ihope.cc` → `proxy_pass http://localhost:8194`

---

## 环境变量

```env
POSTGRES_URL=postgresql+asyncpg://pricing:pricing@postgres:5432/pricing
REDIS_URL=redis://redis:6379/0
APP_PORT=8194
ADMIN_API_KEY=<随机生成>
DOMAIN=price.ihope.cc
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASS=
ALERT_WEBHOOK_URL=
TOGETHER_API_KEY=
```

---

## 开发步骤 + 验收Checklist

### Step 1: 项目骨架
**做什么：** Docker Compose + Backend skeleton + Frontend skeleton

**验收：**
- [ ] `docker compose up --build` 全部容器启动无报错
- [ ] `curl http://localhost:8194/api/v1/health` → `{"status": "ok"}`
- [ ] `curl http://localhost:8194` → HTML
- [ ] PostgreSQL、Redis容器内部连接正常

**测试：**
- [ ] `pytest tests/test_health.py` 通过

---

### Step 2: 数据模型 + Alembic迁移
**做什么：** 全部表定义 + migration

**验收：**
- [ ] `alembic upgrade head` 无报错
- [ ] 所有表存在且字段正确
- [ ] 唯一约束生效

**测试：**
- [ ] `pytest tests/test_models.py` — ORM CRUD 通过

**回归：** Step 1 测试仍通过

---

### Step 3: 汇率爬虫
**验收：**
- [ ] 调用返回当日USD/CNY
- [ ] exchange_rate表有记录
- [ ] 重复调用同天upsert不报错

**测试：**
- [ ] `pytest tests/crawlers/test_exchange_rate.py` — mock响应+异常

**回归：** Step 1-2 通过

---

### Step 4: OpenRouter爬虫
**验收：**
- [ ] model表新增100+条
- [ ] price_snapshot有当日记录
- [ ] CNY换算正确
- [ ] crawl_job status=success

**测试：**
- [ ] `pytest tests/crawlers/test_openrouter.py` — mock+解析+去重+异常

**回归：** Step 1-3 通过

---

### Step 5: Playwright爬虫基础设施
**验收：**
- [ ] Playwright容器启动正常
- [ ] 能打开页面获取HTML

**测试：**
- [ ] `pytest tests/crawlers/test_playwright_base.py`

**回归：** Step 1-4 通过

---

### Step 6: 海外厂商爬虫 (OpenAI, Anthropic, Google, xAI, Mistral, Cohere, Meta)
**验收：**
- [ ] 每个爬虫获取≥1个模型价格
- [ ] price_snapshot正确入库
- [ ] crawl_job全部success

**测试：**
- [ ] 每厂商独立测试文件 — HTML fixtures + 正常/异常case

**回归：** Step 1-5 通过

---

### Step 7: 国内厂商爬虫 (DeepSeek, Qwen, GLM, Doubao, MiniMax, ERNIE, Hunyuan, Kimi, Xiaomi)
**验收：**
- [ ] 每个爬虫获取≥1个模型价格
- [ ] CNY处理正确（原始CNY的exchange_rate=1）
- [ ] 价格单位统一为/百万token

**测试：**
- [ ] 每厂商独立测试 — fixtures + 单位换算

**回归：** Step 1-6 通过

---

### Step 8: 渠道爬虫 (SiliconFlow, Together, Groq, 百炼, 火山方舟, 腾讯云, 华为云)
**验收：**
- [ ] 渠道模型通过alias关联到官方model
- [ ] 同一model多channel价格可查
- [ ] channel_id正确

**测试：**
- [ ] 每渠道独立测试 + alias匹配逻辑测试

**回归：** Step 1-7 通过

---

### Step 9: 套餐爬虫
**验收：**
- [ ] subscription_plan表≥6条
- [ ] subscription_snapshot有当日快照
- [ ] features为有效JSON

**测试：**
- [ ] 每套餐独立测试 + 价格变化检测

**回归：** Step 1-8 通过

---

### Step 10: Celery + Beat调度
**验收：**
- [ ] celery worker启动无报错
- [ ] beat配置每日02:00
- [ ] 任务按序执行：汇率→官方→渠道→套餐→涨跌→清缓存
- [ ] 失败自动重试(max=3)

**测试：**
- [ ] `pytest tests/test_tasks.py` — 注册+链式+重试

**回归：** Step 1-9 通过

---

### Step 11: Redis缓存层
**验收：**
- [ ] 首次请求写缓存，后续<10ms
- [ ] 爬虫完成后缓存清除
- [ ] TTL正确

**测试：**
- [ ] `pytest tests/test_cache.py` — 命中/未命中/过期/清除

**回归：** Step 1-10 通过

---

### Step 12: 告警系统
**验收：**
- [ ] 爬虫失败→触发告警
- [ ] Email/Webhook发送成功

**测试：**
- [ ] `pytest tests/test_alerts.py` — mock SMTP/HTTP + 触发条件 + 升级逻辑

**回归：** Step 1-11 通过

---

### Step 13: Backend API（全部端点）
**验收：**
- [ ] 每端点curl返回正确数据
- [ ] 筛选/排序/分页正确
- [ ] Admin需X-Admin-Key，无Key→401

**测试：**
- [ ] `pytest tests/api/test_models.py`
- [ ] `pytest tests/api/test_providers.py`
- [ ] `pytest tests/api/test_channels.py`
- [ ] `pytest tests/api/test_plans.py`
- [ ] `pytest tests/api/test_compare.py`
- [ ] `pytest tests/api/test_stats.py`
- [ ] `pytest tests/api/test_price_changes.py`
- [ ] `pytest tests/api/test_admin.py`

**回归：** Step 1-12 通过

---

### Step 14: Frontend — 首页 + 布局
**验收：**
- [ ] 统计卡片数据正确
- [ ] 涨跌榜正确展示
- [ ] 深色模式 + 响应式

**测试：**
- [ ] `vitest` — StatsCards / PriceChangeList / Home page (MSW mock)

**回归：** Step 1-13 通过

---

### Step 15: Frontend — Models列表 + 筛选
**验收：**
- [ ] 筛选实时无刷新
- [ ] 排序正确
- [ ] 列表/卡片切换
- [ ] 分页
- [ ] 涨跌颜色正确

**测试：**
- [ ] `vitest` — Models page / ModelCard / FilterPanel

**回归：** Step 1-14 通过

---

### Step 16: Frontend — Model详情 + 图表
**验收：**
- [ ] 模型信息+能力标签正确
- [ ] ECharts折线图渲染
- [ ] 渠道对比表正确

**测试：**
- [ ] `vitest` — ModelDetail / PriceChart

**回归：** Step 1-15 通过

---

### Step 17: Frontend — Compare页
**验收：**
- [ ] 搜索添加正确
- [ ] 最多10个限制
- [ ] 最低价格高亮

**测试：**
- [ ] `vitest` — Compare page

**回归：** Step 1-16 通过

---

### Step 18: Frontend — Providers + Channels
**验收：**
- [ ] 厂商列表+详情正确
- [ ] 渠道价差对比正确

**测试：**
- [ ] `vitest` — Providers / Channels

**回归：** Step 1-17 通过

---

### Step 19: Frontend — Plans
**验收：**
- [ ] 套餐卡片+历史图正确

**测试：**
- [ ] `vitest` — Plans page

**回归：** Step 1-18 通过

---

### Step 20: Frontend — Admin
**验收：**
- [ ] 需Admin Key
- [ ] 任务列表+重试
- [ ] 告警配置CRUD

**测试：**
- [ ] `vitest` — Admin page

**回归：** Step 1-19 通过

---

### Step 21: SEO
**验收：**
- [ ] 每页正确title/description/og
- [ ] `/sitemap.xml` 含全部动态路由
- [ ] `/robots.txt` 存在
- [ ] JSON-LD在源码中

**测试：**
- [ ] `vitest` — meta生成测试
- [ ] `pytest tests/test_sitemap.py`

**回归：** Step 1-20 通过

---

### Step 22: 端到端集成验收
**验收：**
- [ ] `docker compose up` 一键启动
- [ ] 手动触发爬虫→数据入库→前端正确展示
- [ ] 爬虫失败→告警发出
- [ ] Admin重试→任务重新执行
- [ ] `pytest --tb=short` 全部通过
- [ ] `npx vitest run` 全部通过
- [ ] 无跳过或pending测试

---

## 回归测试策略

每完成一个Step执行：
```bash
cd backend && pytest --tb=short -q
cd frontend && npx vitest run  # Step 14起
```

**任何测试失败必须修复后才能进入下一Step。**
