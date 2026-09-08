const API_ROOT = '/api'

export class ApiError extends Error {
  constructor(message, { status, data } = {}) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.data = data
  }
}

async function responseData(response, fallback = '请求失败') {
  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    const message =
      typeof data.detail === 'string'
        ? data.detail
        : Object.entries(data)
            .map(([key, value]) => `${key}: ${[].concat(value).join(' ')}`)
            .join('；')
    throw new ApiError(message || fallback, { status: response.status, data })
  }
  return data
}

export function api(path, { token, method = 'GET', body } = {}) {
  return fetch(`${API_ROOT}${path}`, {
    method,
    headers: {
      ...(token ? { Authorization: `Token ${token}` } : {}),
      ...(body ? { 'Content-Type': 'application/json' } : {})
    },
    body: body ? JSON.stringify(body) : undefined
  }).then(responseData)
}

export function listPayload(data) {
  return Array.isArray(data) ? data : data.results || []
}

export function upload(path, formData, token) {
  return fetch(`${API_ROOT}${path}`, {
    method: 'POST',
    headers: token ? { Authorization: `Token ${token}` } : {},
    body: formData
  }).then(responseData)
}

export async function download(path, { token, body } = {}) {
  const response = await fetch(`${API_ROOT}${path}`, {
    method: 'POST',
    headers: { ...(token ? { Authorization: `Token ${token}` } : {}), 'Content-Type': 'application/json' },
    body: JSON.stringify(body || {})
  })
  if (!response.ok) await responseData(response, '导出失败')
  const disposition = response.headers.get('Content-Disposition') || ''
  const encodedName = disposition.match(/filename\*=UTF-8''([^;]+)/i)?.[1]
  return { blob: await response.blob(), filename: encodedName ? decodeURIComponent(encodedName) : 'ERP导出.xlsx' }
}

export function resourceApi(resource, token) {
  const path = (id) => (id == null ? '/' + resource + '/' : '/' + resource + '/' + id + '/')
  return {
    list: () => api(path(), { token }),
    retrieve: (id) => api(path(id), { token }),
    create: (body) => api(path(), { token, method: 'POST', body }),
    update: (id, body) => api(path(id), { token, method: 'PATCH', body }),
    remove: (id) => api(path(id), { token, method: 'DELETE' }),
    action: (id, name, body = {}) => api('/' + resource + '/' + id + '/' + name + '/', { token, method: 'POST', body })
  }
}
