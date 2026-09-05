import {
  Boxes, ClipboardList, Factory, LayoutDashboard, Settings, ShieldCheck,
  ShoppingCart, Warehouse,
} from 'lucide-react'

export const modules = [
  { id: 'overview', label: '工作台', icon: LayoutDashboard },
  { id: 'organization', label: '组织与权限', icon: ShieldCheck, items: [['departments', '部门'], ['users', '用户'], ['roles', '角色权限'], ['userRoles', '用户角色'], ['approvalRules', '审批规则']] },
  { id: 'base', label: '基础资料', icon: Boxes, items: [['companies', '主体公司'], ['employees', '员工/业务员'], ['warehouses', '仓库'], ['locations', '库位'], ['currencies', '货币'], ['paymentMethods', '支付方式'], ['businessGroups', '业务组'], ['uomCategories', '单位类别'], ['uoms', '计量单位'], ['taxCodes', '税务编码'], ['categories', '产品类'], ['materials', '物料信息']] },
  { id: 'engineering', label: '工程资料', icon: Factory, items: [['boms', 'BOM'], ['bomLines', 'BOM明细'], ['routings', '工艺路线'], ['routingOperations', '工艺工序']] },
  { id: 'sales', label: '销售管理', icon: ShoppingCart, items: [['customers', '客户资料'], ['customerAddresses', '客户地址'], ['customerMaterials', '客户物料'], ['salesQuotes', '销售报价'], ['salesQuoteLines', '报价明细'], ['salesOrders', '客户订单'], ['salesOrderLines', '客户订单明细'], ['deliveries', '送货单'], ['deliveryLines', '送货明细'], ['salesReturns', '销售退货'], ['salesReturnLines', '退货明细']] },
  { id: 'purchase', label: '采购管理', icon: ClipboardList, items: [['suppliers', '供应商资料'], ['supplierQuotes', '供应商报价'], ['requisitions', '请购单'], ['requisitionLines', '请购明细'], ['rfqs', '询价单'], ['rfqLines', '报价明细'], ['inquiries', '供应商响应'], ['purchaseOrders', '采购单'], ['purchaseOrderLines', '采购明细'], ['receipts', '收货单'], ['receiptLines', '收货明细'], ['purchaseReturns', '采购退货'], ['purchaseReturnLines', '采购退货明细'], ['payableVouchers', '应付凭单'], ['payableVoucherLines', '应付来源明细']] },
  { id: 'systemFeatures', label: '系统功能', icon: Settings, items: [['materialImport', '批量导入']] },
  { id: 'inventory', label: '库存管理', icon: Warehouse, items: [['balances', '库存余额'], ['transactions', '库存流水'], ['transfers', '库存调拨'], ['transferLines', '调拨明细'], ['counts', '库存盘点'], ['countLines', '盘点明细'], ['alerts', '缺料预警']] },
]
