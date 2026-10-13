import React from 'react'
import { MaterialWorkspace } from '../../src/modules/master-data/MaterialWorkspace'

export function mount(permissions = ['*']) {
  window.__ERP_REACT_ROOT__.render(<MaterialWorkspace key={permissions.join(',')} session={{ token: 'isolated-material-test', permissions }} />)
}
