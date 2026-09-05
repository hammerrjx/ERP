const SESSION_KEY = 'erp-session'

export function readSession() {
  try { return JSON.parse(localStorage.getItem(SESSION_KEY) || 'null') } catch { return null }
}

export function saveSession(session) {
  localStorage.setItem(SESSION_KEY, JSON.stringify(session))
}

export function clearSession() {
  localStorage.removeItem(SESSION_KEY)
}

export function can(session, permission, action = 'view') {
  return Boolean(session?.permissions?.includes('*') || session?.permissions?.includes(`${permission}.${action}`))
}
