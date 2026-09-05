import { useState } from 'react'
import { Lock, User } from 'lucide-react'
import { api } from '../api/client'

export function Login({ onLogin }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const submit = async event => {
    event.preventDefault(); setBusy(true); setError('')
    try { onLogin(await api('/auth/login/', { method: 'POST', body: { username, password } })) }
    catch (requestError) { setError(requestError.message) }
    finally { setBusy(false) }
  }
  return (
    <main className="lg-page">
      <div className="lg-orb lg-orb-1" />
      <div className="lg-orb lg-orb-2" />
      <div className="lg-orb lg-orb-3" />
      <div className="lg-stage">
        <div className="lg-scene">
          <svg viewBox="0 0 620 540" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="仓储物流 3D 插画">
            <defs>
              <linearGradient id="plat1" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0" stopColor="#E6DCF6" /><stop offset="1" stopColor="#C9B8E8" />
              </linearGradient>
              <linearGradient id="plat2" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0" stopColor="#D9E7F7" /><stop offset="1" stopColor="#B7D2EE" />
              </linearGradient>
              <linearGradient id="platTop" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0" stopColor="#FFFFFF" /><stop offset="1" stopColor="#EDF1F8" />
              </linearGradient>
              <linearGradient id="ringG" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0" stopColor="#F5A06B" /><stop offset=".5" stopColor="#8FB8E8" /><stop offset="1" stopColor="#B9A6E4" />
              </linearGradient>
              <linearGradient id="boxA" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0" stopColor="#F6C58A" /><stop offset="1" stopColor="#E89B4C" />
              </linearGradient>
              <linearGradient id="boxB" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0" stopColor="#B8D4F2" /><stop offset="1" stopColor="#84AEDD" />
              </linearGradient>
              <linearGradient id="clipG" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0" stopColor="#CFC6F0" /><stop offset="1" stopColor="#A496DC" />
              </linearGradient>
              <filter id="soft" x="-40%" y="-40%" width="180%" height="180%">
                <feGaussianBlur stdDeviation="10" />
              </filter>
              <filter id="cardShadow" x="-40%" y="-40%" width="180%" height="180%">
                <feDropShadow dx="0" dy="8" stdDeviation="10" floodColor="#4A3E6B" floodOpacity="0.18" />
              </filter>
            </defs>

            <ellipse cx="310" cy="470" rx="225" ry="34" fill="#4A3E6B" opacity="0.14" filter="url(#soft)" />

            <g>
              <ellipse cx="310" cy="440" rx="215" ry="52" fill="url(#plat1)" />
              <ellipse cx="310" cy="428" rx="215" ry="52" fill="#EFE8FB" />
              <ellipse cx="310" cy="416" rx="178" ry="42" fill="url(#plat2)" />
              <ellipse cx="310" cy="406" rx="178" ry="42" fill="#EAF2FB" />
              <ellipse cx="310" cy="394" rx="140" ry="33" fill="url(#platTop)" />
              <g className="lg-ring">
                <ellipse cx="310" cy="394" rx="126" ry="28" fill="none" stroke="url(#ringG)" strokeWidth="5" strokeDasharray="120 60" strokeLinecap="round" opacity=".9" />
              </g>
              <ellipse cx="310" cy="394" rx="104" ry="22" fill="none" stroke="#D9E2F0" strokeWidth="2" />
            </g>

            <g filter="url(#cardShadow)">
              <rect x="150" y="300" width="86" height="96" rx="6" fill="url(#boxB)" />
              <rect x="160" y="312" width="66" height="12" rx="3" fill="#5E93CC" />
              <rect x="160" y="332" width="66" height="12" rx="3" fill="#5E93CC" />
              <rect x="160" y="352" width="66" height="12" rx="3" fill="#5E93CC" />
              <rect x="166" y="316" width="14" height="8" rx="2" fill="#EAF2FB" />
              <rect x="186" y="336" width="14" height="8" rx="2" fill="#EAF2FB" />
              <rect x="170" y="356" width="14" height="8" rx="2" fill="#EAF2FB" />
            </g>

            <g filter="url(#cardShadow)">
              <rect x="248" y="322" width="64" height="74" rx="6" fill="url(#boxA)" />
              <rect x="256" y="332" width="48" height="10" rx="3" fill="#D17F2E" />
              <rect x="256" y="350" width="48" height="10" rx="3" fill="#D17F2E" />
              <rect x="256" y="368" width="48" height="10" rx="3" fill="#D17F2E" />
              <rect x="326" y="344" width="46" height="52" rx="6" fill="#F0B26B" />
              <rect x="333" y="353" width="32" height="8" rx="3" fill="#D17F2E" />
              <rect x="333" y="367" width="32" height="8" rx="3" fill="#D17F2E" />
            </g>

            <g filter="url(#cardShadow)">
              <rect x="382" y="292" width="72" height="104" rx="8" fill="url(#clipG)" />
              <rect x="404" y="284" width="28" height="16" rx="7" fill="#8F7BCB" />
              <rect x="392" y="312" width="52" height="7" rx="3.5" fill="#EFEAFB" />
              <rect x="392" y="327" width="52" height="7" rx="3.5" fill="#EFEAFB" />
              <rect x="392" y="342" width="38" height="7" rx="3.5" fill="#EFEAFB" />
              <rect x="392" y="357" width="44" height="7" rx="3.5" fill="#EFEAFB" />
              <circle cx="438" cy="382" r="8" fill="#1D9E75" />
              <path d="M434 382 l3 3 l6 -6" stroke="#fff" strokeWidth="2.5" fill="none" strokeLinecap="round" />
            </g>

            <g className="lg-float-1" filter="url(#cardShadow)">
              <rect x="92" y="168" width="118" height="84" rx="14" fill="rgba(255,255,255,0.85)" stroke="#E3E7F0" />
              <text x="108" y="192" fontSize="12" fill="#6B7186">交付趋势</text>
              <polyline points="106,232 126,218 146,226 166,206 186,212" fill="none" stroke="#E8722F" strokeWidth="3" strokeLinecap="round" />
              <circle cx="186" cy="212" r="4" fill="#E8722F" />
              <circle className="lg-dot" cx="196" cy="180" r="4" fill="#1D9E75" />
            </g>

            <g className="lg-float-2" filter="url(#cardShadow)">
              <rect x="428" y="196" width="112" height="80" rx="14" fill="rgba(255,255,255,0.85)" stroke="#E3E7F0" />
              <text x="444" y="220" fontSize="12" fill="#6B7186">合格率</text>
              <circle cx="462" cy="248" r="15" fill="none" stroke="#E5EAF3" strokeWidth="6" />
              <path d="M462 233 A15 15 0 1 1 449 256" fill="none" stroke="#1D9E75" strokeWidth="6" strokeLinecap="round" />
              <text x="486" y="253" fontSize="15" fontWeight="700" fill="#2C2C2A">98.2%</text>
            </g>

            <g className="lg-drone">
              <ellipse cx="310" cy="150" rx="30" ry="7" fill="#4A3E6B" opacity=".12" filter="url(#soft)" />
              <rect x="292" y="108" width="36" height="20" rx="7" fill="#3E3E42" />
              <rect x="266" y="104" width="88" height="4" rx="2" fill="#6E6E74" />
              <line x1="270" y1="108" x2="262" y2="122" stroke="#6E6E74" strokeWidth="3" />
              <line x1="350" y1="108" x2="358" y2="122" stroke="#6E6E74" strokeWidth="3" />
              <ellipse cx="258" cy="100" rx="20" ry="4" fill="#9A9AA2" opacity=".85" />
              <ellipse cx="362" cy="100" rx="20" ry="4" fill="#9A9AA2" opacity=".85" />
              <circle cx="310" cy="126" r="5" fill="#F5A06B" />
            </g>

            <circle className="lg-float-2" cx="120" cy="300" r="9" fill="#B9A6E4" opacity=".8" />
            <circle className="lg-float-1" cx="520" cy="320" r="7" fill="#F5A06B" opacity=".8" />
            <circle className="lg-float-1" cx="470" cy="130" r="6" fill="#8FB8E8" opacity=".8" />
          </svg>
        </div>

        <form className="lg-card" onSubmit={submit}>
          <div className="lg-brand">
            <div className="lg-brand-logo">E</div>
            <div>
              <div className="lg-brand-name">ERP Cloud</div>
              <div className="lg-brand-sub">企业资源计划系统</div>
            </div>
          </div>
          <div className="lg-field">
            <User size={17} />
            <input required placeholder="账号 / 工号" value={username} onChange={event => setUsername(event.target.value)} autoComplete="username" />
          </div>
          <div className="lg-field">
            <Lock size={17} />
            <input required type="password" placeholder="登录密码" value={password} onChange={event => setPassword(event.target.value)} autoComplete="current-password" />
          </div>
          <div className="lg-row">
            <label className="lg-remember"><input type="checkbox" defaultChecked /> 记住我</label>
            <a className="lg-forgot" href="#">忘记密码？</a>
          </div>
          {error ? <p className="lg-error">{error}</p> : null}
          <button className="lg-btn" type="submit" disabled={busy}>{busy ? '登录中…' : '登 录'}</button>
          <p className="lg-foot">仅授权员工访问 · 登录即代表同意信息安全协议</p>
        </form>
      </div>
    </main>
  )
}
