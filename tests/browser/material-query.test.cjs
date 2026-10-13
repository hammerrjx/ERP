const { test } = require('node:test');
const assert = require('node:assert/strict');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const base = process.env.ERP_FRONTEND_URL || 'http://127.0.0.1:5186';

test('material entry is empty; server filters, pages and cross-page record navigation', async () => {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    const calls = [], errors = [];
    page.on('pageerror', e => errors.push(e.message));
    const rows = Array.from({ length: 105 }, (_, i) => ({ id: i + 1, code: `TEST-${String(i).padStart(3, '0')}`, name: '分页测试物料', status: 'draft', active: false }));
    await page.route('**/api/**', async route => {
      const url = new URL(route.request().url());
      if (!url.pathname.startsWith('/api/')) return route.continue();
      calls.push(url.pathname + url.search);
      if (url.pathname === '/api/material/search/') {
        const number = Number(url.searchParams.get('page') || 1), size = Number(url.searchParams.get('page_size') || 50);
        return route.fulfill({ json: { results: rows.slice((number - 1) * size, number * size), count: rows.length, page: number, page_size: size } });
      }
      const id = url.pathname.match(/^\/api\/material\/(\d+)\/$/);
      if (id) return route.fulfill({ json: rows[Number(id[1]) - 1] });
      return route.fulfill({ json: [] });
    });
    await page.goto(base);
    await page.evaluate(async () => (await import('/tests/fixtures/MaterialHarness.jsx')).mount());
    await page.getByText('点击查询显示全部物料，输入条件后查询显示匹配物料', { exact: true }).waitFor();
    assert.equal(calls.length, 0);
    await page.getByRole('button', { name: '查询', exact: true }).click();
    await page.getByRole('button', { name: 'TEST-000', exact: true }).waitFor();
    assert.equal(await page.locator('tbody tr').count(), 50);
    assert.ok(calls.some(x => x.includes('code=&') && x.includes('page_size=50')));
    await page.getByLabel('物料编码', { exact: true }).fill('TEST-');
    await page.getByRole('button', { name: '查询', exact: true }).click();
    await page.getByRole('button', { name: 'TEST-000', exact: true }).waitFor();
    assert.equal(await page.locator('tbody tr').count(), 50);
    assert.ok(calls.some(x => x.includes('code=TEST-')));
    await page.getByRole('button', { name: '下一页', exact: true }).click();
    await page.getByRole('button', { name: 'TEST-099', exact: true }).click();
    await page.getByRole('button', { name: '下笔', exact: true }).click();
    await page.waitForFunction(() => document.querySelector('.mt-head input')?.value === 'TEST-100');
    await page.getByRole('button', { name: '末笔', exact: true }).click();
    await page.waitForFunction(() => document.querySelector('.mt-head input')?.value === 'TEST-104');
    await page.getByRole('button', { name: '资料浏览', exact: true }).click();
    assert.equal(await page.locator('tbody tr').count(), 5);
    assert.ok(!calls.some(x => x === '/api/material/'));
    await page.screenshot({ path: 'outputs/material-query-paged.png' });
    assert.deepEqual(errors, []);
  } finally { await browser.close(); }
});

test('inventory details show pending state and ignore late results', async () => {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    const pending = [];
    await page.route('**/api/**', async route => {
      const url = new URL(route.request().url());
      if (!url.pathname.startsWith('/api/')) return route.continue();
      if (url.pathname.endsWith('/choices/')) return route.fulfill({ json: { periods: [], cost_types: {}, location_types: {} } });
      if (url.pathname.endsWith('/details/')) {
        pending.push({ route, tab: url.searchParams.get('tab') });
        return;
      }
      return route.fulfill({ json: { columns: [['tmp_part', '物料编码']], numeric_columns: [], results: [{ tmp_part: 'ZXX-000215' }], count: 1, totals: {} } });
    });
    await page.goto(base);
    await page.evaluate(async () => (await import('/tests/fixtures/InventoryAnalysisHarness.jsx')).mount());
    await page.getByRole('button', { name: 'ZXX-000215', exact: true }).click();
    await page.getByText('正在加载明细…', { exact: true }).waitFor();
    assert.equal(await page.getByText('无明细数据', { exact: true }).count(), 0);
    await page.getByRole('tab', { name: '请购中明细', exact: true }).click();
    await page.waitForResponse(async response => false, { timeout: 100 }).catch(() => {});
    const latest = pending.find(r => r.tab === 'requisition');
    assert.ok(latest);
    await latest.route.fulfill({ json: { results: [{ kind: '当前请购', quantity: '100' }], total: '100' } });
    await page.getByText('当前请购', { exact: true }).waitFor();
    await pending[0].route.fulfill({ json: { results: [{ kind: '旧库存', quantity: '9' }], total: '9' } }).catch(() => {});
    assert.equal(await page.getByText('旧库存', { exact: true }).count(), 0);
    await page.screenshot({ path: 'outputs/inventory-detail-query.png' });
  } finally { await browser.close(); }
});
