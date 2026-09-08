# ERP

当前版本覆盖开发路径中的阶段 1 和阶段 2：组织、用户、角色、审批、主数据、BOM、工艺路线、销售、请购、询价、采购、收退货、应付凭单、库存调拨、盘点和缺料预警。所有业务写入通过 Django REST API 完成，源 SQL Server 始终只读。

## 启动前端

```powershell
npm install
npm run dev
```

在另一个终端启动后端：

```powershell
uv sync
uv run python backend\manage.py migrate
uv run python backend\manage.py createsuperuser
uv run python backend\manage.py runserver
```

然后打开 `http://localhost:5173`。新增可审核单据先保存为草稿，再从列表提交和审核；菜单、按钮和 API 同时按角色权限控制。

## 导入原 ERP 基础资料

```powershell
python backend\manage.py import_legacy_master_data --source-dir "C:\Users\LENOVO\Desktop\ERP操作路线\表格" --per-category 3
```

命令按编码去重并过滤明确的测试数据和格式错误数据，导入全部合格产品类，并为每个产品类导入最多三条合格物料。详细映射和过滤边界见 `docs/legacy-master-data-mapping.md`，本次结果见 `docs/legacy-import-report.md`。

## 同步原 ERP 用户与权限

```powershell
python backend\manage.py import_departments --source-file "C:\Users\LENOVO\Desktop\ERP操作路线\表格\1.4 -- 部门(AMDPMTA1).xls"
python backend\manage.py import_legacy_access --replace
```

权限同步从 `usr_mstr`、`grp_mstr`、`grpd_det` 和 `usrp_det` 读取非敏感字段。旧密码不会读取或导入；首次登录前必须由新 ERP 管理员设置密码。超级管理员拥有全部权限，普通用户按已审核且启用的角色执行服务端 RBAC。

## 暂定业务规则

- `FG01` 的无订单销售退货必须先进入实体不良仓 `RMA`。
- 非生产采购的 CC 定义为成本中心，并外键关联部门；非生产收货不增加库存。
- 应付凭单从已审核收货和采购退货生成，按供应商、币种、支付方式和税率自动拆分；采购退货以负金额冲减应付。
- 按发票生成应付凭单需等待发票模块启用，本阶段不创建虚构的发票来源。
- 原 ERP 工作流表当前无数据，暂按部门操作员提交、部门经理审核，后续按业务确认补充多级审批。

## 字段来源

附件中的操作指南提取了“物料信息”“供应商资料”“客户资料”及其必填项、审核、联系人、税务编码、单位、产品类、默认库位、支付方式等字段。原始附件位于用户桌面的 `ERP操作路线` 文件夹。
## 项目结构

- `backend/domain/`：基础资料、组织、工程、销售、送货、采购和库存模型；`backend/models.py`保留统一导入入口。
- `backend/master_data/serializers/`：按业务模块组织的校验与API数据表示，公共验证在`common.py`。
- `backend/master_data/*_views.py`：按模块组织的HTTP接口；`api_common.py`管理公共审批与权限行为。
- `src/modules/`：业务页面和专用弹窗；订单编辑与详情共用`sales/salesOrderFields.js`字段定义。
- `src/components/`：通用表单控件、表格及跨模块弹窗；`src/app/`只负责应用导航、加载与页面协调。
- `tools/`：检查与维护脚本；`tmp/`、`outputs/`存放本地运行结果。

历史对话生成的计划、调查和报告保存在`mymd/`、`docs/`、`backend/docs/`，由Git忽略。本地数据库、环境变量和媒体同样不提交；模块README与`backend/architecture.md`作为项目维护文档保留。

## 验证

```powershell
uv run python backend/manage.py check
uv run python backend/manage.py makemigrations --check --dry-run
uv run python backend/manage.py test backend --noinput
npm run build
```
