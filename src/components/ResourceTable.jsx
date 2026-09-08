import { ArrowUpRight, BadgeCheck, CheckCheck, ClipboardList, FileSearch, PackageCheck, Paperclip, RotateCcw, Send, Settings, ShieldCheck, Truck, X } from 'lucide-react'
import { PendingButton } from './PendingControls'
import { can } from '../auth/session'
import { displayValue, relatedLabel, statusLabels } from '../shared/presentation'

export function Stat({ label, value, tone = '' }) {
  return <div className={`stat ${tone}`}><div className={`stat-mark ${tone}`} /><div><span>{label}</span><strong>{value}</strong></div></div>
}

function Status({ value }) {
  const tone = value === 'approved' ? 'green' : value === 'pending' ? 'orange' : ''
  return <span className={`status ${tone}`}><i />{statusLabels[value] || value}</span>
}

export function ResourceTable({ rows, total, config: cfg, session, lookups, onTransition, onConvert, onWorkflow, onEvidence, onView, onEdit, onNewVersion, onDelete, loading }) {
  const actionColumn = cfg.audited || can(session, cfg.permission, 'change') || can(session, cfg.permission, 'delete')
  const columnCount = cfg.columns.length + (actionColumn ? 1 : 0)
  return <div className="table-card"><table><thead><tr>{cfg.columns.map(([, label]) => <th key={label}>{label}</th>)}{actionColumn ? <th>操作</th> : null}</tr></thead><tbody>{loading ? <tr><td className="table-loading" colSpan={columnCount}>正在加载</td></tr> : rows.map(row => <tr key={row.id}>{cfg.columns.map(([key]) => { const field = cfg.fields.find(item => item.key === key); const value = key === 'quote_type' ? ({ purchase: '采购报价', outsource: '外协报价' }[row[key]] || row[key]) : row[key]; return <td key={key}>{key === 'status' ? <Status value={value} /> : key === 'code' || key === 'number' ? <strong className="code">{displayValue(value)}</strong> : relatedLabel(value, field, lookups)}</td> })}{actionColumn ? <RowActions key="actions" row={row} cfg={cfg} session={session} onTransition={onTransition} onConvert={onConvert} onWorkflow={onWorkflow} onEvidence={onEvidence} onView={onView} onEdit={onEdit} onNewVersion={onNewVersion} onDelete={onDelete} /> : null}</tr>)}</tbody></table>{!loading && rows.length === 0 ? <div className="empty">暂无记录</div> : null}<div className="table-foot">显示 {rows.length} 条，共 {total} 条记录</div></div>
}

