import { useState } from 'react'
import { Check, X } from 'lucide-react'
import { field } from '../../app/config'
import { Field } from '../../components/Field'

const customerMaterialFields = [
  field('customer', '客户代码', { lookup: 'customers', required: true }),
  field('material', '物料编码', { lookup: 'materials', required: true }),
  field('material_name', '物料名称', { kind: 'readonly' }),
  field('material_specification', '规格型号', { kind: 'readonly' }),
  field('customer_code', '客户物料编码', { required: true }),
  field('customer_name', '客户物料名称'),
  field('customer_specification', '客户规格'),
  field('customer_uom', '客户单位', { lookup: 'uoms' }),
  field('customer_uom_rate_m', '客户单位换算分子', { kind: 'number' }),
  field('customer_uom_rate_d', '客户单位换算分母', { kind: 'number' }),
  field('customer_barcode', '客户条码'),
  field('terminal_customer_code', '终端客户编码'),
  field('terminal_customer_name', '终端客户名称'),
  field('enabled', '启用', { kind: 'checkbox' }),
  field('notes', '备注'),
  field('created_by', '录入人', { kind: 'readonly' }),
  field('created_at', '录入时间', { kind: 'readonly' }),
]

export function CustomerMaterialModal({ lookups, record, onClose, onSave }) {
  const [values, setValues] = useState({
    customer_uom_rate_m: 1,
    customer_uom_rate_d: 1,
    enabled: true,
    ...(record || {}),
  })
  const update = (key, value) => {
    if (key === 'material') {
      const material = (lookups.materials || []).find((item) => item.id === Number(value))
      setValues((current) => ({
        ...current,
        material: value,
        material_name: material?.name || '',
        material_specification: material?.specification || '',
      }))
      return
    }
    setValues((current) => ({ ...current, [key]: value }))
  }
  return (
    <div className="modal-backdrop">
      <form
        className="modal"
        onSubmit={(event) => {
          event.preventDefault()
          const { material_name, material_specification, created_by, created_at, ...payload } = values
          onSave(payload)
        }}
      >
        <div className="modal-head">
          <div>
            <h2>{record ? '编辑' : '新增'}客户物料</h2>
            <p>客户和物料均关联本系统主数据，名称与规格由物料编码自动带出</p>
          </div>
          <button type="button" aria-label="关闭" onClick={onClose}>
            <X size={19} />
          </button>
        </div>
        <div className="form-grid">
          {customerMaterialFields.map((item) => (
            <Field
              key={item.key}
              field={item}
              value={values[item.key] ?? ''}
              options={item.lookup ? lookups[item.lookup] || [] : item.options || []}
              onChange={(value) => update(item.key, value)}
            />
          ))}
        </div>
        <div className="modal-foot">
          <button className="secondary" type="button" onClick={onClose}>
            取消
          </button>
          <button className="primary">
            <Check size={16} />
            保存
          </button>
        </div>
      </form>
    </div>
  )
}
