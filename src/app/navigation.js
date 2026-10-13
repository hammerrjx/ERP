import {
  Boxes, ClipboardList, Factory, LayoutDashboard, Settings, ShieldCheck,
  ShoppingCart, Warehouse,
} from 'lucide-react'

export const modules = [
  { id: 'overview', label: '工作台', icon: LayoutDashboard },
  { id: 'organization', label: '组织与权限', icon: ShieldCheck, items: [['departments', '部门'], ['users', '登录账户'], ['roles', '角色权限'], ['userRoles', '用户角色'], ['approvalRules', '审批规则']] },
  { id: 'base', label: '基础资料', icon: Boxes, items: [['companies', '主体公司'], ['employees', '用户/员工资料'], ['warehouses', '仓库'], ['locations', '库位'], ['currencies', '货币'], ['currencyRates', '货币汇率'], ['paymentMethods', '支付方式'], ['businessGroups', '业务组'], ['uomCategories', '单位类别'], ['uoms', '计量单位'], ['taxCodes', '税务编码'], ['categories', '产品类'], ['materials', '物料信息']] },
  { id: 'engineering', label: '工程资料', icon: Factory, items: [['boms', 'BOM'], ['bomLines', 'BOM明细'], ['routings', '工艺路线'], ['routingOperations', '工艺工序']] },
  { id: 'sales', label: '销售管理', icon: ShoppingCart, items: [['customers', '客户资料'], ['customerAddresses', '客户地址'], ['customerMaterials', '客户物料'], ['salesQuotes', '销售报价'], ['salesQuoteLines', '报价明细'], ['salesOrders', '客户订单'], ['salesOrderLines', '客户订单明细'], ['deliveries', '送货单'], ['deliveryLines', '送货明细'], ['noOrderReturns', '无订单退货'], ['salesReturns', '有订单退货'], ['salesReturnLines', '退货明细']] },
  { id: 'purchase', label: '采购管理', icon: ClipboardList, items: [['tradeMrp', '贸易端MRP'], ['suppliers', '供应商资料'], ['supplierQuotes', '供应商报价'], ['requisitions', '请购单'], ['requisitionConvert', '请购单转采购单'], ['requisitionLines', '请购明细'], ['rfqs', '询价单'], ['rfqLines', '报价明细'], ['inquiries', '供应商响应'], ['purchaseOrders', '采购单'], ['purchaseOrderLines', '采购明细'], ['receipts', '收货单'], ['receiptLines', '收货明细'], ['purchaseReturns', '采购退货'], ['purchaseReturnLines', '采购退货明细'], ['payableVouchers', '应付凭单'], ['payableVoucherLines', '应付来源明细']] },
  { id: 'systemFeatures', label: '系统功能', icon: Settings, items: [['materialImport', '批量导入']] },
  { id: 'inventory', label: '仓储管理', icon: Warehouse, items: [['warehouseTransfer', '转仓单'], ['warehouseReceipt', '计划外入库单'], ['warehouseIssue', '计划外出库单'], ['warehouseCount', '盘点单'], ['warehouseScrap', '报废单'], ['balances', '库存余额'], ['transactions', '库存流水'], ['inventoryReport', '收发存报表'], ['inventoryOpening', '期初库存录入'], ['materialInventoryBatch', '物料库存批量查询'], ['materialMonthlyInventory', '物料进销存明细查询'], ['materialInventoryDetail', '物料库存明细查询'], ['materialMovementDetail', '物料进出明细查询'], ['transferDetail', '转仓明细查询'], ['countResult', '盘点结果查询'], ['unplannedReceiptDetail', '计划外入库查询'], ['unplannedIssueDetail', '计划外出库查询'], ['scrapDetail', '报废明细查询'], ['inventoryHistory', '源库历史查询'], ['alerts', '库存预警']] },
]
