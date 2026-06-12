# Model Pricing Observatory

AI模型价格观测站 — 自动采集全球主流大模型价格，展示历史趋势和横向对比。

## Quick Start

```bash
docker compose up --build
```

- Production: https://price.ihope.cc
- Local (compose): http://localhost:8194
- API Docs: http://localhost:8194/api/docs

## Development

```bash
# Backend
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm install && npm run dev

# Tests
cd backend && pytest --tb=short -q
cd frontend && npx vitest run
```

## Documentation

- [PRD](docs/PRD.md) — 完整产品需求文档
