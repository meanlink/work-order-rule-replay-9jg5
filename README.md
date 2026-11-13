# 工单决策树解译

星冢设备（售后维修中心）的数据分析工作台。维修中心希望根据设备年龄、运行时长、告警次数和上次保养判断工单是否可能超时。

## 真实场景

- 当前工作流：调度主管凭经验给工单打优先级，班长再手工调整。
- 痛点：优先级规则停留在个人经验；规则太多时无法比较；新人难以理解模型输出。
- 上游：业务导出、实验室复核或历史归档数据。
- 本系统：统一资产登记、分析编排、Python 计算、结果复核与审计。
- 下游：业务负责人、数据管理员与复核员在周会/评审中使用结果。

## 功能

- 规则总览：核心指标、数据状态与近期运行。
- 设备资产：资产列表、样本量与校验摘要。
- 训练编排：从资产创建分析方案并触发运行。
- 树规则解释：查看真实 Python 计算结果、方法、限制与表格。
- 治理审计：审计日志、复核意见与角色权限追踪。

## 快速启动

```bash
cp .env.example .env
docker compose up -d --build
docker compose exec backend python -m scripts.seed_demo
```

访问：

- 前端：http://localhost:18221
- 后端接口：http://localhost:19221/api/health
- 数据库映射：localhost:17721

## 演示账号

| 角色 | 邮箱 | 密码 | 权限 |
|---|---|---|---|
| 数据管理员 | admin@batchdemo.dev | Demo123! | 全部页面、创建与运行 |
| 分析员 | analyst@batchdemo.dev | Demo123! | 创建资产、方案与运行 |
| 业务复核员 | reviewer@batchdemo.dev | Demo123! | 只读结果、提交复核意见 |

## 技术栈

| 服务 | 技术 |
|---|---|
| frontend | vue + TypeScript + Vite + Nginx |
| backend | Python 3.11 + FastAPI + SQLAlchemy |
| worker | Celery + Redis |
| db | mysql |
| redis | Redis 7 |

## 枚举位置

- 后端：`backend/src/constants/enums.py`
- 后端业务标签：`backend/src/constants/domain.py`
- 前端：`frontend/src/constants/enums.ts`
- 前端业务标签：`frontend/src/constants/domain.ts`

## 目录

```text
frontend/       # 页面、组件、store、API
backend/        # routes/controllers/services/models/schemas/middlewares
test-artifacts/ # 由批次 QA 放在项目目录之外
```

## 环境变量

见 `.env.example`。`.env` 不提交。接口统一由 Nginx `/api/` 代理。

## 算法口径

CART 决策树训练：后端按输入样本真实计算并返回效应、区间或评分。

条件路径规则抽取：作为第二层诊断；结果、方法和限制同时返回，前端不硬编码图形数据。

## License

MIT
