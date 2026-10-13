import { useCallback, useEffect, useRef, useState } from 'react'
import { api, listPayload, resourceApi } from '../api/client'
import { can } from '../auth/session'
import { configs } from './configs'

export function useResourceData(session, active, query = '') {
  const paged = ['customerMaterials', 'salesQuotes', 'salesOrders', 'deliveries'].includes(active)
  const [pagination, setPagination] = useState({ page: 1, count: 0, page_size: 50 })
  const pageRef = useRef(1)
  const [rows, setRows] = useState([])
  const [lookups, setLookups] = useState({})
  const [dashboard, setDashboard] = useState({})
  const [dashboardError, setDashboardError] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [dashboardLoading, setDashboardLoading] = useState(false)
  const [deliveryLookupsLoading, setDeliveryLookupsLoading] = useState(false)
  const requestSequence = useRef(0)
  const listCache = useRef(new Map())
  const deliveryLookupsLoaded = useRef(false)
  const deliveryLookupsPromise = useRef(null)
  const salesOrderLookupsLoaded = useRef(false)

  const loadList = useCallback((resource) => {
    const cache = listCache.current
    const cached = cache.get(resource)
    if (cached && (cached.pending || cached.expires > Date.now())) return cached.promise
    const entry = { pending: true }
    entry.promise = resourceApi(resource, session.token).list().then((result) => {
      entry.data = listPayload(result)
      entry.expires = Date.now() + 30_000
      entry.pending = false
      return entry.data
    }).catch((error) => {
      if (cache.get(resource) === entry) cache.delete(resource)
      throw error
    })
    cache.set(resource, entry)
    return entry.promise
  }, [session])

  const loadLookup = useCallback(
    async (id) => {
      const cfg = configs[id]
      if (!cfg || !can(session, cfg.permission)) return [id, []]
      const data = await loadList(cfg.resource)
      const filtered = cfg.filter ? data.filter(cfg.filter) : data
      return [id, filtered]
    },
    [session, loadList]
  )

  const loadPage = useCallback(async (target, page = 1, force = false) => {
    const cfg = configs[target]
    if (!cfg || !can(session, cfg.permission)) return
    const requestId = ++requestSequence.current
    const params = new URLSearchParams({ page, page_size: 50, q: query.trim() })
    const cacheKey = `${cfg.resource}?${params}`
    if (force) listCache.current.clear()
    const cached = listCache.current.get(cacheKey)
    setLoading(true)
    setError('')
    try {
      const result = cached && cached.expires > Date.now() ? cached.data
        : await api(`/${cfg.resource}/?${params}`, { token: session.token })
      if (requestId !== requestSequence.current) return
      listCache.current.set(cacheKey, { data: result, expires: Date.now() + 30_000 })
      pageRef.current = result.page || page
      setPagination({ page: result.page || page, count: result.count ?? result.length, page_size: 50 })
      setRows(listPayload(result))
      setLoading(false)
      const ids = target === 'customerMaterials' ? ['uoms'] : ['customers']
      const entries = await Promise.all(ids.map(loadLookup))
      if (requestId === requestSequence.current) setLookups(previous => ({ ...previous, ...Object.fromEntries(entries) }))
    } catch (error) {
      if (requestId === requestSequence.current) { setError(error.message); setLoading(false) }
    }
  }, [session, query, loadLookup])

  const loadEditorLookups = useCallback(async (target) => {
    const cfg = configs[target]
    const ids = [...new Set([...cfg.fields.filter(f => f.lookup).map(f => f.lookup), ...(cfg.extraLookups || [])])]
      .filter(id => !['materials', 'customerMaterials', 'salesQuotes'].includes(id))
    const entries = await Promise.all(ids.map(loadLookup))
    setLookups(previous => ({ ...previous, ...Object.fromEntries(entries) }))
  }, [loadLookup])

  const loadConfig = useCallback(
    async (target, force = true) => {
      if (['customerMaterials', 'salesQuotes', 'salesOrders', 'deliveries'].includes(target)) return loadPage(target, pageRef.current, force)
      const cfg = configs[target]
      if (!cfg || !can(session, cfg.permission)) return
      const requestId = ++requestSequence.current
      if (cfg.inventoryAnalysis || cfg.inventoryLedger || cfg.warehouseKind || ['balances', 'transactions', 'materials', 'suppliers', 'supplierQuotes', 'requisitions', 'receipts', 'purchaseReturns', 'tradeMrp'].includes(target)) { setRows([]); setLoading(false); setError(''); return }
      if (force) {
        listCache.current.clear()
        deliveryLookupsLoaded.current = false
        salesOrderLookupsLoaded.current = false
      }
      const cached = listCache.current.get(cfg.resource)
      const fresh = cached?.data && cached.expires > Date.now()
      if (fresh) setRows(cfg.filter ? cached.data.filter(cfg.filter) : cached.data)
      setLoading(!fresh)
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
        const dataPromise = loadList(cfg.resource)
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
    [session, loadLookup, loadList, loadPage]
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
      'uoms',
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
    if (paged) {
      pageRef.current = 1
      setLoading(true)
      const timer = setTimeout(() => loadPage(active, 1), 250)
      return () => { clearTimeout(timer); requestSequence.current += 1 }
    }
    if (active === 'overview') loadDashboard()
    else if (active !== 'materialImport') loadConfig(active, false)
  }, [active, loadConfig, loadDashboard, session, paged, loadPage])

  const invalidateLookup = () => {
    listCache.current.clear()
    deliveryLookupsLoaded.current = false
    salesOrderLookupsLoaded.current = false
  }
  const resetPage = (id) => {
    requestSequence.current += 1
    setError('')
    const cfg = configs[id]
    const cached = listCache.current.get(cfg?.resource)
    const fresh = cached?.data && cached.expires > Date.now()
    setRows(fresh ? (cfg.filter ? cached.data.filter(cfg.filter) : cached.data) : [])
    deliveryLookupsLoaded.current = false
    salesOrderLookupsLoaded.current = false
    setLoading(!fresh && id !== 'overview' && id !== 'materialImport')
    setDashboardLoading(id === 'overview')
    setDashboardError('')
  }
  const resetData = () => {
    requestSequence.current += 1
    listCache.current = new Map()
    deliveryLookupsLoaded.current = false
    salesOrderLookupsLoaded.current = false
    setRows([])
    setLookups({})
    setDashboard({})
    setDashboardError('')
  }

  return {
    rows,
    pagination: paged ? pagination : null,
    loadPage,
    loadEditorLookups,
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
