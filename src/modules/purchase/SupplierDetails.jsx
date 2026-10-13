import { useState } from 'react'
import { Plus, Minus } from 'lucide-react'
import { SearchableLookup } from '../../components/Field'

const enums = {
  supplier_type: [['1', '资源供应商'], ['2', '材料采购供应商'], ['3', '外协加工供应商']],
  quote_method: [['1', '含税价'], ['2', '不含税价']],
  invoice_type: [['1', '增值税专用发票'], ['2', '普通发票'], ['9', '其它']],
  material_price_method: [['01', '最高报价'], ['02', '最新报价'], ['03', '供应商报价'], ['04', '标准成本'], ['05', '最高采购单价'], ['06', '最高采购单价(含)'], ['07', '最低采购单价']],
}

function Lookup({ label, value, rows, onChange, disabled, codeValue = false, displayName = false }) {
  const options = rows.map(row => ({ ...row, id: codeValue ? row.code : row.id, name: row.name || row.description || '' }))
  const selected = options.find(row => String(row.id) === String(value))
  const bankType = options.some(row => row.code === 'company')
  return <div className={`sw-code-name${displayName ? ' sw-display-name' : ''}`}><SearchableLookup label={label} value={value} options={options} onChange={onChange} disabled={disabled} hideLabel portal allowClear clearOnFocus className="sw-lookup" selectedText={displayName ? row => row.name : undefined} optionCode={bankType ? row => row.code === 'company' ? '1' : '2' : undefined} />{!displayName && <output title={selected?.name}>{selected?.name}</output>}</div>
}

