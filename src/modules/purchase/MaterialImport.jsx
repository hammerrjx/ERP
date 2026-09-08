import React, { useState } from 'react'
import { Check, FileSpreadsheet, RefreshCw, Upload, X } from 'lucide-react'

import { api, upload } from '../../api/client'

export function MaterialImport({ token, onNotice }) {
  const [file, setFile] = useState(null)
  const [defaultTaxCode, setDefaultTaxCode] = useState('')
  const [batch, setBatch] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const preview = async selectedFile => {
    if (!selectedFile) return
    setBatch(null)
    setFile(selectedFile)
    setLoading(true); setError('')
    try {
      const form = new FormData()
      form.append('file', selectedFile)
      form.append('default_tax_code', defaultTaxCode.trim())
      setBatch(await upload('/material-import/preview/', form, token))
    } catch (requestError) { setError(requestError.message) } finally { setLoading(false) }
  }

  const confirm = async () => {
    setLoading(true); setError('')
    try {
      const result = await api(`/material-import/${batch.id}/confirm/`, { token, method: 'POST', body: {} })
      setBatch(result); onNotice(`已导入 ${result.imported_rows} 条物料信息`)
    } catch (requestError) { setError(requestError.message) } finally { setLoading(false) }
  }

  const reset = () => { setFile(null); setBatch(null); setError(''); setDefaultTaxCode('') }
  const canConfirm = batch?.status === 'preview' && batch.error_rows === 0 && batch.valid_rows > 0

  return <div className="content material-import">
    <div className="import-upload">
      <div className="import-file-icon"><FileSpreadsheet size={24} /></div>
      <div className="import-file-field"><strong>物料信息导入模板</strong><span>{file ? file.name : '选择原 ERP 的 pt_mstr .xls 或 .xlsx 文件'}</span><input type="file" accept=".xls,.xlsx" disabled={loading} onChange={event => { const selectedFile = event.target.files?.[0]; event.target.value = ''; preview(selectedFile) }} /></div>
      <label className="import-tax">默认税务编码<input value={defaultTaxCode} onChange={event => setDefaultTaxCode(event.target.value)} placeholder="模板未填写时使用" /></label>
      <div className="import-auto-preview">{loading ? <><RefreshCw className="spin" size={16} />正在预检</> : <><Upload size={16} />选择文件后自动预检</>}</div>
    </div>
    {error ? <div className="error-banner">{error}<button aria-label="关闭错误" onClick={() => setError('')}><X size={15} /></button></div> : null}
    {batch ? <>
      <div className="stats import-stats"><Stat label="读取行数" value={batch.total_rows} /><Stat label="可导入" value={batch.valid_rows} tone="green" /><Stat label="错误行" value={batch.error_rows} tone={batch.error_rows ? 'orange' : 'green'} /><div className="permission-note">{batch.status === 'imported' ? <><Check size={14} />已确认导入</> : batch.import_profile ? `当前主体：${batch.import_profile.company_name}（${batch.import_profile.company_code}）` : '未配置导入主体，无法确认'}</div></div>
      {batch.import_profile ? <div className="import-profile-note">单主体模式：原 ERP 的 <code>{batch.import_profile.source_company_column}</code> 列填写 Y 时显式选择；留空则自动归属当前主体。其他主体列或多个主体列会被拦截，原始列仍保留用于追溯。</div> : null}
      <div className="toolbar"><div className="view-tabs"><button className="active">预检明细</button></div><div className="tool-right"><button onClick={reset} disabled={loading}><RefreshCw size={16} />重新选择</button>{canConfirm ? <button className="primary" onClick={confirm} disabled={loading}><Check size={16} />确认导入</button> : null}</div></div>
      <div className="table-card import-result"><table><thead><tr><th>Excel 行</th><th>物料编码</th><th>物料名称</th><th>产品类</th><th>归属主体</th><th>状态</th><th>预检结果</th></tr></thead><tbody>{batch.rows.map(row => <tr key={row.id}><td>{row.row_number}</td><td className="code">{row.allocated_code || '-'}</td><td>{row.name}</td><td>{row.category_code}</td><td>{row.company_selection?.company_code || '-'}</td><td><span className={`status ${row.status === 'error' ? 'orange' : row.status === 'imported' ? 'green' : ''}`}><i />{row.status === 'error' ? '有错误' : row.status === 'imported' ? '已导入' : '可导入'}</span></td><td className="import-errors">{row.errors.length ? row.errors.join('；') : row.company_selection?.warnings?.join('；') || '校验通过'}</td></tr>)}</tbody></table></div>
    </> : <div className="import-empty"><FileSpreadsheet size={34} /><strong>上传后先预检</strong><span>预检只校验产品类、单位、库位、供应商、税务编码和主体公司关系，不会写入物料资料。</span></div>}
  </div>
}

function Stat({ label, value, tone = '' }) {
  return <div className="stat"><i className={`stat-mark ${tone}`} /><div><span>{label}</span><strong>{value}</strong></div></div>
}
