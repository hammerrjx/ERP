const { test, before, after } = require('node:test');
const assert = require('node:assert/strict');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const frontend = process.env.ERP_FRONTEND_URL || 'http://127.0.0.1:5176';
let browser;
before(async () => { browser = await chromium.launch({ channel: 'msedge', headless: true }); });
after(async () => { await browser?.close(); });

async function pageFor(t, handler = async route => route.fulfill({ json: [] })) {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  page.setDefaultTimeout(10000);
  t.after(() => page.close());
  await page.route('**/api/**', route => {
    if (!new URL(route.request().url()).pathname.startsWith('/api/')) return route.continue();
    return handler(route);
  });
  await page.goto(frontend);
  await page.locator('.lg-btn').waitFor();
  return page;
}

async function mount(page, module, component, props = {}) {
  await page.evaluate(async ({ module, component, props }) => {
    const { default: React } = await import('/node_modules/.vite/deps/react.js');
    const exports = await import(module);
    window.__ERP_REACT_ROOT__.render(React.createElement(exports[component], {
      ...props, onClose: () => {}, onNotice: () => {}, onSave: () => {},
    }));
  }, { module, component, props });
}

test('login failure preserves form; successful login saves session and opens dashboard', async t => {
  let fail = true;
  const page = await pageFor(t, route => route.request().url().endsWith('/auth/login/')
    ? route.fulfill({ status: fail ? 400 : 200, json: fail ? { detail: 'Invalid credentials' }
      : { token: 'mock-only', username: 'audit', permissions: ['*'] } })
    : route.fulfill({ json: [] }));
  await page.locator('.lg-field input').first().fill('audit');
  await page.locator('input[type=password]').fill('mock');
  await page.locator('.lg-btn').click();
  await page.getByText('Invalid credentials').waitFor();
  assert.equal(await page.locator('.lg-field input').first().inputValue(), 'audit');
  fail = false;
  await page.locator('.lg-btn').click();
  await page.locator('.dashboard').waitFor();
  assert.equal(await page.evaluate(() => JSON.parse(localStorage.getItem('erp-session')).token), 'mock-only');
});

test('lookup restores selected code after uncommitted search and supports selecting another option', async t => {
  const page = await pageFor(t);
  await page.evaluate(async () => {
    const { default: R } = await import('/node_modules/.vite/deps/react.js');
    const { SearchableLookup } = await import('/src/components/Field.jsx');
    const options = [{ id: 1, code: 'A' }, { id: 2, code: 'B' }];
    const render = value => window.__ERP_REACT_ROOT__.render(R.createElement(SearchableLookup, { label: 'Audit', value,
      options, onChange: next => { window.selection = next; render(next); } }));
    render(1);
  });
  const lookup = page.locator('.lookup-field input');
  await lookup.fill('B');
  await lookup.press('Tab');
  await page.waitForFunction(() => document.querySelector('input').value === 'A');
  await lookup.fill('B');
  await page.locator('.lookup-menu button').click();
  assert.equal(await lookup.inputValue(), 'B');
  assert.equal(await page.evaluate(() => window.selection), 2);
});

test('failed replacement import cannot confirm old batch; retry confirms the new batch', async t => {
  let attempts = 0;
  const confirmations = [];
  const page = await pageFor(t, route => {
    const path = new URL(route.request().url()).pathname;
    if (path.endsWith('/preview/')) {
      attempts++;
      return route.fulfill({ status: attempts === 2 ? 400 : 201, json: attempts === 2
        ? { detail: 'Bad replacement' }
        : { id: attempts, status: 'preview', valid_rows: 1, error_rows: 0, total_rows: 1, rows: [] } });
    }
    confirmations.push(path);
    return route.fulfill({ json: { status: 'imported', imported_rows: 1, rows: [] } });
  });
  await mount(page, '/src/modules/purchase/MaterialImport.jsx', 'MaterialImport', { token: 'mock' });
  const upload = name => page.locator('input[type=file]').setInputFiles({ name, mimeType: 'application/vnd.ms-excel', buffer: Buffer.from('fixture') });
  await upload('first.xls');
  await page.locator('.toolbar .primary').waitFor();
  await upload('bad.xls');
  await page.getByText('Bad replacement').waitFor();
  assert.equal(await page.locator('.toolbar .primary').count(), 0);
  assert.deepEqual(confirmations, []);
  await upload('retry.xls');
  await page.locator('.toolbar .primary').click();
  await page.waitForFunction(() => !document.querySelector('.toolbar .primary'));
  assert.deepEqual(confirmations, ['/api/material-import/3/confirm/']);
});

