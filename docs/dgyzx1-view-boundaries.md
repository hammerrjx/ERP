# dgyzx1 视图边界（DEMO）

本文件只记录当前 DEMO 阶段实际需要遵守的源库边界，不把全部视图复制成第二套业务模型。源 SQL Server 使用 `.env` 中的只读连接；本地 ERP 数据仍写入 Django 配置的 SQLite/PostgreSQL。

## 已核对的源视图

| 业务用途 | 源对象 | DEMO 用法 | 不能替代的字段/逻辑 |
| --- | --- | --- | --- |
| 物料编码与基础描述 | `coerp_base.dbo.V_AI_PT_MSTR` | 读取编码流水号和物料基础字段 | 不包含库位、供应商、业务单位换算；导入继续使用 Excel 模板 |
| 客户物料编码 | `dbo.v_cp_part`、`dbo.v_cp_part_all` | 只读对照参考 | 完整唯一键仍按 `cp_mstr(cp_cust, cp_part, cp_cust_part)` 保留 |
| 采购价格核验 | `dbo.v_pc_mstr_price`、`dbo.v_pc_all_price` | 校验供应商、物料、币别、日期、税率和价格 | 报价单号、工作流和阶梯明细继续来自 `pc_mstr/pcd_det` |
| 收货单头/明细 | `dbo.v_prh_receiver`、`dbo.v_prh_hist` | 保留来源对象标识和字段对应 | 不能把单头和明细视图混用 |
| 库存交易历史 | `dbo.v_tr_hist` | 后续只读历史查询 | `site + location + batch` 关系不能丢失 |
| 供应商协同资料 | `dbo.v_vend_SCM` | 后续供应商资料补充 | 先建立字段映射，再决定是否替换现有基础表导入 |

## 不变量

- 源库只读，任何导入或单据操作都写本地 ERP 数据库。
- `coerp_dgyzx1` 是业务源库；物料视图目录位于 `coerp_base`。
- 不修改历史迁移、表名、API 路径、客户物料三字段唯一约束和现有 `source_object` 标识。
- 新模块接入视图前，先补充本表中的业务用途、字段缺口和回归测试。

74 个文档视图已与实际 `coerp_dgyzx1` 的 `dbo` 视图名称和字段数量核对一致；其余视图按模块推进时再逐项接入。