export function SupplierDetails({ doc, set, head, input, locked, lookups, options, lineRows, selected, setSelected, updateLine }) {
  const [tab, setTab] = useState('basic')
  const lookup = (label, key, resource, codeValue = false) => head(label, <Lookup label={label} value={doc[key]} rows={options(resource, doc[key])} onChange={value => set(key, value || '')} disabled={locked} codeValue={codeValue} />)
  const choice = (label, key) => head(label, <Lookup label={label} value={doc[key]} rows={enums[key].map(([code, name]) => ({ code, name }))} codeValue displayName onChange={value => { set(key, value); if (key === 'quote_method') set('quote_tax_included', value === '1') }} disabled={locked} />)
  const checks = [['quoted_settlement','按报价结算'],['payment_hold','暂停付款'],['three_certificates','三证合一'],['business_license','开户许可证'],['internal_company','内部公司']]
  const contacts = doc.contacts || []
  const contactSet = (index, key, value) => set('contacts', contacts.map((row, i) => i === index ? {...row, [key]: value} : row))
  const stamp = value => value ? String(value).replace('T', ' ').slice(0,19) : ''
  const bankFields = [['bank_name','开户行'],['account_name','开户名'],['account_number','银行账号'],['other_info','其它信息'],['notes','备注']]
  return <>
    <div className="sw-tabs"><button className={tab === 'basic' ? 'active' : ''} onClick={() => setTab('basic')}>基本信息</button><button className={tab === 'contacts' ? 'active' : ''} onClick={() => setTab('contacts')}>联系方式</button></div>
    {tab === 'basic' ? <div className="sw-head sw-supplier-head"><div className="sw-fields">
      {input('供应商代码','code')}{input('简称','short_name')}{input('全称','name')}
      {input('地址','address')}{input('网址','website')}{lookup('采购员','buyer','employee',true)}
      {lookup('常用币种','currency','currency')}{lookup('支付方式','payment_method_master','payment-method')}{choice('报价方式','quote_method')}
      {input('增值税率(%)','tax_rate','number')}{choice('发票类型','invoice_type')}{input('服务评分','service_score','number')}
      {input('备品比例(%)','backup_ratio','number')}{input('超收货比例(%)','over_receipt_ratio','number')}{choice('类型','supplier_type')}
      {head('类别', <Lookup label="类别" value={doc.strategic_supplier ? '2' : '1'} rows={[{code:'1',name:'普通供应商'},{code:'2',name:'战略供应商'}]} codeValue displayName disabled={locked} onChange={value => set('strategic_supplier',value === '2')} />)}
      {choice('卖料单价取值','material_price_method')}{input('卖料单价系数','material_price_factor','number')}
      {input('法人','legal_person')}{input('注册资金(万元)','registered_capital','number')}{input('营业额(万元)','annual_revenue','number')}
      {input('开业日期','opening_date','date')}{input('税号','tax_number')}{input('员工人数','employee_count','number')}
      {lookup('应付账款科目','purchase_account','accounting-account',true)}{lookup('暂估应付科目','temporary_payable_account','accounting-account',true)}
      {lookup('委托加工费科目','outsource_fee_account','accounting-account',true)}{lookup('委托加工物资科目','outsource_material_account','accounting-account',true)}
      {lookup('入库库位','default_receipt_location','location')}{lookup('支付方式2','payment_method_2','payment-method',true)}{lookup('支付方式3','payment_method_3','payment-method',true)}
      {head('备注',<textarea aria-label="备注" disabled={locked} value={doc.notes || ''} onChange={event => set('notes',event.target.value)} />)}
      <div className="sw-checks">{checks.map(([key,label]) => <label className="sw-check" key={key}><input type="checkbox" checked={Boolean(doc[key])} disabled={locked} onChange={event => set(key,event.target.checked)} />{label}</label>)}</div>
    </div><aside className="sw-audit"><strong>{({approved:'已审核',draft:'草稿',pending:'待审核',void:'已作废',rejected:'已驳回'})[doc.status] || '草稿'}</strong>{[['录入人',doc.created_by],['录入时间',stamp(doc.created_at)],['审核人',doc.approved_by],['审核时间',stamp(doc.approved_at)],['确认',doc.is_confirmed ? '已确认' : '未确认'],['确认人',doc.confirmed_by],['确认时间',stamp(doc.confirmed_at)]].map(([label,value]) => <div key={label}><span>{label}</span><output>{value || ''}</output></div>)}</aside></div>
    : <div className="sw-contacts"><button disabled={locked || contacts.length >= 4} onClick={() => set('contacts',[...contacts,{name:'',phone:'',fax:'',email:'',position:''}])}><Plus size={15}/>新增联系人</button>{contacts.map((row,index) => <div className="sw-contact-row" key={index}>{[['name','联系人'],['position','职位'],['phone','电话'],['fax','传真'],['email','邮箱']].map(([key,label]) => head(label,<input aria-label={`${label}${index+1}`} disabled={locked} value={row[key] || ''} onChange={event => contactSet(index,key,event.target.value)} />))}<button title="删除联系人" disabled={locked} onClick={() => set('contacts',contacts.filter((_,i) => i !== index))}><Minus size={15}/></button></div>)}</div>}
    <div className="sw-detail-title">银行账户</div><div className="sw-grid"><table className="sw-lines"><thead><tr>{['行号','类型',...bankFields.map(([,label]) => label),'录入人','录入时间','修改次数','最后修改人','最后修改时间','银行联行号'].map(label => <th key={label}>{label}</th>)}</tr></thead><tbody>{lineRows.map((row,index) => <tr key={row.id || `new-${index}`} className={selected === index ? 'selected' : ''} onClick={() => setSelected(index)}>
      <td className="sw-derived">{row.line_number}</td><td className="sw-bank-type"><Lookup label={`银行账户类型${index+1}`} value={row.account_type} rows={[{code:'company',name:'公司'},{code:'personal',name:'个人'}]} codeValue displayName disabled={locked} onChange={value => updateLine(index,'account_type',value)} /></td>
      {bankFields.map(([key,label]) => <td key={key}><input aria-label={`${label}${index+1}`} disabled={locked} value={row[key] || ''} onChange={event => updateLine(index,key,event.target.value)} /></td>)}
      {[row.created_by,stamp(row.created_at),row.modification_count,row.updated_by,stamp(row.updated_at)].map((value,i) => <td className="sw-derived" key={i}>{value ?? ''}</td>)}
      <td><input aria-label={`银行联行号${index+1}`} disabled={locked} value={row.bank_code || ''} onChange={event => updateLine(index,'bank_code',event.target.value)} /></td>
    </tr>)}</tbody></table>{!lineRows.length && <p className="sw-empty">暂无银行账户</p>}</div>
  </>
}
