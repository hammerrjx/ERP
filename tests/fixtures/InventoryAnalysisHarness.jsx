import React from 'react'
import { InventoryAnalysis } from '../../src/modules/inventory/InventoryAnalysis'
export function mount() {
  window.__ERP_REACT_ROOT__.render(<InventoryAnalysis title="物料库存批量查询" session={{ token: 'isolated-query-test', permissions: ['*'] }} />)
}
