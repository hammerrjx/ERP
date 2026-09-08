# ERP

React + Vite 前端，Django REST Framework 后端。业务范围包括基础资料、工程、销售、采购、收送退货、库存和应付。

## 本地运行

需要 Python 3.11+、uv 和满足 Vite 要求的 Node.js。依赖以 `pyproject.toml / uv.lock`、`package.json / package-lock.json` 为准。

```powershell
uv sync --locked
uv run python backend/manage.py migrate
uv run python backend/manage.py createsuperuser
uv run python backend/manage.py runserver
```

另开终端：

```powershell
npm ci
npm run dev
```

前端默认地址为 http://localhost:5173，以 Vite 实际输出为准；API 默认使用 http://127.0.0.1:8000/api/。
本地默认数据库为 `backend/db.sqlite3`。运行环境配置参见 [.env.example](.env.example) 和 [settings.py](backend/erp_backend/settings.py)。
应用数据库的 `ERP_*` 配置通过进程环境变量读取；源库工具按自身实现读取本地 `.env`。不要将源库当作应用写入库。

## 项目结构

| 目录 | 职责 |
|---|---|
| `backend/domain/` | 按业务组织的模型与不变量；`backend/models.py` 是 Django 模型发现入口 |
| `backend/master_data/` | HTTP 接口、审批及序列化，历史目录名；接口已按业务模块分文件 |
| `backend/importing/` | 物料导入预览与确认 |
| `backend/management/commands/` | 可复用的导入和维护命令，参数用 `manage.py <命令> --help` 查看 |
| `backend/test_*.py`、`backend/tests.py` | 业务与接口回归测试 |
| `src/app/` | 导航、页面协调、数据加载 |
| `src/modules/` | 基础资料、销售、采购、库存、工程、财务及系统的专用界面 |
| `src/components/`、`src/shared/` | 公共控件与展示逻辑 |
| `src/api/`、`src/auth/` | 服务端访问、登录及权限展示 |
| `tools/` | 源库只读检查与浏览器验收 |
| `archive/` | 本地历史对话、计划和报告，Git 忽略 |
| `tmp/`、`outputs/` | 本地临时数据库、快照、截图及生成报告，Git 忽略 |

业务规则与模块边界只在 [架构说明](backend/architecture.md) 维护，不再为各目录重复创建说明文件。

## 验证

```powershell
uv run python backend/manage.py check
uv run python backend/manage.py makemigrations --check --dry-run
uv run python backend/manage.py test backend --noinput
npm test
npm run build
```

测试使用独立数据库；普通回归通过测试支持类隔离源库物料编号查询。
浏览器验收脚本的运行条件见 [架构说明](backend/architecture.md#浏览器验收)。
