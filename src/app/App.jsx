import { useDeferredValue, useMemo, useState } from 'react'
import {
  Bell,
  Boxes,
  Check,
  ChevronDown,
  CircleHelp,
  Coins,
  Download,
  Filter,
  LogOut,
  Menu,
  Plus,
  RefreshCw,
  Search,
  Settings,
  ShieldCheck,
  SlidersHorizontal,
  X
} from 'lucide-react'
import { api, download, resourceApi, upload } from '../api/client'
import { can, clearSession, readSession, saveSession } from '../auth/session'
import { Login } from '../auth/Login'
import { ResourceTable, Stat } from '../components/ResourceTable'
import { ConversionModal, DocumentEvidenceModal } from '../components/ResourceModals'
import { OrderWorkflowModal } from '../components/OrderWorkflowModal'
import { PayableGenerateModal } from '../modules/finance/PayableGenerateModal'
import { Dashboard } from '../modules/dashboard/Dashboard'
import { MaterialImport } from '../modules/purchase/MaterialImport'
import { displayValue, labelFor } from '../shared/presentation'
import { modules } from './navigation'
import { configs } from './configs'
import { useResourceData } from './useResourceData'
import { ResourceModal } from './ResourceModal'
import { PendingButton } from '../components/PendingControls'
import { WarehouseWorkspace } from '../modules/inventory/WarehouseWorkspace'
import { InventoryLedger } from '../modules/inventory/InventoryLedger'
import { InventoryAnalysis } from '../modules/inventory/InventoryAnalysis'
import { SupplierWorkspace } from '../modules/purchase/SupplierWorkspace'
import { ConversionWorkspace } from '../modules/purchase/ConversionWorkspace'
import { PurchaseOrderWorkspace } from '../modules/purchase/PurchaseOrderWorkspace'
import { RequisitionWorkspace } from '../modules/purchase/RequisitionWorkspace'
import { ReceivingWorkspace } from '../modules/purchase/ReceivingWorkspace'
import { MaterialWorkspace } from '../modules/master-data/MaterialWorkspace'
import { NoOrderReturnWorkspace } from '../modules/sales/NoOrderReturnWorkspace'
import { TradeMrpWorkspace } from '../modules/purchase/TradeMrpWorkspace'

