import { DetailModal, RecordModal } from '../components/ResourceModals'
import { CustomerMaterialModal } from '../modules/sales/CustomerMaterialModal'
import { SalesOrderModal } from '../modules/sales/SalesOrderModal'
import { MaterialRecordModal } from '../modules/master-data/MaterialRecordModal'
import { SupplierQuoteModal } from '../modules/purchase/SupplierQuoteModal'
import { SalesQuoteModal } from '../modules/sales/SalesQuoteModal'
import { DeliveryOrderModal } from '../modules/sales/DeliveryOrderModal'

const editors = {
  material: MaterialRecordModal,
  'customer-material': CustomerMaterialModal,
  'sales-order': SalesOrderModal,
  'delivery-order': DeliveryOrderModal,
  'sales-quote': SalesQuoteModal,
  'supplier-quote': SupplierQuoteModal
}
const detailEditors = new Set(['sales-order', 'delivery-order', 'sales-quote', 'supplier-quote'])

export function ResourceModal({ config, record, readOnly = false, ...props }) {
  if (readOnly && !detailEditors.has(config.resource)) {
    return <DetailModal config={config} row={record} {...props} />
  }
  const Editor = editors[config.resource] || RecordModal
  return <Editor config={config} record={record} readOnly={readOnly} {...props} />
}
