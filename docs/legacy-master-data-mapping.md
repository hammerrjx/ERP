# 原 ERP 基础资料映射

映射依据为七份 Excel 导出、`source-schema-catalog.md` 和数据库 GraphML。GraphML 中已定位 `pt_mstr`、`pl_mstr`、`um_mstr`、`loc_mstr`、`ex_mstr`、`cm_mstr`、`vd_mstr`、`cp_mstr` 与 `vp_mstr` 节点。

| 业务资料 | Excel 程序 | 原 ERP 对象 | 当前 Django 模型 | 关键关联 |
| --- | --- | --- | --- | --- |
| 货币 | AMCUMTA1 | `ex_mstr` | `Currency` | 客户、供应商通过币种代码关联 |
| 库位 | AMLOMTA1 | `loc_mstr` | `Location` | 物料和产品类通过默认库位代码关联 |
| 产品类 | AMPLMTA1 | `pl_mstr` | `ProductCategory` | GraphML: `pt_mstr → pl_mstr` |
| 计量单位 | AMUNMTA1 | `um_mstr` | `UomCategory`、`Uom` | 物料库存单位及四类业务单位按代码/名称关联 |
| 物料信息 | AMPTMTA1 | `pt_mstr` | `Material`、`MaterialUomConversion` | 产品类、单位、库位、默认供应商均为外键 |
| 客户资料 | SLCMMTA1 | `cm_mstr` | `Partner(kind=customer)` | GraphML: `cm_mstr → ex_mstr` |
| 供应商资料 | PUVDMTA1 | `vd_mstr` | `Partner(kind=supplier)` | GraphML: `vd_mstr → ex_mstr` |
| 客户物料 | 后续导出 | `cp_mstr` | `CustomerMaterial` | GraphML: `cp_mstr → cm_mstr/pt_mstr` |
| 供应商物料 | 后续导出 | `vp_mstr` | 当前由物料默认供应商承载 | GraphML: `vp_mstr → vd_mstr/pt_mstr` |

## 导入规则

- 代码按不区分大小写去重，重复行只保留第一条合格记录。
- 排除代码或名称明确以 `TEST`、`DEMO`、`SAMPLE` 开头及明确中文测试名称的数据。
- 必填代码、名称、长度或字符格式不符合当前模型的数据不导入，并计入报告。
- 三位大写货币代码才导入；原数据中的 `RIUI` 不自动纠正为 JPY。
- 单位名称必须为中文/本地化名称；同名单位只导入第一条。
- 所有非测试产品类均导入。物料按每个产品类最多三条合格记录取样，少于三条则全部导入。
- 物料只有在产品类和计量单位可解析时才导入。源库位为空时关联不可用的系统库位 `LEGACY-UNASSIGNED`，供后续人工分配；源库位为未知非空代码时仍跳过。
- 命令使用 `update_or_create`，可重复执行，不会重复增加同编码主数据。
- 新建物料编码使用产品类代码（`ProductCategory.code_prefix`）作为前缀，并优先从只读视图 `coerp_base.dbo.V_AI_PT_MSTR` 的物料编码列（源表 `pt_part`，当前视图显示为 `物料编码`）读取该前缀最大数字流水号；源库不可达时才使用本地 `Material.code` 回退。流水号位数沿用源视图最大号（例如 `ZXX-000124` → `ZXX-000125`），不会固定截断为四位。
- 税务编码导入遍历所有工作表并按表头识别 `税务编码`、`税务名称`、`开票名称`，重复编码按文件最后一行更新；当前 `税务编码.xlsx` 有 1430 行、1428 个唯一编码（2 行重复）。

## 执行

```powershell
python backend\manage.py import_legacy_master_data `
  --source-dir "C:\Users\LENOVO\Desktop\ERP操作路线\表格" `
  --per-category 3 `
  --replace `
  --report docs\legacy-import-report.md
```

`--replace` 会清空当前项目中的基础资料和依赖报价后重建，适合首次或纠正规则后的完整导入；日常重复同步不加该参数。
