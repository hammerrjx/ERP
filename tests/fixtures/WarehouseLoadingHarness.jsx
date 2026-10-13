import React, { useState } from 'react'
import { createRoot } from 'react-dom/client'
import { WarehouseWorkspace } from '../../src/modules/inventory/WarehouseWorkspace'
import { InventoryLedger } from '../../src/modules/inventory/InventoryLedger'
import { useResourceData } from '../../src/app/useResourceData'
import { configs } from '../../src/app/configs'
import '../../src/styles.css'

const session = { token: 'fixture-only', permissions: ['*'] }
const calls = []
const material = { id: 99, code: 'REMOTE-099', name: '远程检索物料', specification: '验收规格', uom: 1, active: true }
window.fetch = async path => {
  const url = new URL(path, window.location.origin)
  calls.push(url.pathname + url.search)
  let data = []
  if (url.pathname === '/api/material/') {
    if (url.searchParams.get('lookup') !== 'warehouse') throw new Error('禁止全量物料请求')
    data = url.searchParams.get('q') || url.searchParams.get('ids') ? [material] : []
  } else if (url.pathname === '/api/location/') data = [{ id: 1, code: 'A01', name: '仓库' }]
  else if (url.pathname === '/api/uom/') data = [{ id: 1, code: 'EA', name: '件' }]
  else if (url.pathname === '/api/inventory-document/') {
    if (url.searchParams.get('summary') !== '1') throw new Error('禁止全量单据明细请求')
    data = [{ id: 1, number: 'MYMG26090001', document_date: '2026-09-01', status: 'draft', notes: '', to_location: 1 }]
  } else if (url.pathname === '/api/inventory-document/1/') data = {
    id: 1, number: 'MYMG26090001', document_date: '2026-09-01', kind: 'receipt', status: 'draft', notes: '', to_location: 1,
    lines: [{ id: 1, line_number: 10, material: 99, uom: 1, material_code: material.code, material_name: material.name, quantity: '1' }],
  }
  else if (/stock-(balance|transaction)/.test(url.pathname)) {
    if (!url.searchParams.has('page')) throw new Error('禁止首屏全量库存请求')
    const page = Number(url.searchParams.get('page'))
    data = { count: 105, results: Array.from({ length: page === 1 ? 100 : 5 }, (_, i) => ({ id: (page - 1) * 100 + i + 1,
      material_code: `PART-${(page - 1) * 100 + i + 1}`, material_name: '分页物料', location_code: 'A01', uom_name: '件', quantity: '1' })) }
  } else if (/material-(inventory|movement)-detail/.test(url.pathname)) {
    if (!url.searchParams.has('source')) throw new Error('禁止公共加载器重复全量查询')
    data = { count: 1, results: [{ id: 1, material_code: 'REPORT-001', quantity: '1' }], columns: [['material_code', '物料编码'], ['quantity', '数量']], batch: { id: 1, source: 'local' }, page: 1 }
  }
  return { ok: true, json: async () => data }
}

function Harness() {
  const [active, setActive] = useState('warehouseReceipt')
  const [requests, setRequests] = useState([])
  // Exercise the real outer loader alongside the dedicated workspace.
  useResourceData(session, active)
  const entries = Object.entries(configs).filter(([, c]) => ['receipt', 'issue'].includes(c.warehouseKind) && !c.initialCount)
  const chosen = configs[active]
  return <><nav>{[...entries.map(([id, c]) => [id, c.title]), ['balances', '库存余额'], ['transactions', '库存流水'], ['materialInventoryDetail', '物料库存明细'], ['materialMovementDetail', '物料进出明细']].map(([id, title]) => <button key={id} onClick={() => setActive(id)}>{title}</button>)}<button onClick={() => setRequests([...calls])}>显示请求记录</button></nav>
    {chosen?.warehouseKind ? <WarehouseWorkspace key={active} kind={chosen.warehouseKind} title={chosen.title} session={session}/> : chosen ? <InventoryLedger key={active} resource={chosen.resource} title={chosen.title} session={session}/> : <p>请选择仓储页面</p>}
    <pre aria-label="请求记录">{requests.join('\n')}</pre></>
}
createRoot(document.getElementById('root')).render(<Harness/> )
