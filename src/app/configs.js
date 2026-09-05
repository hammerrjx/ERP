import { organizationConfigs } from '../modules/system/configs'
import { masterDataConfigs } from '../modules/master-data/configs'
import { engineeringConfigs } from '../modules/engineering/configs'
import { salesConfigs } from '../modules/sales/configs'
import { purchaseConfigs } from '../modules/purchase/configs'
import { inventoryConfigs } from '../modules/inventory/configs'

export const configs = {
  ...organizationConfigs,
  ...masterDataConfigs,
  ...engineeringConfigs,
  ...salesConfigs,
  ...purchaseConfigs,
  ...inventoryConfigs,
}

for (const id of ['departments', 'currencies', 'paymentMethods', 'locations', 'categories', 'uoms', 'materials', 'customers', 'customerMaterials', 'suppliers']) {
  configs[id].exportable = true
}
configs.customers.partnerKind = 'customer'
configs.suppliers.partnerKind = 'supplier'
