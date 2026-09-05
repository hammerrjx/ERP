# 前端架构约定

## 范围和稳定边界

- 保留 React、Vite、Django REST Framework 和现有 CSS；不引入路由库或组件库。
- 不修改 `backend/models.py`、迁移、数据库结构、API 路径、请求体或审批状态机。
- 前端只负责页面可见性和交互提示；权限与数据约束以 Django API 为准。
- 源 ERP SQL Server 仅作只读参考。已核实物料视图为 `coerp_base.dbo.V_AI_PT_MSTR`，本次只读取了视图元数据。

## 目录职责

| 目录 | 职责 |
| --- | --- |
| `src/app` | 应用壳、侧栏、当前页面状态和页面级编排。 |
| `src/api` | 统一 HTTP 请求、鉴权请求头和错误转换。 |
| `src/auth` | 会话保存、登出、前端权限判断和登录页。 |
| `src/components` | 跨业务模块复用的展示与表单组件。 |
| `src/modules` | 按业务域放置资源配置、页面或业务展示组件。 |
| `src/shared` | 无业务副作用的展示常量、状态文本与格式化。 |

模块域使用 `system`、`master-data`、`engineering`、`sales`、`purchase`、`inventory`、`finance`。资源字段配置位于各域的 `configs.js`，由 `src/app/configs.js` 聚合；侧栏菜单位于 `src/app/navigation.js`。本次不改变现有菜单或配置归属。

## API 和权限

- API 相对路径保持 `/api/<resource>/`；写操作继续由现有 `POST`、`PATCH`、`DELETE` 和单据动作端点完成。
- 前端请求必须经 `src/api/client.js`，令牌格式保持 `Authorization: Token <token>`。
- 权限码保持 `<resource>.<action>`，例如 `material.view`、`purchase_order.create`；`*` 继续表示超级管理员权限。
- 菜单、按钮隐藏和页面加载均使用同一个 `can(session, permission, action)` 判断，但不能替代后端 `ErpRolePermission`。

## 页面与依赖规则

- `app` 只编排页面和状态，不直接定义 HTTP 请求细节或会话存储实现。
- 业务模块不得直接导入其他模块的内部实现；跨模块数据通过 API、配置或 `shared` 工具传递。
- `components` 不依赖特定业务资源；业务字段与单据规则留在模块配置或 Django 服务端。
- 当前使用 `active` 状态切换页面。需要地址栏深链接、刷新保留页面或浏览器前进后退时，再评估引入 `react-router-dom`。

## 界面稳定契约

- 组件拆分只允许移动现有 JSX 和辅助逻辑；不得借机调整 CSS、视觉密度、颜色、间距或响应式断点。
- 保持现有 `className`、关键 DOM 层级、菜单与字段顺序、按钮文案、页签名称和条件渲染规则。
- 列表、详情、表单与弹窗组件继续接收原事件参数；组件内不得改变 API 路径、权限判断或审批动作。
- 每次界面组件化必须通过生产构建，并检查工作台、部门、物料列表和物料新增弹窗的 DOM 与控制台状态。

## API 访问层约定

- 资源列表和 CRUD 操作优先使用 `src/api/client.js` 的 `resourceApi`，页面不得自行拼接资源 URL。
- 单据动作统一使用 `resourceApi(...).action(id, action, body)`；动作名称和请求体仍以现有 Django API 为准。
- HTTP 失败统一抛出 `ApiError`，调用方只展示原有错误文案，不在组件中重复解析响应格式。
