import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  Bell, Boxes, Check, ChevronDown, CircleHelp, Coins, Download, Filter, LogOut,
  Menu, Plus, RefreshCw, Search, Settings, ShieldCheck, SlidersHorizontal, X,
} from 'lucide-react'
import { api, download, listPayload, resourceApi, upload } from '../api/client'
import { can, clearSession, readSession, saveSession } from '../auth/session'
import { Login } from '../auth/Login'
import { ResourceTable, Stat } from '../components/ResourceTable'
import { ConversionModal, CustomerMaterialModal, DetailModal, DocumentEvidenceModal, MaterialRecordModal, PayableGenerateModal, RecordModal, SalesOrderModal, SalesOrderWorkflowModal } from '../components/ResourceModals'
import { Dashboard } from '../modules/dashboard/Dashboard'
import { MaterialImport } from '../modules/purchase/MaterialImport'
import { SupplierQuoteModal } from '../modules/purchase/SupplierQuoteModal'
import { SalesQuoteModal } from '../modules/sales/SalesQuoteModal'
import { DeliveryOrderModal } from '../modules/sales/DeliveryOrderModal'
import { displayValue, labelFor } from '../shared/presentation'
import { modules } from './navigation'
import { configs } from './configs'

export default function App() {
  const [session, setSession] = useState(readSession)
  const [active, setActive] = useState('overview')
  const [open, setOpen] = useState({})
  const [rows, setRows] = useState([])
  const [lookups, setLookups] = useState({})
  const [dashboard, setDashboard] = useState({})
  const [dashboardError, setDashboardError] = useState('')
  const [query, setQuery] = useState('')
  const [modal, setModal] = useState(false)
  const [editor, setEditor] = useState(null)
  const [detail, setDetail] = useState(null)
  const [payableModal, setPayableModal] = useState(false)
  const [conversionRow, setConversionRow] = useState(null)
  const [workflow, setWorkflow] = useState(null)
  const [evidenceRow, setEvidenceRow] = useState(null)
  const [notice, setNotice] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [dashboardLoading, setDashboardLoading] = useState(false)
  const [mobileNav, setMobileNav] = useState(false)
  const [deliveryLookupsLoading, setDeliveryLookupsLoading] = useState(false)
  const requestSequence = useRef(0)
  const lookupCache = useRef(new Map())
  const deliveryLookupsLoaded = useRef(false)
  const deliveryLookupsPromise = useRef(null)
  const salesOrderLookupsLoaded = useRef(false)
  const current = configs[active]

  const allowedModules = useMemo(() => modules.map(module => module.items ? {
    ...module,
    items: module.items.filter(([id]) => can(session, configs[id].permission)),
  } : module).filter(module => !module.items || module.items.length), [session])

  const loadConfig = useCallback(async target => {
    const cfg = configs[target]
    if (!cfg || !can(session, cfg.permission)) return
    const requestId = ++requestSequence.current
    setLoading(true); setError('')
    try {
      const allLookupIds = [...new Set([...cfg.fields.filter(item => item.lookup).map(item => item.lookup), ...(cfg.extraLookups || [])])]
      const lookupIds = cfg.resource === 'delivery-order' || cfg.resource === 'sales-order'
        ? allLookupIds.filter(id => id === 'customers')
        : allLookupIds
      const lookupPromise = Promise.all(lookupIds.map(async id => {
        const lookupConfig = configs[id]
        if (!lookupConfig || !can(session, lookupConfig.permission)) return [id, []]
        if (lookupCache.current.has(id)) return [id, lookupCache.current.get(id)]
        const data = listPayload(await resourceApi(lookupConfig.resource, session.token).list())
        const filtered = lookupConfig.filter ? data.filter(lookupConfig.filter) : data
        if (['customers', 'customerAddresses', 'materials', 'customerMaterials', 'uoms', 'currencies', 'businessGroups', 'paymentMethods', 'employees', 'locations'].includes(id)) {
          lookupCache.current.set(id, filtered)
        }
        return [id, filtered]
      }))
      const dataPromise = resourceApi(cfg.resource, session.token).list()
      dataPromise.then(result => {
        if (requestId !== requestSequence.current) return
        let data = listPayload(result)
        if (cfg.filter) data = data.filter(cfg.filter)
        setRows(data)
        setLoading(false)
      }).catch(requestError => {
        if (requestId === requestSequence.current) { setError(requestError.message); setLoading(false) }
      })
      lookupPromise.then(entries => {
        if (requestId !== requestSequence.current) return
        if (entries.length) setLookups(previous => ({ ...previous, ...Object.fromEntries(entries) }))
      }).catch(requestError => {
        if (requestId === requestSequence.current) setError(requestError.message)
      })
      await dataPromise
    } catch (requestError) {
      if (requestId === requestSequence.current) setError(requestError.message)
    } finally {
      // The main list clears loading as soon as it is available; lookups may continue in the background.
    }
  }, [session])

  const loadDeliveryLookups = useCallback(async () => {
    if (deliveryLookupsLoaded.current) return
    if (deliveryLookupsPromise.current) return deliveryLookupsPromise.current
    const ids = ['salesOrders', 'customerAddresses', 'locations', 'salesOrderLines', 'materials', 'customerMaterials', 'uoms', 'currencies']
    setDeliveryLookupsLoading(true)
    deliveryLookupsPromise.current = (async () => {
      try {
        const entries = await Promise.all(ids.map(async id => {
          const cfg = configs[id]
          if (!cfg || !can(session, cfg.permission)) return [id, []]
          if (lookupCache.current.has(id)) return [id, lookupCache.current.get(id)]
          const data = listPayload(await resourceApi(cfg.resource, session.token).list())
          const filtered = cfg.filter ? data.filter(cfg.filter) : data
          if (['customers', 'customerAddresses', 'materials', 'customerMaterials', 'uoms', 'currencies', 'businessGroups', 'paymentMethods', 'employees', 'locations'].includes(id)) {
            lookupCache.current.set(id, filtered)
          }
          return [id, filtered]
        }))
        setLookups(previous => ({ ...previous, ...Object.fromEntries(entries) }))
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
  }, [session])

  const invalidateDeliveryLookups = () => { deliveryLookupsLoaded.current = false }

  const loadSalesOrderLookups = useCallback(async () => {
    if (salesOrderLookupsLoaded.current) return
    salesOrderLookupsLoaded.current = true
    const ids = ['customerAddresses', 'businessGroups', 'paymentMethods', 'currencies', 'materials', 'uoms', 'customerMaterials', 'employees']
    try {
      const entries = await Promise.all(ids.map(async id => {
        const cfg = configs[id]
        if (!cfg || !can(session, cfg.permission)) return [id, []]
        if (lookupCache.current.has(id)) return [id, lookupCache.current.get(id)]
        const data = listPayload(await resourceApi(cfg.resource, session.token).list())
        const filtered = cfg.filter ? data.filter(cfg.filter) : data
        lookupCache.current.set(id, filtered)
        return [id, filtered]
      }))
      setLookups(previous => ({ ...previous, ...Object.fromEntries(entries) }))
    } catch (requestError) {
      salesOrderLookupsLoaded.current = false
      setError(requestError.message)
    }
  }, [session])

  const loadDashboard = useCallback(async () => {
    const requestId = ++requestSequence.current
    setDashboardLoading(true); setDashboardError('')
    const ids = ['materials', 'salesOrders', 'purchaseOrders', 'balances', 'alerts'].filter(id => can(session, configs[id].permission))
    const entries = await Promise.all(ids.map(async id => {
      try { return [id, listPayload(await resourceApi(configs[id].resource, session.token).list()), ''] }
      catch (requestError) { return [id, null, `${configs[id].title}: ${requestError.message}`] }
    }))
    if (requestId === requestSequence.current) {
      setDashboard(Object.fromEntries(entries.map(([id, data]) => [id, data])))
      setDashboardError(entries.map(([, , message]) => message).filter(Boolean).join('；'))
      setDashboardLoading(false)
    }
  }, [session])

  useEffect(() => {
    if (!session) return
    if (active === 'overview') loadDashboard()
    else if (active !== 'materialImport') loadConfig(active)
  }, [active, loadConfig, loadDashboard, session])

  const select = id => {
    setActive(id); setQuery(''); setNotice(''); setError(''); setMobileNav(false)
    setRows([])
    deliveryLookupsLoaded.current = false
    salesOrderLookupsLoaded.current = false
    setLoading(id !== 'overview' && id !== 'materialImport')
    setDashboardLoading(id === 'overview'); setDashboardError('')
  }
  const logout = () => { clearSession(); lookupCache.current.clear(); setSession(null); setRows([]); setLookups({}); setDashboard({}); setDashboardError('') }
  const invalidateLookup = resource => {
    const lookupByResource = {
      partner: 'customers', 'customer-address': 'customerAddresses', material: 'materials',
      'customer-material': 'customerMaterials', uom: 'uoms', currency: 'currencies',
      'business-group': 'businessGroups', 'payment-method': 'paymentMethods', employee: 'employees', location: 'locations',
    }
    const id = lookupByResource[resource]
    if (id) lookupCache.current.delete(id)
  }
  const refresh = () => active === 'overview' ? loadDashboard() : active === 'materialImport' ? undefined : loadConfig(active)
  const add = async values => {
    const payload = Object.fromEntries(Object.entries(values).filter(([, value]) => value !== '' && value !== undefined))
    try {
      await resourceApi(current.resource, session.token).create(payload)
      invalidateLookup(current.resource); setModal(false); await loadConfig(active); setNotice(`已创建${current.title}`)
    } catch (requestError) { setError(requestError.message) }
  }
  const saveRecord = async (values, row) => {
    const payload = Object.fromEntries(Object.entries(values).filter(([, value]) => value !== '' && value !== undefined))
    try {
      const resource = resourceApi(current.resource, session.token)
      await (row?.id ? resource.update(row.id, payload) : resource.create(payload))
      invalidateLookup(current.resource); setModal(false); setEditor(null); await loadConfig(active); setNotice(row?.id ? `已更新${current.title}` : `已创建${current.title}`)
    } catch (requestError) { setError(requestError.message) }
  }
  const saveDeliveryOrder = async (values, row) => {
    try {
      const { lines = [], ...header } = values
      const orderLines = lookups.salesOrderLines || []
      const orders = lookups.salesOrders || []
      const sourceOrders = [...new Set(lines.map(line => orderLines.find(item => item.id === Number(line.sales_order_line))?.order).filter(Boolean))]
      const firstOrder = orders.find(order => order.id === Number(sourceOrders[0]))
      const deliveryHeader = { ...header, customer_po: header.customer_po || firstOrder?.customer_po || '', sales_order: sourceOrders.length === 1 ? sourceOrders[0] : undefined }
      const resource = resourceApi('delivery-order', session.token)
      if (!row?.id) {
        await api('/delivery-order/generate-from-order/', { token: session.token, method: 'POST', body: { ...deliveryHeader, lines } })
      } else {
        const saved = await resource.update(row.id, deliveryHeader)
        const lineResource = resourceApi('delivery-order-line', session.token)
        for (const line of lines) {
          if (line.id) await lineResource.update(line.id, line)
          else await lineResource.create({ ...line, delivery: saved.id })
        }
      }
      invalidateDeliveryLookups()
      setModal(false); setEditor(null); await loadConfig(active); setNotice(row?.id ? '已更新送货单' : '已创建送货单')
    } catch (requestError) { setError(requestError.message) }
  }
  const newSalesQuoteVersion = row => {
    const sourceLine = row.lines?.[0]
    setEditor({ ...row, id: undefined, number: undefined, status: 'draft', is_confirmed: false, is_ratified: false, lines: sourceLine ? [{ ...sourceLine, id: undefined }] : [] })
    setModal(true)
  }
  const removeRecord = async row => {
    if (!window.confirm(`确认删除${current.title} ${labelFor(row)}？`)) return
    try { await resourceApi(current.resource, session.token).remove(row.id); await loadConfig(active); setNotice(`已删除${current.title}`) }
    catch (requestError) { setError(requestError.message) }
  }
  const generatePayables = async values => {
    try {
      const generated = await api('/payable-voucher/auto-generate/', { token: session.token, method: 'POST', body: values })
      setPayableModal(false); await loadConfig(active); setNotice(`已生成 ${generated.length} 张应付凭单`)
    } catch (requestError) { setError(requestError.message) }
  }
  const convertRecord = async values => {
    try {
      await resourceApi(current.resource, session.token).action(conversionRow.id, 'convert', values)
      setConversionRow(null); await loadConfig(active)
      setNotice(current.convertKind === 'sales' ? '已生成销售订单' : '已生成采购单')
    } catch (requestError) { setError(requestError.message) }
  }
  const runSalesOrderWorkflow = async values => {
    try {
      const result = workflow.kind === 'mrp'
        ? await resourceApi('sales-order', session.token).action(workflow.row.id, 'generate-requisition', values)
        : workflow.kind === 'receipt'
          ? await resourceApi('purchase-order', session.token).action(workflow.row.id, 'generate-receipt', values)
          : await api('/delivery-order/generate-from-order/', { token: session.token, method: 'POST', body: { ...values, sales_order: workflow.row.id } })
      if (workflow.kind === 'delivery') invalidateDeliveryLookups()
      setWorkflow(null); await loadConfig(active)
      setNotice(workflow.kind === 'mrp' ? `已生成请购草稿 ${result.number}` : workflow.kind === 'receipt' ? `已生成收货草稿 ${result.number}` : `已生成送货草稿 ${result.number}`)
    } catch (requestError) { setError(requestError.message) }
  }
  const uploadAndConfirm = async ({ file, notes }) => {
    try {
      const formData = new FormData()
      formData.append('document_type', current.resource.replaceAll('-', ''))
      formData.append('document_id', evidenceRow.id)
      formData.append('document_number', evidenceRow.number || '')
      formData.append('evidence_type', current.evidenceType)
      formData.append('file', file)
      formData.append('notes', notes)
      await upload('/document-evidence/', formData, session.token)
      await resourceApi(current.resource, session.token).action(evidenceRow.id, 'confirm')
      setEvidenceRow(null); await loadConfig(active); setNotice('签收凭证已归档，单据已确认')
    } catch (requestError) { setError(requestError.message) }
  }
  const transition = async (row, action) => {
    try {
      await resourceApi(current.resource, session.token).action(row.id, action)
      if (current.resource === 'delivery-order') invalidateDeliveryLookups()
      await loadConfig(active)
      setNotice({ submit: '已提交审核', confirm: '报价已确认', unconfirm: '报价已反确认', approve: '报价已审核', unapprove: '报价已反审核', ratify: '报价已核准', unratify: '报价已反核准', 'sales-confirm': '报价已销售确认', 'sales-unconfirm': '报价已反销售确认' }[action] || '状态已更新')
    } catch (requestError) { setError(requestError.message) }
  }
  const exportRecords = async filtered => {
    try {
      const body = {
        ...(filtered ? { ids: filteredRows.map(row => row.id) } : {}),
        ...(current.partnerKind ? { partner_kind: current.partnerKind } : {}),
      }
      const file = await download(`/${current.resource}/export/`, { token: session.token, body })
      const url = URL.createObjectURL(file.blob)
      const link = document.createElement('a')
      link.href = url; link.download = file.filename; link.click()
      URL.revokeObjectURL(url)
      setNotice(`已导出${filtered ? filteredRows.length : rows.length}条${current.title}`)
    } catch (requestError) { setError(requestError.message) }
  }
  const filteredRows = useMemo(() => {
    const needle = query.trim().toLowerCase()
    return needle ? rows.filter(row => Object.values(row).some(value => displayValue(value).toLowerCase().includes(needle))) : rows
  }, [query, rows])

  if (!session) return <Login onLogin={next => { lookupCache.current.clear(); saveSession(next); setSession(next) }} />
  const CurrentIcon = current?.icon
  const activeModule = modules.find(module => module.items?.some(([id]) => id === active))
  const canCreate = current && (current.fields.length || current.resource === 'supplier-quote') && active !== 'payableVouchers' && can(session, current.permission, 'create')
  const canGeneratePayables = active === 'payableVouchers' && can(session, current.permission, 'create')
  const openEditor = () => {
    setError('')
    setModal(true)
    if (current?.resource === 'delivery-order') loadDeliveryLookups()
    if (current?.resource === 'sales-order') loadSalesOrderLookups()
  }
  const openDeliveryRecord = async row => {
    try {
      setError('')
      await loadDeliveryLookups()
      setEditor(await resourceApi('delivery-order', session.token).retrieve(row.id))
    } catch (requestError) { setError(requestError.message) }
  }
  const viewDeliveryRecord = async row => {
    try {
      setError('')
      setDetail(await resourceApi('delivery-order', session.token).retrieve(row.id))
    } catch (requestError) { setError(requestError.message) }
  }
  const openSalesOrderRecord = async row => {
    try { await loadSalesOrderLookups(); setEditor(await resourceApi('sales-order', session.token).retrieve(row.id)) }
    catch (requestError) { setError(requestError.message) }
  }
  const viewSalesOrderRecord = async row => {
    try { await loadSalesOrderLookups(); setDetail(await resourceApi('sales-order', session.token).retrieve(row.id)) }
    catch (requestError) { setError(requestError.message) }
  }

  return <div className="app-shell">
    <aside className={`sidebar ${mobileNav ? 'mobile-open' : ''}`}>
      <div className="brand"><div className="brand-mark"><Boxes size={17} /></div><div><strong>ERP</strong><span>企业资源管理系统</span></div></div>
      <div className="workspace-switch"><span className="workspace-dot" /> 制造运营中心 <ChevronDown size={14} /></div>
      <nav>{allowedModules.map(module => <div key={module.id}>
        <button className={`nav-parent ${active === module.id ? 'active' : ''}`} onClick={() => module.items ? setOpen(value => ({ ...value, [module.id]: !value[module.id] })) : select(module.id)}><module.icon size={17} /><span>{module.label}</span>{module.items ? <ChevronDown size={15} className={open[module.id] ? 'rotate' : ''} /> : null}</button>
        {module.items && open[module.id] ? <div className="subnav">{module.items.map(([id, label]) => <button key={id} className={active === id ? 'selected' : ''} onClick={() => select(id)}>{label}</button>)}</div> : null}
      </div>)}</nav>
      <div className="sidebar-bottom"><button><Settings size={16} />系统设置</button><button><CircleHelp size={16} />帮助中心</button><div className="user-chip"><div className="avatar">{session.username.slice(0, 1).toUpperCase()}</div><div><strong>{session.username}</strong><span>{session.roles?.join(' / ') || '已登录'}</span></div><button title="退出登录" aria-label="退出登录" onClick={logout}><LogOut size={16} /></button></div></div>
    </aside>
    {mobileNav ? <button className="nav-backdrop" aria-label="关闭导航" onClick={() => setMobileNav(false)} /> : null}
    {error && (modal || editor || detail || payableModal || conversionRow || workflow || evidenceRow) ? <div className="error-banner app-error-banner" role="alert"><span>{error}</span><button aria-label="关闭错误" onClick={() => setError('')}><X size={15} /></button></div> : null}
    <main className="main">
      <header className="topbar"><button className="icon-button mobile-menu" aria-label="打开导航" onClick={() => setMobileNav(true)}><Menu size={20} /></button><div className="crumb">{active === 'overview' ? '工作台' : <>{activeModule?.label}<span>/</span>{current.title}</>}</div><div className="top-actions">{active !== 'overview' ? <div className="search"><Search size={17} /><input aria-label="搜索当前列表" placeholder="搜索当前列表" value={query} onChange={event => setQuery(event.target.value)} /></div> : null}<button className="icon-button" title="通知" aria-label="通知"><Bell size={18} /></button><div className="top-user"><div className="avatar small">{session.username.slice(0, 1).toUpperCase()}</div></div></div></header>
      {active === 'overview' ? <Dashboard data={dashboard} modules={allowedModules} configs={configs} onSelect={select} loading={dashboardLoading} error={dashboardError} onRetry={loadDashboard} /> : active === 'materialImport' ? <><div className="page-head"><div className="title-wrap"><div className="title-icon"><CurrentIcon size={21} /></div><div><h1>{current.title}</h1><p>从原 ERP pt_mstr 模板预检后确认导入，编码按产品类自动连续分配</p></div></div></div><MaterialImport token={session.token} onNotice={setNotice} /></> : <>
        <div className="page-head"><div className="title-wrap"><div className="title-icon"><CurrentIcon size={21} /></div><div><h1>{current.title}</h1><p>{current.audited ? '草稿提交后进入审批，所有状态变化保留审计记录' : '按业务来源维护和查询明细记录'}</p></div></div><div className="head-actions"><button className="secondary" onClick={refresh} disabled={loading}><RefreshCw size={16} />刷新</button>{current.exportable ? <><button className="secondary export-button" onClick={() => exportRecords(true)} disabled={loading}><Download size={16} />导出当前</button><button className="secondary export-button" onClick={() => exportRecords(false)} disabled={loading}><Download size={16} />导出全部</button></> : null}{canGeneratePayables ? <button className="primary" onClick={() => setPayableModal(true)}><Coins size={17} />自动生成</button> : null}{canCreate ? <button className="primary" onClick={openEditor}><Plus size={16} />新增</button> : null}</div></div>
      <div className="content">{error && !modal && !editor ? <div className="error-banner">{error}<button aria-label="关闭错误" onClick={() => setError('')}><X size={15} /></button></div> : null}<div className="stats"><Stat label="全部记录" value={rows.length} /><Stat label="已审核" value={rows.filter(row => row.status === 'approved').length} tone="green" /><Stat label="待审核" value={rows.filter(row => row.status === 'pending').length} tone="orange" /><div className="permission-note"><ShieldCheck size={14} />{can(session, current.permission, 'create') ? '可操作' : '只读权限'}</div></div><div className="toolbar"><div className="view-tabs"><button className="active">列表</button></div><div className="tool-right"><button title="筛选"><Filter size={16} />筛选</button><button title="列设置"><SlidersHorizontal size={16} />列</button></div></div><ResourceTable rows={filteredRows} total={rows.length} config={current} session={session} lookups={lookups} onTransition={transition} onConvert={setConversionRow} onWorkflow={(row, kind) => setWorkflow({ row, kind })} onEvidence={setEvidenceRow} onView={row => current.resource === 'sales-order' ? viewSalesOrderRecord(row) : current.resource === 'delivery-order' ? viewDeliveryRecord(row) : setDetail(row)} onEdit={row => current.resource === 'sales-order' ? openSalesOrderRecord(row) : current.resource === 'delivery-order' ? openDeliveryRecord(row) : setEditor(row)} onNewVersion={newSalesQuoteVersion} onDelete={removeRecord} loading={loading} /></div>
      </>}
    </main>
    {modal || editor ? current.resource === 'material' ? <MaterialRecordModal config={current} lookups={lookups} record={editor} onClose={() => { setModal(false); setEditor(null) }} onSave={values => editor ? saveRecord(values, editor) : add(values)} /> : current.resource === 'customer-material' ? <CustomerMaterialModal lookups={lookups} record={editor} onClose={() => { setModal(false); setEditor(null) }} onSave={values => editor ? saveRecord(values, editor) : add(values)} /> : current.resource === 'sales-order' ? <SalesOrderModal key={`sales-order-${editor?.id || 'new'}`} token={session.token} lookups={lookups} record={editor} onClose={() => { setModal(false); setEditor(null) }} onSave={values => editor ? saveRecord(values, editor) : add(values)} onDelete={editor ? () => removeRecord(editor) : undefined} onAction={action => action === 'new' ? setEditor(null) : editor ? transition(editor, action) : undefined} /> : current.resource === 'delivery-order' ? <DeliveryOrderModal key={`delivery-order-${editor?.id || 'new'}`} lookups={lookups} record={editor} loading={deliveryLookupsLoading} error={error} onClearError={() => setError('')} onClose={() => { setModal(false); setEditor(null); setError('') }} onSave={values => saveDeliveryOrder(values, editor)} /> : current.resource === 'sales-quote' ? <SalesQuoteModal token={session.token} lookups={lookups} record={editor} onClose={() => { setModal(false); setEditor(null) }} onSave={values => editor ? saveRecord(values, editor) : add(values)} /> : current.resource === 'supplier-quote' ? <SupplierQuoteModal lookups={lookups} record={editor} onClose={() => { setModal(false); setEditor(null) }} onSave={values => editor ? saveRecord(values, editor) : add(values)} /> : <RecordModal config={current} lookups={lookups} record={editor} onClose={() => { setModal(false); setEditor(null) }} onSave={values => editor ? saveRecord(values, editor) : add(values)} /> : null}
    {detail ? current.resource === 'sales-order' ? <SalesOrderModal token={session.token} lookups={lookups} record={detail} readOnly onClose={() => setDetail(null)} /> : current.resource === 'sales-quote' ? <SalesQuoteModal token={session.token} lookups={lookups} record={detail} readOnly onClose={() => setDetail(null)} /> : current.resource === 'supplier-quote' ? <SupplierQuoteModal lookups={lookups} record={detail} readOnly onClose={() => setDetail(null)} /> : current.resource === 'delivery-order' ? <DeliveryOrderModal lookups={lookups} record={detail} loading={deliveryLookupsLoading} readOnly onClose={() => setDetail(null)} /> : <DetailModal config={current} row={detail} lookups={lookups} onClose={() => setDetail(null)} /> : null}
    {payableModal ? <PayableGenerateModal session={session} onClose={() => setPayableModal(false)} onSave={generatePayables} /> : null}
    {conversionRow ? <ConversionModal kind={current.convertKind} row={conversionRow} session={session} onClose={() => setConversionRow(null)} onSave={convertRecord} /> : null}
    {workflow ? <SalesOrderWorkflowModal workflow={workflow.kind} row={workflow.row} session={session} onClose={() => setWorkflow(null)} onSave={runSalesOrderWorkflow} /> : null}
    {evidenceRow ? <DocumentEvidenceModal row={evidenceRow} evidenceType={current.evidenceType} onClose={() => setEvidenceRow(null)} onSave={uploadAndConfirm} /> : null}
    {notice ? <div className="toast"><Check size={17} />{notice}<button aria-label="关闭通知" onClick={() => setNotice('')}><X size={15} /></button></div> : null}
  </div>
}


