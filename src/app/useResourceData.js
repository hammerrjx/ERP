import { useCallback, useEffect, useRef, useState } from 'react'
import { listPayload, resourceApi } from '../api/client'
import { can } from '../auth/session'
import { configs } from './configs'

export function useResourceData(session, active) {
  const [rows, setRows] = useState([])
  const [lookups, setLookups] = useState({})
  const [dashboard, setDashboard] = useState({})
  const [dashboardError, setDashboardError] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [dashboardLoading, setDashboardLoading] = useState(false)
  const [deliveryLookupsLoading, setDeliveryLookupsLoading] = useState(false)
  const requestSequence = useRef(0)
  const lookupCache = useRef(new Map())
  const deliveryLookupsLoaded = useRef(false)
  const deliveryLookupsPromise = useRef(null)
  const salesOrderLookupsLoaded = useRef(false)

  const loadLookup = useCallback(
    async (id) => {
      const cfg = configs[id]
      if (!cfg || !can(session, cfg.permission)) return [id, []]
      if (lookupCache.current.has(id)) return [id, lookupCache.current.get(id)]
      const data = listPayload(await resourceApi(cfg.resource, session.token).list())
      const filtered = cfg.filter ? data.filter(cfg.filter) : data
      if (
        [
          'customers',
          'customerAddresses',
          'materials',
          'customerMaterials',
          'uoms',
          'currencies',
          'businessGroups',
          'paymentMethods',
          'employees',
          'locations'
        ].includes(id)
      ) {
        lookupCache.current.set(id, filtered)
      }
      return [id, filtered]
    },
    [session]
  )

  const loadConfig = useCallback(
    async (target) => {
      const cfg = configs[target]
      if (!cfg || !can(session, cfg.permission)) return
      const requestId = ++requestSequence.current
      setLoading(true)
      setError('')
      try {
        const allLookupIds = [
          ...new Set([
            ...cfg.fields.filter((item) => item.lookup).map((item) => item.lookup),
            ...(cfg.extraLookups || [])
          ])
        ]
        const lookupIds =
          cfg.resource === 'delivery-order' || cfg.resource === 'sales-order'
            ? allLookupIds.filter((id) => id === 'customers')
            : allLookupIds
        const lookupPromise = Promise.all(lookupIds.map(loadLookup))
        const dataPromise = resourceApi(cfg.resource, session.token).list()
        dataPromise
          .then((result) => {
            if (requestId !== requestSequence.current) return
            let data = listPayload(result)
            if (cfg.filter) data = data.filter(cfg.filter)
            setRows(data)
            setLoading(false)
          })
          .catch((requestError) => {
            if (requestId === requestSequence.current) {
              setError(requestError.message)
              setLoading(false)
            }
          })
        lookupPromise
          .then((entries) => {
            if (requestId !== requestSequence.current) return
            if (entries.length) setLookups((previous) => ({ ...previous, ...Object.fromEntries(entries) }))
          })
          .catch((requestError) => {
            if (requestId === requestSequence.current) setError(requestError.message)
          })
        await dataPromise
      } catch (requestError) {
        if (requestId === requestSequence.current) setError(requestError.message)
      }
    },
    [session, loadLookup]
  )

  const loadDeliveryLookups = useCallback(async () => {
    if (deliveryLookupsLoaded.current) return
    if (deliveryLookupsPromise.current) return deliveryLookupsPromise.current
    const ids = ['customerAddresses', 'locations']
    setDeliveryLookupsLoading(true)
    deliveryLookupsPromise.current = (async () => {
      try {
        const entries = await Promise.all(ids.map(loadLookup))
        setLookups((previous) => ({ ...previous, ...Object.fromEntries(entries) }))
        deliveryLookupsLoaded.current = true
      } catch (requestError) {
        setError(requestError.message)
        throw requestError
      } finally {
        deliveryLookupsPromise.current = null
        setDeliveryLookupsLoading(false)
      }
    })()
    return deliveryLookupsPromise.current
  }, [loadLookup])

  const invalidateDeliveryLookups = () => {
    deliveryLookupsLoaded.current = false
  }

  const loadSalesOrderLookups = useCallback(async () => {
    if (salesOrderLookupsLoaded.current) return
    salesOrderLookupsLoaded.current = true
    const ids = [
      'customerAddresses',
      'businessGroups',
      'paymentMethods',
      'currencies',
      'materials',
      'uoms',
      'customerMaterials',
      'employees'
    ]
    try {
      const entries = await Promise.all(ids.map(loadLookup))
      setLookups((previous) => ({ ...previous, ...Object.fromEntries(entries) }))
    } catch (requestError) {
      salesOrderLookupsLoaded.current = false
      setError(requestError.message)
    }
  }, [loadLookup])

  const loadDashboard = useCallback(async () => {
    const requestId = ++requestSequence.current
    setDashboardLoading(true)
    setDashboardError('')
    const ids = ['materials', 'salesOrders', 'purchaseOrders', 'balances', 'alerts'].filter((id) =>
      can(session, configs[id].permission)
    )
    const entries = await Promise.all(
      ids.map(async (id) => {
        try {
          return [id, listPayload(await resourceApi(configs[id].resource, session.token).list()), '']
        } catch (requestError) {
          return [id, null, `${configs[id].title}: ${requestError.message}`]
        }
      })
    )
    if (requestId === requestSequence.current) {
      setDashboard(Object.fromEntries(entries.map(([id, data]) => [id, data])))
      setDashboardError(
        entries
          .map(([, , message]) => message)
          .filter(Boolean)
          .join('；')
      )
      setDashboardLoading(false)
    }
  }, [session])

  useEffect(() => {
    if (!session) return
    if (active === 'overview') loadDashboard()
    else if (active !== 'materialImport') loadConfig(active)
  }, [active, loadConfig, loadDashboard, session])

  const invalidateLookup = (resource) => {
    const lookupByResource = {
      partner: 'customers',
      'customer-address': 'customerAddresses',
      material: 'materials',
      'customer-material': 'customerMaterials',
      uom: 'uoms',
      currency: 'currencies',
      'business-group': 'businessGroups',
      'payment-method': 'paymentMethods',
      employee: 'employees',
      location: 'locations'
    }
    const id = lookupByResource[resource]
    if (id) lookupCache.current.delete(id)
    deliveryLookupsLoaded.current = false
    salesOrderLookupsLoaded.current = false
  }
  const resetPage = (id) => {
    setError('')
    setRows([])
    deliveryLookupsLoaded.current = false
    salesOrderLookupsLoaded.current = false
    setLoading(id !== 'overview' && id !== 'materialImport')
    setDashboardLoading(id === 'overview')
    setDashboardError('')
  }
  const resetData = () => {
    requestSequence.current += 1
    lookupCache.current.clear()
    deliveryLookupsLoaded.current = false
    salesOrderLookupsLoaded.current = false
    setRows([])
    setLookups({})
    setDashboard({})
    setDashboardError('')
  }

  return {
    rows,
    lookups,
    dashboard,
    dashboardError,
    error,
    loading,
    dashboardLoading,
    deliveryLookupsLoading,
    setError,
    loadConfig,
    loadDashboard,
    loadDeliveryLookups,
    loadSalesOrderLookups,
    invalidateDeliveryLookups,
    invalidateLookup,
    resetPage,
    resetData
  }
}
