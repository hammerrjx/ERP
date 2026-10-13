import React, { useState } from 'react'
import { useResourceData } from '../../src/app/useResourceData'
import { ResourceTable } from '../../src/components/ResourceTable'
import { configs } from '../../src/app/configs'

const session = { token: 'performance-test', permissions: ['*'] }
function Harness() {
  const [active, select] = useState('customerMaterials')
  const data = useResourceData(session, active)
  window.switchList = id => { data.resetPage(id); select(id) }
  window.refreshList = () => data.loadConfig(active)
  window.invalidateList = () => data.invalidateLookup('customer-material')
  return <ResourceTable key={active} rows={data.rows} total={data.rows.length}
    config={configs[active]} session={session} lookups={data.lookups} loading={data.loading} />
}
export function mount() {
  window.started = performance.now()
  window.__ERP_REACT_ROOT__.render(<Harness />)
}
