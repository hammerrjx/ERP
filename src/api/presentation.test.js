import assert from 'node:assert/strict'
import { test } from 'node:test'
import { today } from '../shared/presentation.js'

test('business dates use Shanghai midnight, including year boundaries', context => {
  const RealDate = Date
  for (const [instant, expected] of [
    ['2026-09-07T16:00:00Z', '2026-09-08'],
    ['2026-09-07T15:59:59Z', '2026-09-07'],
    ['2026-12-31T16:00:00Z', '2027-01-01']
  ]) {
    context.mock.method(globalThis, 'Date', class extends RealDate {
      constructor() { super(instant) }
    })
    assert.equal(today(), expected)
    context.mock.restoreAll()
  }
})
