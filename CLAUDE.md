# Model Pricing Observatory

## Project Overview
AI模型价格观测站 — 自动采集全球主流大模型官方/渠道/套餐价格，展示历史趋势和横向对比。

## Tech Stack
- Frontend: Next.js 14 + TypeScript + Tailwind + Shadcn UI + ECharts + Framer Motion
- Frontend Testing: Vitest + React Testing Library + MSW
- Backend: FastAPI + SQLAlchemy 2 async + PostgreSQL 16
- Backend Testing: pytest + pytest-asyncio + httpx (AsyncClient) + factory_boy
- Crawler: httpx (API类) + Playwright (JS渲染类) + BeautifulSoup
- Cache: Redis 7
- Task Queue: Celery + Redis (broker) + Celery Beat
- Deploy: Docker Compose

## Project Structure
```
model-pricing-observatory/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── api/
│   │   ├── crawlers/
│   │   ├── tasks/
│   │   ├── cache.py
│   │   ├── alerts.py
│   │   └── schemas/
│   ├── tests/
│   ├── alembic/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/app/
│   ├── src/components/
│   ├── src/lib/
│   ├── tests/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Deployment
- Domain: price.ihope.cc
- Architecture: 服务器Nginx → localhost:8194 → frontend容器(内置nginx反代 /api → backend:3722)
- 唯一对外端口: APP_PORT=8194
- postgres/redis/playwright仅Docker内部网络，不映射host端口
- 参考finance项目docker-compose模式：frontend做入口，expose backend内部

## Commands
- Backend test: `cd backend && pytest --tb=short -q`
- Frontend test: `cd frontend && npx vitest run`
- Start all: `docker compose up --build`
- Backend dev: `cd backend && uvicorn app.main:app --reload --port 3722`
- Frontend dev: `cd frontend && npm run dev`
- Migration: `cd backend && alembic upgrade head`

## Conventions
- API response format: `{"items": [...], "total": N, "page": N, "page_size": N}` for lists
- Price unit: per million tokens (input/output separately)
- Currency: store original + CNY converted
- Price snapshots are immutable — never update, only insert new date
- Admin auth: `X-Admin-Key` header
- All crawlers must record crawl_job with status

## Development Rules
- 每完成一个Step，运行全部已有测试确保无回归
- 爬虫全自动，禁止人工录入数据
- 价格按日快照存储，永不覆盖历史
- 测试必须mock外部API调用，不依赖真实网络

## Git
- Commit author: heyu.nwpu@gmail.com
- Push to: main branch
- No Co-Authored-By lines
