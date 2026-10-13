const { test } = require('node:test');
const assert = require('node:assert/strict');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');

test('real ledger entry keeps range filters without a snapshot and still renders local inventory', async () => {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const page = await browser.newPage();
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.route('**/api/**', async route => {
      const url = new URL(route.request().url());
      if (!url.pathname.startsWith('/api/')) return route.continue();
      if (url.pathname.endsWith('/availability/')) return route.fulfill({ json: { ready: false } });
      if (/material-(inventory|movement)-detail/.test(url.pathname)) {
        assert.equal(url.searchParams.get('source'), 'local');
        return route.fulfill({ json: { count: 0, results: [], columns: [['material_code', '物料编码']], batch: null, page: 1 } });
      }
      return route.fulfill({ json: [] });
    });
    await page.goto(process.env.ERP_FRONTEND_URL || 'http://127.0.0.1:5173');
    await page.evaluate(async () => (await import('/tests/fixtures/InventoryReportsHarness.jsx')).mount());
    await page.locator('.ir-grid').getByText('尚未同步报表数据', { exact: true }).waitFor();
    for (const label of ['物料编码', '产品类', '库位', '批号']) {
      assert.equal(await page.getByLabel(`${label}起始`, { exact: true }).count(), 1);
      assert.equal(await page.getByLabel(`${label}结束`, { exact: true }).count(), 1);
    }
    assert.equal(await page.getByLabel('搜索库存', { exact: true }).count(), 0);
    assert.equal(await page.getByRole('button', { name: '导出', exact: true }).isDisabled(), true);
    await page.getByLabel('物料编码起始', { exact: true }).fill('ZZJ-00002');
    await page.evaluate(() => window.selectMovementReport());
    await page.locator('.ir-grid').getByText('尚未同步报表数据', { exact: true }).waitFor();
    assert.equal(await page.getByLabel('物料编码起始', { exact: true }).inputValue(), '');
    assert.equal(await page.getByLabel('进出类型', { exact: true }).count(), 1);
    assert.equal(await page.getByLabel('仓管员', { exact: true }).count(), 1);
    await page.evaluate(() => window.selectInventoryResource('stock-balance'));
    await page.getByLabel('搜索库存', { exact: true }).waitFor();
    assert.deepEqual(errors, []);
  } finally { await browser.close(); }
});

test('inventory report paging, applied filters, lookup, export and responsive layout', async () => {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1500, height: 980 } });
    const calls = [], exports = [], errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.route('**/api/**', async route => {
      const request = route.request(), url = new URL(request.url());
      if (!url.pathname.startsWith('/api/')) return route.continue();
      if (url.pathname.endsWith('/export/')) {
        exports.push(request.postDataJSON());
        return route.fulfill({ body: 'test-export', headers: { 'content-disposition': "attachment; filename*=UTF-8''report.xlsx", 'content-type': 'application/octet-stream' } });
      }
      if (url.pathname.endsWith('/lookup/')) return route.fulfill({ json: { count: 1, page: 1, page_size: 50, results: [{ code: 'ZZJ-00002', name: '检索测试物料', specification: '测试规格', site: '' }] } });
      if (url.pathname.includes('material-inventory-detail') || url.pathname.includes('material-movement-detail')) {
        calls.push(Object.fromEntries(url.searchParams));
        const offset = (Number(url.searchParams.get('page')) - 1) * 100;
        return route.fulfill({ json: { count: 205711, page: Number(url.searchParams.get('page')), batch: { id: 7, finished_at: '2026-09-16T16:00:00', date_from: '2026-01-01', date_to: '2026-12-31' },
          columns: [['material_code', '物料编码'], ['material_name', '物料名称'], ['quantity', '库存数量'], ['batch_number', '批号'], ['standard_cost', '单位标准成本']],
          results: Array.from({ length: 100 }, (_, i) => ({ id: offset + i + 1, material_code: `ZZJ-${String(offset + i + 1).padStart(5, '0')}`, material_name: '浏览器测试物料', quantity: '0', batch_number: '00001', standard_cost: null })) } });
      }
      return route.fulfill({ json: [] });
    });
    await page.goto(process.env.ERP_FRONTEND_URL || 'http://127.0.0.1:5173');
    await page.evaluate(async () => (await import('/tests/fixtures/InventoryReportsHarness.jsx')).mount());
    await page.getByText('ZZJ-00001', { exact: true }).waitFor();
    assert.equal(await page.locator('.ir-grid tbody tr').count(), 100);
    assert.equal(calls.at(-1).page_size, '100');
    const resize = page.getByRole('separator', { name: '物料编码列宽', exact: true });
    await resize.focus(); await page.keyboard.press('ArrowRight');
    assert.equal(await resize.getAttribute('aria-valuenow'), '140');
    await page.getByRole('button', { name: '恢复默认栏位设置', exact: true }).click();
    assert.equal(await resize.getAttribute('aria-valuenow'), '130');
    await page.getByLabel('物料编码起始', { exact: true }).fill('ZZJ-00002');
    await page.getByRole('button', { name: '下一页', exact: true }).click();
    await page.getByText('ZZJ-00101', { exact: true }).waitFor();
    assert.equal(calls.at(-1).material_from, undefined, 'draft filters must not change paging');
    assert.equal(calls.at(-1).batch_id, '7');
    await page.locator('.ir-toolbar').getByRole('button', { name: '查询', exact: true }).click();
    await page.getByText('ZZJ-00001', { exact: true }).waitFor();
    assert.equal(calls.at(-1).material_from, 'ZZJ-00002');
    await page.getByRole('button', { name: '检索物料编码结束', exact: true }).click();
    const dialog = page.getByRole('dialog');
    await dialog.getByText('检索测试物料', { exact: true }).waitFor();
    await dialog.getByRole('button', { name: 'ZZJ-00002', exact: true }).dblclick();
    assert.equal(await page.getByLabel('物料编码结束', { exact: true }).inputValue(), 'ZZJ-00002');
    const completed = page.waitForEvent('download');
    await page.getByRole('button', { name: '导出', exact: true }).click();
    await completed;
    assert.equal(exports.at(-1).filters.batch_id, 7);
    assert.equal(exports.at(-1).filters.material_to, undefined, 'export must use last executed filters');
    await page.screenshot({ path: 'outputs/inventory-reports-desktop.png' });
    await page.evaluate(() => window.selectMovementReport());
    await page.getByLabel('审核日期结束', { exact: true }).waitFor();
    await page.getByText('ZZJ-00001', { exact: true }).waitFor();
    await page.screenshot({ path: 'outputs/movement-report-desktop.png' });
    await page.setViewportSize({ width: 390, height: 844 });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 2), false);
    await page.screenshot({ path: 'outputs/movement-report-mobile.png', fullPage: true });
    assert.deepEqual(errors, []);
  } finally { await browser.close(); }
});
