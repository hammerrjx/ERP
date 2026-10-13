const { test } = require('node:test');
const assert = require('node:assert/strict');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');

test('large customer material list renders a bounded page and returns from cache', async () => {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const page = await browser.newPage();
    page.on('pageerror', error => console.log(error.message));
    let requests = 0;
    const rows = Array.from({ length: 3000 }, (_, i) => ({ id: i + 1, customer_code: `CM-${i + 1}`, customer: 1, material: i + 1 }));
    await page.route('**/api/**', async route => {
      const path = new URL(route.request().url()).pathname;
      if (!path.startsWith('/api/')) return route.continue();
      if (path === '/api/customer-material/') requests++;
      await route.fulfill({ json: path === '/api/customer-material/' ? rows : [] });
    });
    await page.goto(process.env.ERP_FRONTEND_URL || 'http://127.0.0.1:5177');
    await page.evaluate(async () => {
      const { mount } = await import('/tests/fixtures/ListHarness.jsx');
      mount();
    });
    await page.getByText('CM-1', { exact: true }).waitFor();
    console.log('3000 rows, first display ms:', await page.evaluate(() => Math.round(performance.now() - window.started)));
    const rendered = await page.locator('tbody tr').count();
    console.log('rendered rows:', rendered);
    assert.ok(rendered <= 100, `Rendered ${rendered} rows instead of one page`);
    await page.getByRole('button', { name: '下一页', exact: true }).click();
    await page.getByText('CM-51', { exact: true }).waitFor();
    await page.evaluate(() => window.switchList('customers'));
    await page.waitForFunction(() => !document.querySelector('.table-loading'));
    await page.evaluate(() => window.switchList('customerMaterials'));
    await page.getByText('CM-1', { exact: true }).waitFor();
    assert.equal(requests, 1);
    await page.evaluate(() => window.refreshList());
    assert.equal(requests, 2);
    await page.evaluate(() => { window.invalidateList(); window.switchList('customers'); });
    await page.waitForFunction(() => !document.querySelector('.table-loading'));
    await page.evaluate(() => window.switchList('customerMaterials'));
    await page.getByText('CM-1', { exact: true }).waitFor();
    assert.equal(requests, 3);
    await page.evaluate(() => {
      const now = Date.now();
      Date.now = () => now + 31_000;
      window.switchList('customers');
    });
    await page.waitForFunction(() => !document.querySelector('.table-loading'));
    await page.evaluate(() => window.switchList('customerMaterials'));
    await page.getByText('CM-1', { exact: true }).waitFor();
    assert.equal(requests, 4, 'Expired cache must fetch current data');
    await page.locator('.table-foot').scrollIntoViewIfNeeded();
    await page.screenshot({ path: 'outputs/list-performance-desktop.png' });
    await page.setViewportSize({ width: 390, height: 844 });
    await page.locator('.table-foot').scrollIntoViewIfNeeded();
    await page.screenshot({ path: 'outputs/list-performance-mobile.png' });
  } finally { await browser.close(); }
});
