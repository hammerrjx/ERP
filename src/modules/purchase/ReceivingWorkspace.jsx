import { useEffect, useState } from 'react'
import { Search, Plus, Save, Undo2, Trash2, Check, Printer, Download, X, Paperclip, Minus } from 'lucide-react'
import { api, upload, download } from '../../api/client'
import { PurchaseGrid, Tool, today, statusNames, dateTime, sum } from './PurchaseControls'
import './purchase-workspace.css'
import './receiving.css'

const columns = [ ['line_number','行号'], ['purchase_number','采购单号'], ['purchase_line','采购行号'], ['material_code','物料编码'], ['material_name','物料名称'], ['specification','规格'], ['ordered_quantity','订购数量'], ['ordered_spare_quantity','订购备品'], ['quantity','正式数量'], ['spare_quantity','备品数量'], ['uom_name','采购单位'], ['location','库位'], ['batch_number','批号'], ['notes','备注'], ['pending_quantity','待检数量'], ['uom_rate_m','换算分子'], ['uom_rate_d','换算分母'], ['inventory_uom','库存单位'], ['source_order','原客户订单'], ['source_order_line','原订单行'] ]

export function ReceivingWorkspace({ session, returning = false, onClose, onOpenOrder }) {
  const resource = returning ? 'purchase-return' : 'goods-receipt'
  const title = returning ? '采购退货单' : '采购收货单'
  const blank = () => ({ site:'1000', supplier:'', supplier_name:'', supplier_code:'', receipt_date:today(), return_date:today(), supplier_delivery_number:'', notes:'', reason:'', replenishment:true, return_location:'', iqc_location:'', raw_location:'', default_print_person:session.username, status:'draft', lines:[], attachments:[] })
  const [doc,setDoc]=useState(blank), [saved,setSaved]=useState(null), [dirty,setDirty]=useState(false), [browse,setBrowse]=useState(true)
  const [list,setList]=useState({results:[],count:0}), [q,setQ]=useState(''), [page,setPage]=useState(1), [unconfirmed,setUnconfirmed]=useState(false)
  const [busy,setBusy]=useState(false), [error,setError]=useState(''), [notice,setNotice]=useState(''), [selected,setSelected]=useState(0)
  const [locations,setLocations]=useState([]), [lookup,setLookup]=useState(false), [lookupQ,setLookupQ]=useState(''), [suppliers,setSuppliers]=useState([]), [pickedSupplier,setPickedSupplier]=useState(null)
  const [generate,setGenerate]=useState(false), [candidates,setCandidates]=useState([]), [chosen,setChosen]=useState([]), [filters,setFilters]=useState({q:'',order_from:'',order_to:'',date_from:'',date_to:''}), [preview,setPreview]=useState(false)
  const [file,setFile]=useState(null)
  const request=(path,options={})=>api(path,{token:session.token,...options})
  const run=async fn=>{setBusy(true);setError('');setNotice('');try{return await fn()}catch(e){setError(e.message)}finally{setBusy(false)}}
  const adopt=data=>{setDoc(data);setSaved(data);setDirty(false);setBrowse(false);setSelected(0)}
  const leave=()=>!dirty || window.confirm('尚有未保存修改，确认放弃？')
  const locked=busy || !['draft','rejected'].includes(doc.status) || doc.posted
  const loadList=async(p=1)=>{const data=await request(`/${resource}/?${new URLSearchParams({workspace:'1',q,page:p,unconfirmed:unconfirmed?'1':'0'})}`);setList(data);setPage(p)}
  useEffect(()=>{run(()=>loadList());},[resource])
  useEffect(()=>{let active=true;request(`/${resource}/lookups/?kind=location&site=${encodeURIComponent(doc.site)}`).then(r=>{if(active)setLocations(r)}).catch(e=>{if(active)setError(e.message)});return()=>{active=false}},[doc.site,resource])
  const change=(key,value)=>{setDoc(d=>({...d,[key]:value}));setDirty(true)}
  const changeLine=(i,key,value)=>change('lines',doc.lines.map((r,n)=>n===i?{...r,[key]:value}:r))
  const save=()=>run(async()=>{const data=await request(`/${resource}/${doc.id?doc.id+'/':''}`,{method:doc.id?'PUT':'POST',body:doc});adopt(data);setNotice('单据已保存');await loadList(page)})
  const action=name=>run(async()=>{adopt(await request(`/${resource}/${doc.id}/${name}/`,{method:'POST',body:{version:doc.version}}));await loadList(page);setNotice('操作已完成')})
  const field=(key,label,type='text',readOnly=false,required=false)=><label>{label}{required&&<span className="rc-required"> *</span>}<input aria-label={label} type={type} readOnly={readOnly} disabled={!readOnly&&locked} value={doc[key]??''} onChange={e=>change(key,e.target.value)} /></label>
  const locationField=(key,label)=><label>{label}<select aria-label={label} disabled={locked} value={doc[key]||''} onChange={e=>change(key,e.target.value)}><option value="">请选择</option>{locations.map(l=><option key={l.id} value={l.id} disabled={l.disabled}>{l.code} {l.name}</option>)}</select></label>
  const queryCandidates=()=>run(async()=>{setCandidates(await request(`/${resource}/candidates/?${new URLSearchParams({...filters,supplier:doc.supplier,site:doc.site,document:doc.id||''})}`));setChosen([])})
  const addChosen=()=>{
    const existing=new Set(doc.lines.map(l=>l.purchase_order_line));let n=Math.max(0,...doc.lines.map(l=>Number(l.line_number)))
    const rows=candidates.filter(r=>chosen.includes(r.purchase_order_line)&&!existing.has(r.purchase_order_line)).map(r=>({...r,line_number:n+=10,source_location:doc.return_location||r.source_location}))
    change('lines',[...doc.lines,...rows]);setGenerate(false);setNotice(`已生成 ${rows.length} 行；已有来源行不重复添加`)
  }
  const uploadFile=()=>run(async()=>{if(!file)throw new Error('请选择回单附件');const form=new FormData();form.append('document_type','goodsreceipt');form.append('document_id',doc.id);form.append('evidence_type','supplier_delivery');form.append('file',file);await upload('/document-evidence/',form,session.token);adopt(await request(`/${resource}/${doc.id}/`));setFile(null);setNotice('附件已上传，可执行回单确认')})
  const downloadEvidence=e=>run(async()=>{const res=await fetch(`/api/document-evidence/${e.id}/download/`,{headers:{Authorization:`Token ${session.token}`}});if(!res.ok)throw new Error('附件下载失败');const url=URL.createObjectURL(await res.blob());const a=document.createElement('a');a.href=url;a.download=e.name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)})
  const exportFile=()=>run(async()=>{const result=await download(`/${resource}/${doc.id}/export/`,{token:session.token});const url=URL.createObjectURL(result.blob);const a=document.createElement('a');a.href=url;a.download=result.filename;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)})
  const cols=columns.filter(([key])=>!returning||!['pending_quantity','ordered_quantity','ordered_spare_quantity'].includes(key)).map(([key,label])=>key==='location'?[returning?'source_location':key,returning?'退货暂存仓':label]:key==='notes'?[returning?'reason':key,returning?'不良原因':label]:[key,label])
  if(returning)cols.splice(1,0,['iqc_number','IQC检验单号'],['iqc_line','IQC检验行号'])
  return <section className={`pu-workspace rc-workspace ${preview?'rc-preview':''}`}>
    <h1>{title}<span>{doc.number||'〈自动编号〉'}</span></h1>
    <div className="pu-toolbar">
      <Tool icon={Search} disabled={busy} onClick={()=>{if(leave()){setBrowse(true);run(()=>loadList())}}}>查询</Tool>
      <Tool icon={Plus} disabled={busy} onClick={()=>{if(leave()){setDoc(blank());setSaved(null);setDirty(false);setBrowse(false)}}}>新增</Tool>
      <Tool icon={Save} disabled={locked||!dirty} onClick={save}>保存</Tool>
      <Tool icon={Undo2} disabled={busy||!dirty} onClick={()=>saved?adopt(saved):(setDoc(blank()),setDirty(false))}>取消</Tool>
      <Tool icon={Trash2} disabled={locked||!doc.id} onClick={()=>{if(window.confirm(`删除 ${doc.number}？`))run(async()=>{await request(`/${resource}/${doc.id}/`,{method:'DELETE'});setDoc(blank());setSaved(null);setDirty(false);setBrowse(true);await loadList()})}}>删除</Tool>
      <Tool icon={Minus} disabled={locked||!doc.lines.length} onClick={()=>change('lines',doc.lines.filter((_,i)=>i!==selected))}>删行</Tool>
      <Tool icon={Check} disabled={busy||dirty||!doc.id||doc.status==='approved'} onClick={()=>action('approve')}>审核</Tool>
      <Tool icon={Undo2} disabled={busy||dirty||doc.status!=='approved'} onClick={()=>action('unapprove')}>反审核</Tool>
      {!returning&&<><Tool icon={Check} disabled={busy||dirty||doc.status!=='approved'||doc.is_confirmed} onClick={()=>action('confirm')}>回单确认</Tool><Tool icon={Undo2} disabled={busy||dirty||!doc.is_confirmed} onClick={()=>action('unconfirm')}>反回单确认</Tool></>}
      <Tool icon={Search} disabled={!doc.id||dirty} onClick={()=>{setBrowse(false);setPreview(!preview)}}>{preview?'关闭预览':'预览'}</Tool>
      <Tool icon={Printer} disabled={busy||!doc.id||dirty} onClick={()=>run(async()=>{adopt(await request(`/${resource}/${doc.id}/print/`,{method:'POST'}));setPreview(true);setTimeout(()=>window.print(),100)})}>打印</Tool>
      <Tool icon={Download} disabled={busy||!doc.id||dirty} onClick={exportFile}>导出</Tool><Tool icon={X} onClick={()=>{if(leave())onClose()}}>关闭</Tool>
    </div>
    {error&&<p role="alert" className="pu-error">{error}</p>}{notice&&<p role="status" className="pu-notice">{notice}</p>}
    <nav className="pu-tabs"><button aria-selected={!browse} onClick={()=>setBrowse(false)}>资料维护</button><button aria-selected={browse} onClick={()=>{if(leave()){setBrowse(true);run(()=>loadList())}}}>资料浏览</button></nav>
    {browse?<><form className="pu-query" onSubmit={e=>{e.preventDefault();run(()=>loadList())}}><input aria-label="单据查询" placeholder="单号、供应商代码或名称" value={q} onChange={e=>setQ(e.target.value)}/>{!returning&&<label><input type="checkbox" checked={unconfirmed} onChange={e=>setUnconfirmed(e.target.checked)}/>已审核未回单</label>}<button disabled={busy}>查询</button></form>
      <PurchaseGrid label={`${title}资料浏览`} className="pu-grow" columns={[['number','单号'],['supplier_name','供应商'],['date','日期'],['supplier_delivery_number','供应商送货单号'],['status','审核状态'],...(!returning?[['is_confirmed','回单确认']]:[])]} rows={list.results} cell={(r,k)=>k==='number'?<button className="pu-link" onClick={()=>run(async()=>adopt(await request(`/${resource}/${r.id}/`)))}>{r.number}</button>:k==='status'?statusNames[r.status]:k==='is_confirmed'?(r[k]?'已确认':'未确认'):r[k]}/>
      <footer className="pu-pagination">共 {list.count} 张<button disabled={busy||page<=1} onClick={()=>run(()=>loadList(page-1))}>上一页</button>{page}<button disabled={busy||page*50>=list.count} onClick={()=>run(()=>loadList(page+1))}>下一页</button></footer></>:
      <><div className="rc-header"><div className="rc-fields">
        {field('number',returning?'退货单号':'收货单号','text',true)}{field(returning?'return_date':'receipt_date','日期','date',false,true)}{field('site','站点','text',true)}
        <label>供应商代码 <span className="rc-required">*</span><span className="pu-search-field"><input aria-label="供应商代码" readOnly value={doc.supplier_code} disabled={locked}/><button aria-label="检索供应商" disabled={locked} onClick={()=>{setLookup(true);setPickedSupplier(null);run(async()=>setSuppliers(await request(`/${resource}/lookups/?kind=supplier`)))}}><Search size={14}/></button></span></label>{field('supplier_name','供应商名称','text',true)}
        {!returning&&field('supplier_delivery_number','供应商送货单号','text',false,true)}
        {returning?<>{locationField('return_location','退货暂存仓 *')}<label className="rc-check"><input type="checkbox" checked={doc.replenishment} disabled={locked} onChange={e=>change('replenishment',e.target.checked)}/>补货</label>{field('reason','备注')}</>:<>{locationField('iqc_location','IQC库位')}{locationField('raw_location','原材料库位')}{field('notes','备注')}</>}
        {field('default_print_person','默认打印人')}{field('print_count','打印次数','text',true)}
      </div><dl className="rc-audit"><dt>状态</dt><dd>{statusNames[doc.status]}{!returning&&` · ${doc.is_confirmed?'回单已确认':'回单未确认'}`}</dd>{[['created_by','录入人'],['created_at','录入时间'],['updated_by','修改人'],['updated_at','修改时间'],['approved_by','审核人'],['approved_at','审核时间'],...(!returning?[['confirmed_by','回单确认人'],['confirmed_at','确认时间']]:[])].map(([k,l])=><div key={k}><dt>{l}</dt><dd>{k.endsWith('_at')?dateTime(doc[k]):doc[k]||'—'}</dd></div>)}</dl></div>
      <div className="rc-actions"><button disabled={locked||!doc.supplier} onClick={()=>{setGenerate(true);setCandidates([]);setChosen([])}}>{returning?'选择可退采购明细':'工具：按采购单生成收货明细'}</button>{!returning&&<button disabled={!doc.id||dirty||busy} onClick={()=>run(async()=>setNotice((await request(`/${resource}/${doc.id}/shortage/`)).message))}>查询本单缺料情况</button>}</div>
      <PurchaseGrid label={`${title}明细`} className="pu-grow" columns={cols} rows={doc.lines} selected={selected} onSelect={setSelected} totals={{quantity:sum(doc.lines.map(l=>l.quantity)),spare_quantity:sum(doc.lines.map(l=>l.spare_quantity))}} cell={(r,k,label,i)=>{
        if(['quantity','spare_quantity','batch_number','notes','reason'].includes(k))return <input aria-label={`${label} 第${i+1}行`} disabled={locked} type={['quantity','spare_quantity'].includes(k)?'number':'text'} step="0.00000001" value={r[k]??''} onChange={e=>changeLine(i,k,e.target.value)}/>
        if(['location','source_location'].includes(k))return <select aria-label={`${label} 第${i+1}行`} disabled={locked} value={r[k]||''} onChange={e=>changeLine(i,k,e.target.value)}><option value="">请选择</option>{locations.map(l=><option key={l.id} value={l.id} disabled={l.disabled}>{l.code}</option>)}</select>
        if(k==='purchase_number')return <button className="pu-link" disabled={!r.purchase_order} onClick={()=>{if(leave())onOpenOrder?.(r.purchase_order)}}>{r[k]}</button>
        return <span className="rc-derived">{r[k]??''}</span>
      }}/>
      {!returning&&doc.id&&<div className="rc-attachments"><strong><Paperclip size={15}/>回单附件</strong>{doc.attachments?.map(e=><button key={e.id} onClick={()=>downloadEvidence(e)}>{e.name}</button>)}<input type="file" aria-label="上传回单附件" accept=".pdf,.png,.jpg,.jpeg" disabled={busy||dirty||doc.is_confirmed} onChange={e=>setFile(e.target.files[0])}/><button disabled={busy||dirty||!file||doc.is_confirmed} onClick={uploadFile}>上传附件</button></div>}
      <footer className="pu-pagination">{doc.lines.length} 行 · {doc.site} · {dirty||!doc.id?'尚未保存':'已保存'}{doc.imported&&' · 历史单据'}</footer></>}
    {preview&&<article className="rc-print-sheet">
      <h2>{title}</h2><div className="rc-print-info"><span>单号：{doc.number}</span><span>日期：{returning?doc.return_date:doc.receipt_date}</span><span>站点：{doc.site}</span><span>供应商：{doc.supplier_code} {doc.supplier_name}</span>{!returning&&<span>供应商送货单号：{doc.supplier_delivery_number}</span>}</div>
      <table><thead><tr>{['行','采购单 / 行','物料编码','物料名称 / 规格','正式数量','备品数量','单位','库位','批号','备注'].map(t=><th key={t}>{t}</th>)}</tr></thead><tbody>{doc.lines.map((r,i)=><tr key={r.id||i}><td>{r.line_number}</td><td>{r.purchase_number} / {r.purchase_line}</td><td>{r.material_code}</td><td>{r.material_name}<br/>{r.specification}</td><td>{r.quantity}</td><td>{r.spare_quantity}</td><td>{r.uom_name}</td><td>{r.location_code||locations.find(l=>String(l.id)===String(r[returning?'source_location':'location']))?.code}</td><td>{r.batch_number}</td><td>{returning?r.reason:r.notes}</td></tr>)}</tbody><tfoot><tr><th colSpan="4">合计</th><td>{sum(doc.lines.map(r=>r.quantity))}</td><td>{sum(doc.lines.map(r=>r.spare_quantity))}</td><td colSpan="4"/></tr></tfoot></table>
      <p>备注：{returning?doc.reason:doc.notes}</p><footer><span>录入：{doc.created_by}</span><span>审核：{doc.approved_by||'未审核'}</span><span>打印：{doc.default_print_person}</span></footer>
    </article>}
    {lookup&&<div className="pu-backdrop"><section className="pu-dialog pu-lookup" role="dialog" aria-modal="true" aria-label="供应商查询"><header><strong>供应商查询</strong><button aria-label="关闭供应商查询" onClick={()=>setLookup(false)}><X size={16}/></button></header><form className="pu-query" onSubmit={e=>{e.preventDefault();run(async()=>setSuppliers(await request(`/${resource}/lookups/?${new URLSearchParams({kind:'supplier',q:lookupQ})}`)))}}><label>简称 / 代码 / 名称<input autoFocus value={lookupQ} onChange={e=>setLookupQ(e.target.value)}/></label><span>包含</span><button disabled={busy}>查询</button></form><div className="pu-lookup-list">{suppliers.map(s=><button key={s.id} className={pickedSupplier?.id===s.id?'rc-picked':''} onClick={()=>setPickedSupplier(s)}>{s.code}　{s.short_name}　{s.name}</button>)}</div><footer><button disabled={!pickedSupplier} onClick={()=>{if(doc.lines.length && doc.supplier!==pickedSupplier.id && !window.confirm('更换供应商将清空已选明细，确认继续？'))return;setDoc(d=>({...d,supplier:pickedSupplier.id,supplier_code:pickedSupplier.code,supplier_name:pickedSupplier.name,lines:d.supplier===pickedSupplier.id?d.lines:[]}));setDirty(true);setLookup(false)}}>确认</button><button onClick={()=>setLookup(false)}>取消</button></footer></section></div>}
    {generate&&<div className="pu-backdrop"><section className="pu-dialog rc-generator" role="dialog" aria-modal="true" aria-label={returning?'选择可退明细':'按采购单生成收货明细'}><header><strong>{returning?'选择可退采购明细':'按采购单生成收货明细'}</strong><button aria-label="关闭生成窗口" onClick={()=>setGenerate(false)}><X size={16}/></button></header><form className="rc-filter" onSubmit={e=>{e.preventDefault();queryCandidates()}}>{[['q','物料 / 采购单','text'],['order_from','采购单从','text'],['order_to','采购单至','text'],['date_from','下单日期从','date'],['date_to','下单日期至','date']].map(([k,l,t])=><label key={k}>{l}<input aria-label={l} type={t} value={filters[k]} onChange={e=>setFilters({...filters,[k]:e.target.value})}/></label>)}<button disabled={busy}>查询</button></form><div className="rc-actions"><button onClick={()=>setChosen(candidates.map(r=>r.purchase_order_line))}>全选</button><button onClick={()=>setChosen([])}>全不选</button><span>本次数量默认使用剩余额度，可生成后修改；最多显示500项，请按条件筛选。</span></div><PurchaseGrid label="采购来源候选" columns={[["selected","选择"],...columns.slice(1,8),['received_quantity','已收数量'],['reserved_quantity','未审核占用'],['available_quantity',returning?'可退数量':'可收数量'],['available_spare_quantity',returning?'可退备品':'可收备品']]} rows={candidates} cell={(r,k)=>k==='selected'?<input type="checkbox" aria-label={`选择 ${r.purchase_number}/${r.purchase_line}`} checked={chosen.includes(r.purchase_order_line)} onChange={e=>setChosen(e.target.checked?[...chosen,r.purchase_order_line]:chosen.filter(id=>id!==r.purchase_order_line))}/>:r[k]}/><footer><button disabled={!chosen.length||busy} onClick={addChosen}>生成</button><button onClick={()=>setGenerate(false)}>关闭</button></footer></section></div>}
  </section>
}
