import assert from 'node:assert/strict'
import { test } from 'node:test'
import { api, upload, download, ApiError } from './client.js'

test('JSON, uploads and exports preserve server errors', async context => {
  const details = { quantity: ['Invalid quantity'] }
  context.mock.method(globalThis, 'fetch', async () => Response.json(details, { status: 400 }))
  for (const request of [() => api('/order/'), () => upload('/file/', new FormData()), () => download('/export/')]) {
    await assert.rejects(request, error => {
      assert.ok(error instanceof ApiError)
      assert.equal(error.status, 400)
      assert.deepEqual(error.data, details)
      assert.equal(error.message, 'quantity: Invalid quantity')
      return true
    })
  }
})

test('empty responses, multipart bodies and binary downloads retain their contracts', async context => {
  const fetch = context.mock.method(globalThis, 'fetch', async () => new Response(null, { status: 204 }))
  assert.deepEqual(await api('/order/', { method: 'DELETE' }), {})
  const form = new FormData()
  await upload('/file/', form, 'test-token')
  assert.equal(fetch.mock.calls[1].arguments[1].body, form)
  assert.equal(fetch.mock.calls[1].arguments[1].headers['Content-Type'], undefined)
  fetch.mock.mockImplementation(async () => new Response('workbook', {
    headers: { 'Content-Disposition': "attachment; filename*=UTF-8''ERP%20export.xlsx" }
  }))
  const result = await download('/export/')
  assert.equal(result.filename, 'ERP export.xlsx')
  assert.equal(await result.blob.text(), 'workbook')
})