export default function App() {
  const [session, setSession] = useState(readSession)
  const [active, setActive] = useState('overview')
  const [purchaseOrderId, setPurchaseOrderId] = useState(null)
  const [requisitionId, setRequisitionId] = useState(null)
  const [open, setOpen] = useState({})
  const [query, setQuery] = useState('')
  const deferredQuery = useDeferredValue(query)
  const [modal, setModal] = useState(false)
  const [editor, setEditor] = useState(null)
  const [detail, setDetail] = useState(null)
  const [payableModal, setPayableModal] = useState(false)
  const [conversionRow, setConversionRow] = useState(null)
  const [workflow, setWorkflow] = useState(null)
  const [evidenceRow, setEvidenceRow] = useState(null)
  const [notice, setNotice] = useState('')
  const [mobileNav, setMobileNav] = useState(false)
  const current = configs[active]
  const {
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
    resetData,
    pagination, loadPage, loadEditorLookups
  } = useResourceData(session, active, deferredQuery)

  const allowedModules = useMemo(
    () =>
      modules
        .map((module) =>
          module.items
            ? {
                ...module,
                items: module.items.filter(([id]) => can(session, configs[id].permission))
              }
            : module
        )
        .filter((module) => !module.items || module.items.length),
    [session]
  )

  const select = (id) => {
    if (id === active) { setMobileNav(false); return }
    setActive(id)
    setQuery('')
    setNotice('')
    setMobileNav(false)
    resetPage(id)
  }
  const logout = () => {
    clearSession()
    resetData()
    setSession(null)
  }
  const refresh = () =>
    active === 'overview' ? loadDashboard() : active === 'materialImport' ? undefined : loadConfig(active)
  const saveRecord = async (values, row) => {
    const payload = Object.fromEntries(
      Object.entries(values).filter(([, value]) => value !== '' && value !== undefined)
    )
    try {
      const resource = resourceApi(current.resource, session.token)
      await (row?.id ? resource.update(row.id, payload) : resource.create(payload))
      invalidateLookup(current.resource)
      setModal(false)
      setEditor(null)
      await loadConfig(active)
      setNotice(row?.id ? `已更新${current.title}` : `已创建${current.title}`)
    } catch (requestError) {
      setError(requestError.message)
    }
  }
  const saveDeliveryOrder = async (values, row) => {
    await api(row?.id ? '/delivery-order/' + row.id + '/save-sheet/' : '/delivery-order/save-sheet/', {
      token: session.token,
      method: 'POST',
      body: values
    })
    invalidateDeliveryLookups()
    invalidateLookup('sales-order')
    invalidateLookup('sales-order-line')
    setModal(false)
    setEditor(null)
    await loadConfig(active)
    setNotice(row?.id ? '已更新送货单' : '已创建送货单')
  }
  const newSalesQuoteVersion = (row) => {
    const sourceLine = row.lines?.[0]
    setEditor({
      ...row,
      id: undefined,
      number: undefined,
      status: 'draft',
      is_confirmed: false,
      is_ratified: false,
      lines: sourceLine ? [{ ...sourceLine, id: undefined }] : []
    })
    loadEditorLookups('salesQuotes').catch(error => setError(error.message))
    setModal(true)
  }
  const removeRecord = async (row) => {
    if (!window.confirm(`确认删除${current.title} ${labelFor(row)}？`)) return
    try {
      await resourceApi(current.resource, session.token).remove(row.id)
      invalidateLookup(current.resource)
      if (editor?.id === row.id) {
        setEditor(null)
        setModal(false)
      }
      await loadConfig(active)
      setNotice(`已删除${current.title}`)
    } catch (requestError) {
      setError(requestError.message)
    }
  }
  const generatePayables = async (values) => {
    try {
      const generated = await api('/payable-voucher/auto-generate/', {
        token: session.token,
        method: 'POST',
        body: values
      })
      setPayableModal(false)
      await loadConfig(active)
      setNotice(`已生成 ${generated.length} 张应付凭单`)
    } catch (requestError) {
      setError(requestError.message)
    }
  }
  const convertRecord = async (values) => {
    try {
      await resourceApi(current.resource, session.token).action(conversionRow.id, 'convert', values)
      setConversionRow(null)
      await loadConfig(active)
      setNotice(current.convertKind === 'sales' ? '已生成销售订单' : '已生成采购单')
    } catch (requestError) {
      setError(requestError.message)
    }
  }
  const runSalesOrderWorkflow = async (values) => {
    try {
      const result =
        workflow.kind === 'mrp'
          ? await resourceApi('sales-order', session.token).action(workflow.row.id, 'generate-requisition', values)
          : workflow.kind === 'receipt'
            ? await resourceApi('purchase-order', session.token).action(workflow.row.id, 'generate-receipt', values)
            : await api('/delivery-order/generate-from-order/', {
                token: session.token,
                method: 'POST',
                body: { ...values, sales_order: workflow.row.id }
              })
      if (workflow.kind === 'delivery') invalidateDeliveryLookups()
      setWorkflow(null)
      await loadConfig(active)
      setNotice(
        workflow.kind === 'mrp'
          ? `已生成请购草稿 ${result.number}`
          : workflow.kind === 'receipt'
            ? `已生成收货草稿 ${result.number}`
            : `已生成送货草稿 ${result.number}`
      )
    } catch (requestError) {
      setError(requestError.message)
    }
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
      setEvidenceRow(null)
      await loadConfig(active)
      setNotice('签收凭证已归档，单据已确认')
    } catch (requestError) {
      setError(requestError.message)
    }
  }
  const transition = async (row, action) => {
    if (current.resource === 'delivery-order' && action === 'void' && !window.confirm(`作废送货单 ${row.number} 并释放订单数量占用？单号和记录将保留。`)) return
    try {
      await resourceApi(current.resource, session.token).action(row.id, action)
      invalidateLookup(current.resource)
      if (editor?.id === row.id) {
        setEditor(null)
        setModal(false)
      }
      if (current.resource === 'delivery-order') invalidateDeliveryLookups()
      await loadConfig(active)
      setNotice(
        {
          submit: '已提交审核',
          confirm: '报价已确认',
          unconfirm: current.resource === 'delivery-order' ? '送货单已取消回单确认' : '报价已反确认',
          approve: current.resource === 'delivery-order' ? '送货单已审核' : '报价已审核',
          unapprove: current.resource === 'delivery-order' ? '送货单已反审核，请编辑原单修正库位' : '报价已反审核',
          void: '单据已作废，数量占用已释放',
          ratify: '报价已核准',
          unratify: '报价已反核准',
          'sales-confirm': '报价已销售确认',
          'sales-unconfirm': '报价已反销售确认'
        }[action] || '状态已更新'
      )
    } catch (requestError) {
      setError(requestError.message)
    }
  }
  const exportRecords = async (filtered) => {
    try {
      const body = {
        ...(filtered ? (pagination ? { filters: { q: deferredQuery.trim() } } : { ids: filteredRows.map((row) => row.id) }) : {}),
        ...(current.partnerKind ? { partner_kind: current.partnerKind } : {})
      }
      const file = await download(`/${current.resource}/export/`, { token: session.token, body })
      const url = URL.createObjectURL(file.blob)
      const link = document.createElement('a')
      link.href = url
      link.download = file.filename
      link.click()
      URL.revokeObjectURL(url)
      setNotice(`已导出${filtered ? filteredRows.length : rows.length}条${current.title}`)
    } catch (requestError) {
      setError(requestError.message)
    }
  }
  const filteredRows = useMemo(() => {
    if (pagination) return rows
    const needle = deferredQuery.trim().toLowerCase()
    return needle
      ? rows.filter((row) => Object.values(row).some((value) => displayValue(value).toLowerCase().includes(needle)))
      : rows
  }, [deferredQuery, rows, pagination])

  if (!session)
    return (
      <Login
        onLogin={(next) => {
          resetData()
          saveSession(next)
          setSession(next)
        }}
      />
    )
  const CurrentIcon = current?.icon
  const activeModule = modules.find((module) => module.items?.some(([id]) => id === active))
  const canCreate =
    current &&
    (current.fields.length || current.resource === 'supplier-quote') &&
      active !== 'payableVouchers' &&
      !(['currency', 'currency-rate'].includes(current.resource) && [...rows, ...(lookups.currencies || [])].some(row => row.source_object?.startsWith('dgyzx1.'))) &&
    can(session, current.permission, 'create')
  const canGeneratePayables = active === 'payableVouchers' && can(session, current.permission, 'create')
  const openEditor = () => {
    setError('')
    setNotice('')
    setModal(true)
    if (pagination) loadEditorLookups(active).catch(error => setError(error.message))
    if (current?.resource === 'delivery-order') loadDeliveryLookups()
    if (current?.resource === 'sales-order') loadSalesOrderLookups()
  }
  const openDeliveryRecord = async (row) => {
    try {
      setError('')
      setNotice('')
      await loadDeliveryLookups()
      setEditor(await resourceApi('delivery-order', session.token).retrieve(row.id))
    } catch (requestError) {
      setError(requestError.message)
    }
  }
  const viewDeliveryRecord = async (row) => {
    try {
      setError('')
      setNotice('')
      setDetail(await resourceApi('delivery-order', session.token).retrieve(row.id))
    } catch (requestError) {
      setError(requestError.message)
    }
  }
  const loadSalesOrderRecord = async (row, showRecord) => {
    try {
      await loadSalesOrderLookups()
      showRecord(await resourceApi('sales-order', session.token).retrieve(row.id))
    } catch (requestError) {
      setError(requestError.message)
    }
  }
  const openSalesOrderRecord = (row) => loadSalesOrderRecord(row, setEditor)
  const viewSalesOrderRecord = (row) => loadSalesOrderRecord(row, setDetail)

  return (
    <div className="app-shell">
      <aside className={`sidebar ${mobileNav ? 'mobile-open' : ''}`}>
        <div className="brand">
          <div className="brand-mark">
            <Boxes size={17} />
          </div>
          <div>
            <strong>ERP</strong>
            <span>企业资源管理系统</span>
          </div>
        </div>
        <div className="workspace-switch">
          <span className="workspace-dot" /> 制造运营中心 <ChevronDown size={14} />
        </div>
        <nav>
          {allowedModules.map((module) => (
            <div key={module.id}>
              <button
                className={`nav-parent ${active === module.id ? 'active' : ''}`}
                onClick={() =>
                  module.items ? setOpen((value) => ({ ...value, [module.id]: !value[module.id] })) : select(module.id)
                }
              >
                <module.icon size={17} />
                <span>{module.label}</span>
                {module.items ? <ChevronDown size={15} className={open[module.id] ? 'rotate' : ''} /> : null}
              </button>
              {module.items && open[module.id] ? (
                <div className="subnav">
                  {module.items.map(([id, label]) => (
                    <button key={id} className={active === id ? 'selected' : ''} onClick={() => select(id)}>
                      {label}
                    </button>
                  ))}
                </div>
              ) : null}
            </div>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <button>
            <Settings size={16} />
            系统设置
          </button>
          <button>
            <CircleHelp size={16} />
            帮助中心
          </button>
          <div className="user-chip">
            <div className="avatar">{session.username.slice(0, 1).toUpperCase()}</div>
            <div>
              <strong>{session.username}</strong>
              <span>{session.roles?.join(' / ') || '已登录'}</span>
            </div>
            <button title="退出登录" aria-label="退出登录" onClick={logout}>
              <LogOut size={16} />
            </button>
          </div>
        </div>
      </aside>
      {mobileNav ? <button className="nav-backdrop" aria-label="关闭导航" onClick={() => setMobileNav(false)} /> : null}
      {error && (modal || editor || detail || payableModal || conversionRow || workflow || evidenceRow) ? (
        <div className="error-banner app-error-banner" role="alert">
          <span>{error}</span>
          <button aria-label="关闭错误" onClick={() => setError('')}>
            <X size={15} />
          </button>
        </div>
      ) : null}
      <main className="main">
        <header className="topbar">
          <button className="icon-button mobile-menu" aria-label="打开导航" onClick={() => setMobileNav(true)}>
            <Menu size={20} />
          </button>
          <div className="crumb">
            {active === 'overview' ? (
              '工作台'
            ) : (
              <>
                {activeModule?.label}
                <span>/</span>
                {current.title}
              </>
            )}
          </div>
          <div className="top-actions">
            {active !== 'overview' ? (
              <div className="search">
                <Search size={17} />
                <input
                  aria-label="搜索当前列表"
                  placeholder="搜索当前列表"
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                />
              </div>
            ) : null}
            <button className="icon-button" title="通知" aria-label="通知">
              <Bell size={18} />
            </button>
            <div className="top-user">
              <div className="avatar small">{session.username.slice(0, 1).toUpperCase()}</div>
            </div>
          </div>
        </header>
        {active === 'overview' ? (
          <Dashboard
            data={dashboard}
            modules={allowedModules}
            configs={configs}
            onSelect={select}
            loading={dashboardLoading}
            error={dashboardError}
            onRetry={loadDashboard}
          />
        ) : current?.inventoryAnalysis ? (
          <InventoryAnalysis key={active} monthly={current.inventoryAnalysis === 'monthly'} title={current.title} session={session} />
        ) : current?.inventoryLedger || ['balances', 'transactions'].includes(active) ? (
          <InventoryLedger key={active} resource={current.resource} title={current.title} session={session} onClose={() => setActive('overview')} />
        ) : current?.warehouseKind ? (
          <WarehouseWorkspace key={active} kind={current.warehouseKind} initialCount={current.initialCount} title={current.title} session={session} />
        ) : active === 'tradeMrp' ? (
          <TradeMrpWorkspace session={session} onClose={() => select('overview')} onOpenRequisition={id => { setRequisitionId(id); select('requisitions') }} />
        ) : active === 'noOrderReturns' ? (
          <NoOrderReturnWorkspace session={session} />
        ) : active === 'requisitionConvert' ? (
          <ConversionWorkspace session={session} onClose={() => select('overview')} onOpenOrder={id => { setPurchaseOrderId(id); select('purchaseOrders') }} />
        ) : active === 'purchaseOrders' ? (
          <PurchaseOrderWorkspace session={session} initialId={purchaseOrderId} onClose={() => { setPurchaseOrderId(null); select('overview') }} />
        ) : active === 'receipts' || active === 'purchaseReturns' ? (
          <ReceivingWorkspace key={active} session={session} returning={active === 'purchaseReturns'} onOpenOrder={id => { setPurchaseOrderId(id); select('purchaseOrders') }} onClose={() => select('overview')} />
        ) : active === 'requisitions' ? (
          <RequisitionWorkspace session={session} initialId={requisitionId} />
        ) : active === 'suppliers' || active === 'supplierQuotes' ? (
          <SupplierWorkspace key={active} mode={active === 'supplierQuotes' ? 'quote' : 'supplier'} session={session} />
        ) : active === 'materials' ? (
          <MaterialWorkspace key="materials" session={session} />
        ) : active === 'materialImport' ? (
          <>
            <div className="page-head">
              <div className="title-wrap">
                <div className="title-icon">
                  <CurrentIcon size={21} />
                </div>
                <div>
                  <h1>{current.title}</h1>
                  <p>从原 ERP pt_mstr 模板预检后确认导入，编码按产品类自动连续分配</p>
                </div>
              </div>
            </div>
            <MaterialImport token={session.token} onNotice={setNotice} />
          </>
        ) : (
          <>
            <div className="page-head">
              <div className="title-wrap">
                <div className="title-icon">
                  <CurrentIcon size={21} />
                </div>
                <div>
                  <h1>{current.title}</h1>
                  <p>
                    {current.audited ? '草稿提交后进入审批，所有状态变化保留审计记录' : '按业务来源维护和查询明细记录'}
                  </p>
                </div>
              </div>
              <div className="head-actions">
                <button className="secondary" onClick={refresh} disabled={loading}>
                  <RefreshCw size={16} />
                  刷新
                </button>
                {current.exportable ? (
                  <>
                    <PendingButton className="secondary export-button" onClick={() => exportRecords(true)} disabled={loading}>
                      <Download size={16} />
                      导出当前
                    </PendingButton>
                    <PendingButton className="secondary export-button" onClick={() => exportRecords(false)} disabled={loading}>
                      <Download size={16} />
                      导出全部
                    </PendingButton>
                  </>
                ) : null}
                {canGeneratePayables ? (
                  <button className="primary" onClick={() => setPayableModal(true)}>
                    <Coins size={17} />
                    自动生成
                  </button>
                ) : null}
                {canCreate ? (
                  <button className="primary" onClick={openEditor}>
                    <Plus size={16} />
                    新增
                  </button>
                ) : null}
              </div>
            </div>
            <div className="content">
              {error && !modal && !editor ? (
                <div className="error-banner">
                  {error}
                  <button aria-label="关闭错误" onClick={() => setError('')}>
                    <X size={15} />
                  </button>
                </div>
              ) : null}
              <div className="stats">
                <Stat label="全部记录" value={rows.length} />
                <Stat label="已审核" value={rows.filter((row) => row.status === 'approved').length} tone="green" />
                <Stat label="待审核" value={rows.filter((row) => row.status === 'pending').length} tone="orange" />
                <div className="permission-note">
                  <ShieldCheck size={14} />
                  {can(session, current.permission, 'create') ? '可操作' : '只读权限'}
                </div>
              </div>
              <div className="toolbar">
                <div className="view-tabs">
                  <button className="active">列表</button>
                </div>
                <div className="tool-right">
                  <button title="筛选">
                    <Filter size={16} />
                    筛选
                  </button>
                  <button title="列设置">
                    <SlidersHorizontal size={16} />列
                  </button>
                </div>
              </div>
              <ResourceTable
                key={`${active}-${deferredQuery}`}
                rows={filteredRows}
                total={pagination?.count ?? rows.length}
                pagination={pagination}
                onPageChange={pagination ? page => loadPage(active, page) : undefined}
                config={current}
                session={session}
                lookups={lookups}
                onTransition={transition}
                onConvert={setConversionRow}
                onWorkflow={(row, kind) => kind === 'mrp' ? select('tradeMrp') : setWorkflow({ row, kind })}
                onEvidence={setEvidenceRow}
                onView={(row) =>
                  current.resource === 'sales-order'
                    ? viewSalesOrderRecord(row)
                    : current.resource === 'delivery-order'
                      ? viewDeliveryRecord(row)
                      : (loadEditorLookups(active).catch(error => setError(error.message)), setDetail(row))
                }
                onEdit={(row) =>
                  current.resource === 'sales-order'
                    ? openSalesOrderRecord(row)
                    : current.resource === 'delivery-order'
                      ? openDeliveryRecord(row)
                      : (loadEditorLookups(active).catch(error => setError(error.message)), setEditor(row))
                }
                onNewVersion={newSalesQuoteVersion}
                onDelete={removeRecord}
                loading={loading}
              />
            </div>
          </>
        )}
      </main>
      {modal || editor ? (
        <ResourceModal
          key={`${current.resource}-${editor?.id || 'new'}`}
          config={current}
          record={editor}
          token={session.token}
          lookups={lookups}
          loading={deliveryLookupsLoading}
          error={error}
          onClearError={() => setError('')}
          onClose={() => {
            setModal(false)
            setEditor(null)
            setError('')
          }}
          onSave={(values) =>
            current.resource === 'delivery-order' ? saveDeliveryOrder(values, editor) : saveRecord(values, editor)
          }
          onDelete={editor ? () => removeRecord(editor) : undefined}
          onAction={(action) => (action === 'new' ? setEditor(null) : editor ? transition(editor, action) : undefined)}
        />
      ) : null}
      {detail ? (
        <ResourceModal
          config={current}
          record={detail}
          token={session.token}
          lookups={lookups}
          loading={deliveryLookupsLoading}
          readOnly
          onClose={() => setDetail(null)}
        />
      ) : null}
      {payableModal ? (
        <PayableGenerateModal session={session} onClose={() => setPayableModal(false)} onSave={generatePayables} />
      ) : null}
      {conversionRow ? (
        <ConversionModal
          kind={current.convertKind}
          row={conversionRow}
          session={session}
          onClose={() => setConversionRow(null)}
          onSave={convertRecord}
        />
      ) : null}
      {workflow ? (
        <OrderWorkflowModal
          workflow={workflow.kind}
          row={workflow.row}
          session={session}
          onClose={() => setWorkflow(null)}
          onSave={runSalesOrderWorkflow}
        />
      ) : null}
      {evidenceRow ? (
        <DocumentEvidenceModal
          row={evidenceRow}
          evidenceType={current.evidenceType}
          onClose={() => setEvidenceRow(null)}
          onSave={uploadAndConfirm}
        />
      ) : null}
      {notice ? (
        <div className="toast">
          <Check size={17} />
          {notice}
          <button aria-label="关闭通知" onClick={() => setNotice('')}>
            <X size={15} />
          </button>
        </div>
      ) : null}
    </div>
  )
}
