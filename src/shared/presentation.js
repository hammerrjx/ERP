export const statusLabels = { draft: '草稿', pending: '待审核', approved: '已审核', rejected: '已驳回', void: '已作废' }
export const documentTypeLabels = { normal: '正常送货', return: '正常退货', red_flush: '红冲单据' }

export const today = () => new Intl.DateTimeFormat('en-CA', {
  timeZone: 'Asia/Shanghai', year: 'numeric', month: '2-digit', day: '2-digit'
}).format(new Date())
export const formatQuantity = value => Number(value || 0).toLocaleString('zh-CN', { maximumFractionDigits: 8 })

export function labelFor(row) {
  return row?.code || row?.number || row?.username || row?.name || row?.material_code || `#${row?.id}`
}

export function displayValue(value) {
  if (value === true) return '是'
  if (value === false) return '否'
  if (value == null) return ''
  return statusLabels[value] || documentTypeLabels[value] || String(value)
}

export function formatDateTime(value) {
  if (!value) return ''
  const match = String(value).match(/^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2}):(\d{2})/)
  return match ? `${match[1]}/${match[2]}/${match[3]} ${match[4]}:${match[5]}:${match[6]}` : String(value)
}

export function relatedLabel(value, field, lookups) {
  if (!field?.lookup || value == null) return displayValue(value)
  const row = (lookups[field.lookup] || []).find(option => option.id === Number(value))
  return row ? labelFor(row) : displayValue(value)
}