test('shared form prevents duplicate requests and unlocks after failure without losing input', async t => {
  const page = await pageFor(t);
  await page.evaluate(async () => {
    const { default: R } = await import('/node_modules/.vite/deps/react.js');
    const { RecordModal } = await import('/src/components/ResourceModals.jsx');
    window.saves = 0;
    window.__ERP_REACT_ROOT__.render(R.createElement(RecordModal, {
      config: { title: 'Audit', fields: [{ key: 'name', label: 'Name' }] }, lookups: {}, onClose: () => {},
      onSave: async () => { window.saves++; try { await new Promise((resolve, reject) => { window.finish = resolve; window.fail = reject; }); } catch { /* Parent handlers display API errors. */ } },
    }));
  });
  await page.getByLabel('Name').fill('Kept value');
  await page.locator('.modal-foot .primary').click();
  assert.equal(await page.locator('.modal-foot .primary').isDisabled(), true);
  await page.locator('form').evaluate(form => form.requestSubmit());
  assert.equal(await page.evaluate(() => window.saves), 1);
  await page.evaluate(() => window.fail(new Error('offline')));
  await page.waitForFunction(() => !document.querySelector('fieldset').disabled);
  assert.equal(await page.getByLabel('Name').inputValue(), 'Kept value');
  await page.locator('.modal-foot .primary').click();
  assert.equal(await page.evaluate(() => window.saves), 2);
  await page.evaluate(() => window.finish());
});

test('history refetches for date and currency, shows errors and retries', async t => {
  let fail = false;
  const queries = [];
  const page = await pageFor(t, route => {
    queries.push(new URL(route.request().url()));
    return route.fulfill({ status: fail ? 503 : 200, json: fail ? { detail: 'History offline' }
      : { quote_number: 'HISTORY', unit_price: '10' } });
  });
  await mount(page, '/src/modules/sales/SalesQuoteModal.jsx', 'SalesQuoteModal', {
    token: 'mock', lookups: { currencies: [{ id: 1, code: 'CNY' }, { id: 2, code: 'USD' }] },
    record: { customer: 1, currency: 1, effective_date: '2026-09-01', lines: [{ material: 1, unit_price: '10' }] },
  });
  await page.locator('.quote-history-grid').waitFor();
  fail = true;
  await page.locator('input[type=date]').first().fill('2026-09-02');
  await page.getByRole('alert').waitFor();
  assert.equal(queries.at(-1).searchParams.get('date'), '2026-09-02');
  assert.match(await page.getByRole('alert').innerText(), /History offline/);
  fail = false;
  await page.getByRole('button', { name: '重试', exact: true }).click();
  await page.locator('.quote-history-grid').waitFor();
  await page.getByLabel('币种', { exact: false }).first().fill('USD');
  const changed = page.waitForResponse(r => r.url().includes('currency=2'));
  await page.locator('.lookup-menu button').click();
  await changed;
  assert.equal(queries.at(-1).searchParams.get('currency'), '2');
});

