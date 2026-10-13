import React, { useState } from 'react'
import { createRoot } from 'react-dom/client'
import { ConversionWorkspace } from '../../src/modules/purchase/ConversionWorkspace'
import { PurchaseOrderWorkspace } from '../../src/modules/purchase/PurchaseOrderWorkspace'

export function mount(token) {
  function Harness() {
    const [id, setId] = useState(null)
    const session = { token, username: 'flow-admin', permissions: ['*'] }
    return <div style={{ margin: 0, background: '#fff' }}>{id
      ? <PurchaseOrderWorkspace session={session} initialId={id} onClose={() => setId(null)} />
      : <ConversionWorkspace session={session} onOpenOrder={setId} onClose={() => {}} />}</div>
  }
  document.body.style.margin = '0'
  const host = document.createElement('div'); document.body.replaceChildren(host)
  createRoot(host).render(<Harness />)
}