function RowActions({ row, cfg, session, onTransition, onConvert, onWorkflow, onEvidence, onView, onEdit, onNewVersion, onDelete }) {
  const editable = !cfg.audited || ['draft', 'rejected'].includes(row.status)
  return <td className="row-actions">
    <PendingButton title="查看" aria-label="查看" onClick={() => onView(row)}><FileSearch size={15} /></PendingButton>
    {cfg.resource === 'sales-quote' && row.is_ratified && can(session, cfg.permission, 'create') ? <PendingButton title="新版本报价" aria-label="新版本报价" onClick={() => onNewVersion(row)}><ClipboardList size={15} /></PendingButton> : null}
    {can(session, cfg.permission, 'change') && editable ? <PendingButton title="编辑" aria-label="编辑" onClick={() => onEdit(row)}><Settings size={15} /></PendingButton> : null}
    {can(session, cfg.permission, 'delete') && editable ? <PendingButton title="删除" aria-label="删除" onClick={() => onDelete(row)}><X size={15} /></PendingButton> : null}
    {cfg.quoteWorkflow ? <QuoteActions row={row} session={session} permission={cfg.permission} onTransition={onTransition} supplierQuote={cfg.resource === 'supplier-quote'} /> : null}
    {!cfg.quoteWorkflow && cfg.audited && row.status === 'draft' && can(session, cfg.permission, 'submit') ? <PendingButton title="提交审核" aria-label="提交审核" onClick={() => onTransition(row, 'submit')}><Send size={15} /></PendingButton> : null}
    {!cfg.quoteWorkflow && cfg.audited && row.status === 'rejected' && can(session, cfg.permission, 'submit') ? <PendingButton title="提交审核" aria-label="提交审核" onClick={() => onTransition(row, 'submit')}><Send size={15} /></PendingButton> : null}
    {!cfg.quoteWorkflow && cfg.audited && row.status === 'pending' && can(session, cfg.permission, 'approve') ? <PendingButton title="审核" aria-label="审核" onClick={() => onTransition(row, 'approve')}><BadgeCheck size={16} /></PendingButton> : null}
    {!cfg.quoteWorkflow && cfg.audited && row.status === 'approved' && can(session, cfg.permission, 'approve') ? <PendingButton title="反审核" aria-label="反审核" onClick={() => onTransition(row, 'unapprove')}><RotateCcw size={15} /></PendingButton> : null}
    {cfg.audited && row.status === 'approved' && cfg.requiresConfirmation && !row.is_confirmed && can(session, cfg.permission, 'approve') ? <PendingButton title="上传签收凭证并确认" aria-label="上传签收凭证并确认" onClick={() => onEvidence(row)}><Paperclip size={16} /></PendingButton> : null}
    {cfg.audited && row.status === 'approved' && cfg.workflowActions?.includes('mrp') && can(session, 'purchase_requisition', 'create') ? <PendingButton title="生成 MRP 请购" aria-label="生成 MRP 请购" onClick={() => onWorkflow(row, 'mrp')}><ClipboardList size={16} /></PendingButton> : null}
    {cfg.audited && row.status === 'approved' && cfg.workflowActions?.includes('delivery') && can(session, 'delivery_order', 'create') ? <PendingButton title="生成送货草稿" aria-label="生成送货草稿" onClick={() => onWorkflow(row, 'delivery')}><PackageCheck size={16} /></PendingButton> : null}
    {cfg.audited && row.status === 'approved' && cfg.workflowActions?.includes('receipt') && can(session, 'goods_receipt', 'create') ? <PendingButton title="生成收货草稿" aria-label="生成收货草稿" onClick={() => onWorkflow(row, 'receipt')}><Truck size={16} /></PendingButton> : null}
    {cfg.audited && row.status === 'approved' && (!cfg.quoteWorkflow || row.is_ratified) && cfg.convertKind && can(session, cfg.convertPermission, 'create') ? <PendingButton title="转换下游单据" aria-label="转换下游单据" onClick={() => onConvert(row)}><ArrowUpRight size={16} /></PendingButton> : null}
  </td>
}

function QuoteActions({ row, session, permission, onTransition, supplierQuote }) {
  if (['draft', 'rejected'].includes(row.status) && can(session, permission, 'confirm')) return <PendingButton title="确认报价" aria-label="确认报价" onClick={() => onTransition(row, 'confirm')}><CheckCheck size={16} /></PendingButton>
  if (row.status === 'pending') return <><PendingButton title="反确认" aria-label="反确认" disabled={!can(session, permission, 'confirm')} onClick={() => onTransition(row, 'unconfirm')}><RotateCcw size={15} /></PendingButton>{can(session, permission, 'approve') ? <PendingButton title="审核报价" aria-label="审核报价" onClick={() => onTransition(row, 'approve')}><BadgeCheck size={16} /></PendingButton> : null}</>
  if (row.status === 'approved' && !row.is_ratified) return <>{can(session, permission, 'approve') ? <PendingButton title="反审核" aria-label="反审核" onClick={() => onTransition(row, 'unapprove')}><RotateCcw size={15} /></PendingButton> : null}{can(session, permission, 'ratify') ? <PendingButton title="核准报价" aria-label="核准报价" onClick={() => onTransition(row, 'ratify')}><ShieldCheck size={16} /></PendingButton> : null}</>
  if (row.is_ratified && supplierQuote && !row.is_sales_confirmed && can(session, permission, 'approve')) return <><PendingButton title="销售确认" aria-label="销售确认" onClick={() => onTransition(row, 'sales-confirm')}><CheckCheck size={16} /></PendingButton>{can(session, permission, 'ratify') ? <PendingButton title="反核准" aria-label="反核准" onClick={() => onTransition(row, 'unratify')}><RotateCcw size={15} /></PendingButton> : null}</>
  if (row.is_ratified && supplierQuote && row.is_sales_confirmed && can(session, permission, 'approve')) return <PendingButton title="反销售确认" aria-label="反销售确认" onClick={() => onTransition(row, 'sales-unconfirm')}><RotateCcw size={15} /></PendingButton>
  if (row.is_ratified && can(session, permission, 'ratify')) return <PendingButton title="反核准" aria-label="反核准" onClick={() => onTransition(row, 'unratify')}><RotateCcw size={15} /></PendingButton>
  return null
}
