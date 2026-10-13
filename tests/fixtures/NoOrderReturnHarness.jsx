import React from 'react'
import { createRoot } from 'react-dom/client'
import { NoOrderReturnWorkspace } from '../../src/modules/sales/NoOrderReturnWorkspace'
export function mount() {
  const host = document.createElement('div')
  document.body.replaceChildren(host)
  createRoot(host).render(<NoOrderReturnWorkspace session={{ token: 'test-only', permissions: ['*'] }} />)
}
