# Odoo 19 借鉴研究（官方一手来源）

> 目的：为本项目从“基础信息”起步设计一个可维护的 ERP，提取 Odoo Community 的领域模型、ORM、权限和交互模式。本文只引用 Odoo 官方 GitHub 仓库或 `odoo.com` 官方文档。Odoo 的具体字段和界面会随版本变化，落地前仍应锁定版本并以本项目需求为准。

## 1. Odoo 的总体技术形态

- Odoo 的服务端以 Python 编写，功能按可安装的 addon/module 组织；官方仓库的顶层 `addons/`、`odoo/`、`setup/` 和 `odoo-bin` 体现了“核心框架 + 业务模块”的结构。适合借鉴为本项目的模块边界：基础资料、库存、采购、销售、财务等模块通过明确的模型关系连接，而不是把所有字段放进一个大表。[仓库目录](https://github.com/odoo/odoo/tree/19.0)
- Odoo ORM 以 Python 类描述模型，字段定义、关系字段、约束、默认值和计算字段集中在模型层；支持 `Many2one`、`One2many`、`Many2many` 等关系，以及 `_inherit` 对现有模型扩展。这种“模型优先、视图只是呈现”的方式适合复刻基础资料中的关联字段和可扩展属性。[ORM API](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html)
- Odoo 使用 PostgreSQL 作为事务数据库，官方部署文档明确要求 PostgreSQL。对本项目，建议从关系数据库开始，使用外键、唯一约束和事务保证编码、单位、币种、库位等主数据的一致性，而不是在前端维护孤立 JSON。[安装/部署文档](https://www.odoo.com/documentation/19.0/administration/on_premise/source.html)
- Odoo 的 addon manifest、数据文件、访问控制文件和视图文件形成可安装模块。可以借鉴其“模块内自包含迁移/权限/菜单”的交付方式，但本项目不必复制 Odoo 的全部 web 客户端和模块数量。[模块开发教程](https://www.odoo.com/documentation/19.0/developer/tutorials/define_module.html)

## 2. 与本项目基础资料对应的官方领域模型

下表给出应优先抽象的实体和 Odoo 的对应概念。名称是 Odoo 模型名，字段以当前官方模块为准；本项目可以使用自己的命名，但关系方向和约束值得保留。

| 本项目资料 | Odoo 对应模型/模块 | 可借鉴的关系与行为 | 官方来源 |
|---|---|---|---|
| 产品类 | `product.category`（产品类别） | 类别树、库存计价/会计属性的继承入口；产品记录引用类别而不是重复类别文本。 | [`product.category` 源码](https://github.com/odoo/odoo/blob/19.0/addons/product/models/product_category.py) |
| 物料信息 | `product.template`（模板）+ `product.product`（变体） | 把共享属性放在模板，把可库存/销售的具体 SKU 放在变体；类别、单位、条码、税、采购/销售策略等由关系字段连接。 | [`product.template` / `product.product` 源码](https://github.com/odoo/odoo/blob/19.0/addons/product/models/product_template.py)；[产品变体文档](https://www.odoo.com/documentation/19.0/applications/sales/sales/products_prices/products/variants.html) |
| 计量单位 | `uom.uom`、`uom.category` | 单位属于单位类别；同一类别可按比例换算，交易前应阻止跨类别换算。图片中的工程/生产/采购/销售/库存单位可落为每个业务用途的 UoM 关系及换算率。 | [`uom` 模型源码](https://github.com/odoo/odoo/tree/19.0/addons/uom/models)；[单位与换算文档](https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/product_management/configure/uom.html) |
| 货币 | `res.currency`、`res.currency.rate` | 货币主表与按日期生效的汇率历史分离；金额记录保存交易币种，并按公司本位币换算。 | [`res.currency` 源码](https://github.com/odoo/odoo/blob/19.0/odoo/addons/base/models/res_currency.py)；[多币种](https://www.odoo.com/documentation/19.0/applications/finance/accounting/get_started/multi_currency.html) |
| 客户资料/供应商资料 | `res.partner`，通过销售/采购属性区分角色 | 客户与供应商共享合作伙伴主数据，联系人、地址、银行账户作为一对多子记录；角色、付款条款、税务信息等按业务模块扩展。避免为客户和供应商复制两套完全独立的“公司表”。 | [`res.partner` 源码](https://github.com/odoo/odoo/blob/19.0/odoo/addons/base/models/res_partner.py)；[`res.partner.bank` 源码](https://github.com/odoo/odoo/blob/19.0/odoo/addons/base/models/res_bank.py) |
| 客户物料 | Odoo Community 没有与本需求完全对称的独立核心模型；最接近的是 `product.supplierinfo` 和带合作伙伴范围的价目表 | 可借鉴“产品 + 合作伙伴 + 外部编码/名称/价格”的关联记录，但本项目应明确新增 `partner_product`（含 customer/vendor 角色），而不是假设 Odoo 已完整覆盖客户物料。 | [`product.supplierinfo` 源码](https://github.com/odoo/odoo/blob/19.0/addons/product/models/product_supplierinfo.py)；[`product.pricelist` 源码](https://github.com/odoo/odoo/blob/19.0/addons/product/models/product_pricelist.py) |
| 库位 | `stock.location`；仓库为 `stock.warehouse` | 库位是树状层级，仓库包含多个业务库位；库存移动以源库位/目标库位形成流水，不能直接修改“现存量”字段。 | [`stock.location` 源码](https://github.com/odoo/odoo/blob/19.0/addons/stock/models/stock_location.py)；[`stock.warehouse` 源码](https://github.com/odoo/odoo/blob/19.0/addons/stock/models/stock_warehouse.py) |
| 多主体/公司 | `res.company`，用户通过公司和公司可用范围关联 | 业务单据要明确 `company_id`；跨公司访问由公司上下文、访问规则和记录规则约束，主数据是否共享要有显式策略。 | [`res.company` 源码](https://github.com/odoo/odoo/blob/19.0/odoo/addons/base/models/res_company.py)；[多公司指南](https://www.odoo.com/documentation/19.0/developer/howtos/company.html) |

### 对图片字段的建模建议

1. 产品类、默认库位、默认单位、采购/制造方式、采购员、质检策略、批号控制、库存/销售/生产会计科目等，拆成 `product` 主表及 `product_mrp`、`product_inventory`、`product_accounting` 等扩展表（或模块模型）。通过外键引用类别、单位、库位、员工、科目；不要把下拉选项保存成自由文本。
2. 物料的“基本属性 / 工程属性 / 库存属性 / MRP 属性”适合用同一物料 ID 下的分组页签；页签只是 UI 分组，校验和权限仍在服务端模型层完成。Odoo 的模板/变体分离可用于处理“同名不同规格”的情况。
3. 客户/供应商的付款方式、税率、报价方式、银行账户、联系人、适用公司等应分别建关系表或子模型；银行账户和联系人是一对多，不要固定为单个字符串列。Odoo 联系人模型的层级地址与联系人记录是值得复用的交互模式。

## 3. ORM、继承与扩展边界

- Odoo 的模型继承（`_inherit`）允许 addon 在不复制核心表的情况下增加字段、方法、约束和视图；本项目可采用“核心主数据 + 领域扩展表/模块”的方式，给后续采购、销售、生产增加字段，而不反复改动基础表。[继承 API](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html#inheritance-and-extension)
- 关系字段应在数据库层配合外键删除策略、唯一约束和应用层校验。Odoo 文档也明确区分 `related`、computed、stored 字段；对库存余额、账龄等派生数据，优先由交易流水计算或异步汇总，避免允许用户直接编辑派生结果。[计算字段](https://www.odoo.com/documentation/19.0/developer/tutorials/server_framework_101/08_compute_onchange.html)
- `onchange` 只负责表单交互提示，不是安全边界；最终约束必须放在模型约束/数据库约束，并在 API、批量导入时同样生效。[onchange 与约束](https://www.odoo.com/documentation/19.0/developer/tutorials/server_framework_101/08_compute_onchange.html)

## 4. 权限、审批状态与审计

- Odoo 的权限分为模型访问控制（`ir.model.access.csv`）和记录规则（record rules/domain）；前者决定能否对模型读写，后者按公司、部门、负责人等条件过滤记录。复刻时至少需要角色、模型级 CRUD、字段级敏感权限和行级公司隔离四层概念。[安全参考](https://www.odoo.com/documentation/19.0/developer/reference/backend/security.html)
- 业务审批不应只靠前端按钮隐藏。将状态机（草稿、待审、已审、作废/反审等）定义在服务端，状态变更校验操作者角色、前置条件和幂等性，并记录时间、用户、原因。Odoo 的采购、销售、库存单据都以状态字段驱动按钮和后续动作，可借鉴这种模式。[`purchase.order` 状态模型源码](https://github.com/odoo/odoo/blob/19.0/addons/purchase/models/purchase_order.py)
- 需要可追溯的主数据和单据可采用 `mail.thread` 的 chatter/字段追踪与 `mail.activity.mixin` 的待办活动；它们适合作为审计 UI 的参考，但财务级不可抵赖日志仍应在本项目单独设计追加写入的审计表。[消息线程 mixin](https://www.odoo.com/documentation/19.0/developer/reference/backend/mixins.html)
- 记录规则和多公司上下文必须在所有入口一致执行；不要把权限逻辑只放在菜单或前端路由。官方安全文档特别提醒，绕过 ORM、拼接 SQL 或使用不受限的 `sudo` 会绕过访问控制。[安全陷阱](https://www.odoo.com/documentation/19.0/developer/reference/backend/security.html#bypassing-the-orm)

## 5. 多公司、单位和库存一致性要点

- 多公司环境下，公司字段应成为产品、仓库、库位、价目表、税、会计科目和业务单据的显式维度；共享主数据与公司专属主数据要有清晰规则。Odoo 的 `with_company`/公司上下文模式可以作为服务层 API 设计参考。[多公司指南](https://www.odoo.com/documentation/19.0/developer/howtos/company.html)
- 单位换算必须绑定单位类别，并保存精度/舍入规则。图片中的“工程 BOM、生产领用、采购、销售、库存”换算可设计为用途维度的换算配置，但库存数量统一采用产品库存单位，业务单据保留原始单位与换算结果以便追溯。[UoM 文档](https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/product_management/configure/uom.html)
- 库存应通过库存移动、盘点和批次/序列号记录推导；库位是层级树和业务语义，不是简单下拉字典。Odoo 的库存文档将仓库、库位、路线和补货规则分开，适合后续逐步扩展。[库存库位](https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/warehouses_storage/inventory_management/locations.html)

## 6. 可借鉴与不建议直接复制

### 建议借鉴

- 领域拆分：以产品、单位、币种、合作伙伴、仓库/库位为稳定核心，再由采购、销售、MRP、财务模块扩展。
- 关系建模：模板/变体、伙伴/联系人、仓库/库位、币种/汇率、产品/伙伴价格等组合，能覆盖图片中的关联字段并支持一对多。
- 服务端 ORM + PostgreSQL 事务、数据库约束、状态机、模型级/行级权限、字段追踪和模块化迁移。
- 交互：资料维护与资料浏览分离；下拉/弹窗选择均来自主数据表；审批、反审、作废保留状态与审计信息；批量导入走同一服务端校验。

### 不建议直接复制或依赖

- 不要复制 Odoo 全部前端、工作流、会计和库存实现来“快速完成”本项目。其模块数量、依赖和升级约束很大，且会把本项目绑定到 Odoo 内部 API。
- 不要直接拷贝 Enterprise 模块或其代码/视图。Enterprise 代码受 Odoo Enterprise 协议约束，不能因为 Community 仓库开源就认为全部 Odoo 都是 LGPL。
- 不要把 Odoo 数据库表名、XML ID、内部字段名当作本项目公共 API；可借鉴概念与关系，字段名称和迁移策略应由本项目自行定义。
- 不要以 `sudo`、原生 SQL 或前端隐藏按钮规避权限；官方安全文档将其列为绕过访问控制的风险。[安全参考](https://www.odoo.com/documentation/19.0/developer/reference/backend/security.html)

## 7. 许可证边界（必须在立项时确认）

- Odoo Community 主仓库在 `19.0` 分支根目录提供 LGPL-3.0 许可证文本；仓库代码可在 LGPL-3.0 条件下使用、修改和再分发，需保留版权/许可证声明并遵守 LGPL 对链接/修改部分的要求。[Community LICENSE](https://github.com/odoo/odoo/blob/19.0/LICENSE)
- Odoo 官方许可证页区分 Community（LGPLv3）与 Enterprise（Odoo Enterprise Edition License，专有许可）。使用 Enterprise 模块、其源代码或受限资产前必须取得相应商业授权；不能把 Enterprise 代码复制进本项目或以 LGPL 方式再发布。[官方许可证说明](https://www.odoo.com/documentation/19.0/legal/licenses.html)
- 本项目若只借鉴公开文档描述的领域概念、数据关系和交互，不等于复制受版权保护的实现；仍应避免逐文件复制代码、XML 视图、翻译和专有资源，并为自有实现保留独立版权记录。需要发行基于 Odoo Community 的衍生模块时，法务应复核 LGPL-3.0 的动态链接、修改文件声明、许可证随附和源码提供义务。

## 8. 面向本项目的落地顺序

1. 先定义 `company`、`user/role`、`uom_category/uom`、`currency/currency_rate`、`product_category`、`warehouse/location`、`partner/contact/bank_account`、`product` 及其业务属性扩展；为编码、名称、单位类别、公司范围建立唯一约束。
2. 实现统一的服务端校验和审批状态机，再制作表单页签和资料浏览列表；前端字段必须来自 API 元数据或明确 DTO，避免直接暴露数据库表。
3. 以库存移动、采购订单、销售订单为第一批交易流水，验证产品/单位/库位/伙伴/公司关系和审计；之后再接 MRP、应收应付和成本核算。
4. 每个模块提供数据库迁移、权限种子、审计事件和 API 测试；以 Odoo 的 addon 边界为参考，但保持本项目技术栈和命名独立。

## 参考索引

- [Odoo 19.0 GitHub 主仓库](https://github.com/odoo/odoo/tree/19.0)
- [ORM API](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html)
- [安全参考](https://www.odoo.com/documentation/19.0/developer/reference/backend/security.html)
- [多公司指南](https://www.odoo.com/documentation/19.0/developer/howtos/company.html)
- [Odoo 官方许可证](https://www.odoo.com/documentation/19.0/legal/licenses.html)
