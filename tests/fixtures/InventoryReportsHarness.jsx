import React, { useState } from 'react'
import { InventoryLedger } from '../../src/modules/inventory/InventoryLedger'

function Harness() {
  const [resource, setResource] = useState('material-inventory-detail')
  window.selectMovementReport = () => setResource('material-movement-detail')
  window.selectInventoryResource = setResource
  return <InventoryLedger resource={resource} title={resource === 'material-movement-detail' ? '物料进出明细查询' : '物料库存明细查询'} session={{ token: 'report-browser-test' }}/>
}
export function mount() {
  window.__ERP_REACT_ROOT__.render(<Harness />)
}
