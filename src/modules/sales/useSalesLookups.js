import { useCallback, useEffect, useRef, useState } from 'react'
import { api, listPayload } from '../../api/client'

const merge = (old, rows) => [...new Map([...old, ...rows].map(row => [row.id, row])).values()]

// Keep selected rows in memory while fetching at most 50 candidates per search.
export function useSalesLookups(token, customer, lines = [], initial = {}) {
  const [materials, setMaterials] = useState(initial.materials || [])
  const [customerMaterials, setCustomerMaterials] = useState(initial.customerMaterials || [])
  const [error, setError] = useState('')
  const requests = useRef({})
  const timers = useRef({})
  const search = useCallback((kind, query = '', material = '') => {
    clearTimeout(timers.current[kind])
    const version = (requests.current[kind] || 0) + 1
    requests.current[kind] = version
    timers.current[kind] = setTimeout(async () => {
      try {
        const path = kind === 'materials'
          ? `/material/sales-candidates/?${new URLSearchParams({ q: query })}`
          : `/customer-material/?${new URLSearchParams({ page: 1, q: query, customer, material, enabled: 1 })}`
        const data = await api(path, { token })
        if (requests.current[kind] !== version) return
        ;(kind === 'materials' ? setMaterials : setCustomerMaterials)(old => merge(old, listPayload(data)))
        setError('')
      } catch (err) {
        if (requests.current[kind] === version) setError(err.message)
      }
    }, 200)
  }, [token, customer])
  const materialIds = [...new Set(lines.map(line => line.material).filter(Boolean))].join(',')
  const customerMaterialIds = [...new Set(lines.map(line => line.customer_material).filter(Boolean))].join(',')
  useEffect(() => {
    let alive = true
    const fetchSelected = async () => {
      try {
        const selectedMaterials = await Promise.all(materialIds.split(',').filter(Boolean).map(id => api(`/material/${id}/`, { token })))
        const selectedMappings = await Promise.all(customerMaterialIds.split(',').filter(Boolean).map(id => api(`/customer-material/${id}/`, { token })))
        if (alive) { setMaterials(old => merge(old, selectedMaterials)); setCustomerMaterials(old => merge(old, selectedMappings)) }
      } catch (err) { if (alive) setError(err.message) }
    }
    fetchSelected()
    return () => { alive = false }
  }, [token, materialIds, customerMaterialIds])
  useEffect(() => {
    requests.current.customerMaterials = (requests.current.customerMaterials || 0) + 1
    setCustomerMaterials([])
    if (customer) search('customerMaterials')
    return () => { clearTimeout(timers.current.customerMaterials); requests.current.customerMaterials += 1 }
  }, [customer, search])
  useEffect(() => {
    search('materials')
    return () => { Object.values(timers.current).forEach(clearTimeout); Object.keys(requests.current).forEach(key => requests.current[key] += 1) }
  }, [search])
  return { materials, customerMaterials, search, error }
}
