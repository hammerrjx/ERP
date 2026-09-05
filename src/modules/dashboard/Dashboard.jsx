import { AlertTriangle, ArrowUpRight, ClipboardList, Package, RefreshCw, ShoppingCart } from 'lucide-react'

export function Dashboard({ data, modules, configs, onSelect, loading, error, onRetry }) {
  const count = id => data[id]?.length ?? null
  const quick = modules.flatMap(module => module.items?.length ? [module.items[0]] : [])
  return <div className="dashboard"><div className="welcome"><div><h1>ERP 工作台</h1><p>阶段 1 主数据与阶段 2 销售、采购、库存闭环。</p></div>{quick[0] ? <button className="primary" onClick={() => onSelect(quick[0][0])}><ArrowUpRight size={17} />进入业务</button> : null}</div>{error ? <div className="error-banner" role="alert"><span>工作台数据加载失败：{error}</span><button className="secondary" onClick={onRetry} disabled={loading}><RefreshCw size={15} />重试</button></div> : null}<div className="metric-grid">{loading ? <div className="dashboard-loading">正在加载工作台数据</div> : <><Metric label="物料" value={count('materials')} icon={Package} /><Metric label="销售订单" value={count('salesOrders')} icon={ShoppingCart} tone="blue" /><Metric label="采购订单" value={count('purchaseOrders')} icon={ClipboardList} tone="orange" /><Metric label="缺料预警" value={count('alerts')} icon={AlertTriangle} tone="red" /></>}</div><section className="panel"><div className="panel-head"><div><h2>业务入口</h2><p>仅显示当前账号有权访问的功能</p></div></div><div className="quick-grid">{quick.map(([id, label]) => { const Icon = configs[id].icon; return <button className="quick" key={id} onClick={() => onSelect(id)}><div className="quick-icon"><Icon size={19} /></div><div><strong>{label}</strong><span>{configs[id].title}</span></div><ArrowUpRight size={16} /></button> })}</div></section></div>
}

function Metric({ label, value, tone = '', icon: Icon }) {
  return <div className="metric"><div className={`metric-icon ${tone}`}><Icon size={19} /></div><span>{label}</span><strong>{value == null ? '—' : value}</strong></div>
}
