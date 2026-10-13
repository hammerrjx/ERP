import test from 'node:test'
import assert from 'node:assert/strict'
import { previewLineNumbers } from '../../src/modules/sales/lineNumbers.js'

test('new lines follow saved maximum while imported and reordered lines retain their numbers', () => {
  const saved = [{ id: 1, line_number: 15 }, { id: 2, line_number: 35 }]
  assert.deepEqual(previewLineNumbers([{}, {}]), [10, 20])
  assert.deepEqual(previewLineNumbers([saved[0], {}], saved), [15, 45])
  assert.deepEqual(previewLineNumbers([saved[1], {}, saved[0], {}], saved), [35, 45, 15, 55])
})