test('order ignores a quote response after its date changes', async t => {
  let release;
  const page = await pageFor(t, async route => {
    await new Promise(resolve => { release = resolve; });
    await route.fulfill({ json: { quote_line_id: 99, quote_number: 'STALE', unit_price: '99' } });
  });
  await mount(page, '/src/modules/sales/SalesOrderModal.jsx', 'SalesOrderModal', {
    token: 'mock', lookups: {}, record: { customer: 1, currency: 1, order_date: '2026-09-01',
      lines: [{ material: 1, customer_material: '', unit_price: '20', quantity: '1' }] },
  });
  const request = page.waitForRequest(r => r.url().includes('/previous/'));
  await page.getByRole('button', { name: '采用有效报价', exact: true }).click();
  await request;
  await page.getByLabel('下单日期', { exact: false }).fill('2026-09-02');
  release();
  await page.waitForFunction(() => !document.querySelector('button[aria-label="采用有效报价"]').disabled);
  const labels = await page.locator('.order-lines th').allTextContents();
  const price = page.locator('.order-lines tbody tr').first().locator('td').nth(labels.indexOf('订单单价')).locator('input');
  assert.equal(await price.inputValue(), '20');
  assert.equal(await page.getByText('STALE', { exact: true }).count(), 0);
});

test('lookup invalidation reloads deleted records and login reset clears cache', async t => {
  let customers = [{ id: 1, code: 'A', kind: 'customer' }];
  const page = await pageFor(t, route => route.fulfill({ json: route.request().url().endsWith('/partner/') ? customers : [] }));
  await page.evaluate(async () => {
    const { default: R } = await import('/node_modules/.vite/deps/react.js');
    const { useResourceData } = await import('/src/app/useResourceData.js');
    const session = { token: 'mock', permissions: ['*'] };
    function Harness() { const data = useResourceData(session, 'materialImport'); window.data = data;
      return R.createElement('pre', { id: 'lookup-state' }, JSON.stringify(data.lookups)); }
    window.__ERP_REACT_ROOT__.render(R.createElement(Harness));
  });
  await page.locator('#lookup-state').waitFor();
  await page.evaluate(() => window.data.loadConfig('salesQuotes'));
  await page.waitForFunction(() => window.data.lookups.customers?.length === 1);
  customers = [];
  await page.evaluate(async () => { window.data.invalidateLookup('partner'); await window.data.loadConfig('salesQuotes'); });
  await page.waitForFunction(() => window.data.lookups.customers?.length === 0);
  await page.evaluate(() => window.data.resetData());
  await page.waitForFunction(() => Object.keys(window.data.lookups).length === 0);
});

test('editor closes after successful action and delete and list refreshes', async t => {
  let rows = [{ id: 1, number: 'SO-AUDIT', customer: 1, status: 'draft', lines: [] }];
  const page = await pageFor(t, route => {
    const path = new URL(route.request().url()).pathname;
    if (path === '/api/auth/login/') return route.fulfill({ json: { token: 'mock', username: 'audit', permissions: ['*'] } });
    if (path.endsWith('/approve/')) { rows[0] = { ...rows[0], status: 'approved' }; return route.fulfill({ json: rows[0] }); }
    if (route.request().method() === 'DELETE') { rows = []; return route.fulfill({ status: 204 }); }
    if (path === '/api/sales-order/1/') return route.fulfill({ json: rows[0] });
    return route.fulfill({ json: path === '/api/sales-order/' ? rows : [] });
  });
  await page.locator('.lg-field input').first().fill('audit'); await page.locator('input[type=password]').fill('mock');
  await page.locator('.lg-btn').click(); await page.locator('.dashboard').waitFor();
  await page.getByRole('button', { name: '销售管理', exact: true }).click();
  await page.getByRole('button', { name: '客户订单', exact: true }).click();
  await page.getByRole('button', { name: '编辑', exact: true }).click();
  await page.locator('.sales-order-modal').waitFor();
  await page.locator('.sales-order-modal').getByRole('button', { name: '审核', exact: true }).click();
  await page.locator('.sales-order-modal').waitFor({ state: 'hidden' });
  assert.equal(await page.getByRole('button', { name: '编辑', exact: true }).count(), 0);
  rows[0].status = 'draft';
  await page.getByRole('button', { name: '刷新', exact: true }).click();
  await page.getByRole('button', { name: '编辑', exact: true }).click();
  page.once('dialog', dialog => dialog.accept());
  await page.locator('.sales-order-modal').getByRole('button', { name: '删除', exact: true }).click();
  await page.locator('.sales-order-modal').waitFor({ state: 'hidden' });
  assert.equal(await page.getByText('SO-AUDIT', { exact: true }).count(), 0);
});
