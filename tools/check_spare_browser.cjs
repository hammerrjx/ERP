const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const apiUrl = process.env.ERP_TEST_API_URL || 'http://127.0.0.1:8013';
const frontendUrl = process.env.ERP_FRONTEND_URL || 'http://127.0.0.1:5175';

(async () => {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    const headers = { Authorization: 'Token spare-isolated-browser-test-token' };
    const existingResponse = await page.request.get(apiUrl + '/api/delivery-order/', { headers });
    assert.ok(existingResponse.ok(), 'Start tools/spare_browser_server.py before running this check');
    const existing = await existingResponse.json();
    for (const row of (existing.results || existing)) {
      if (!row.posted && row.status !== 'void') {
        const result = await page.request.post(`${apiUrl}/api/delivery-order/${row.id}/void/`, { headers });
        assert.ok(result.ok());
      }
    }
    await page.route('**/api/**', async route => {
      const url = new URL(route.request().url());
      if (!url.pathname.startsWith('/api/')) return route.continue();
      const response = await route.fetch({ url: apiUrl + url.pathname + url.search });
      await route.fulfill({ response });
    });
    await page.addInitScript(() => localStorage.setItem('erp-session', JSON.stringify({
      token: 'spare-isolated-browser-test-token', username: '隔离验收', permissions: ['*'],
    })));
    await page.goto(frontendUrl);
    await page.getByRole('button', { name: '销售管理', exact: true }).click();
    await page.getByRole('button', { name: '送货单', exact: true }).click();
    await page.getByRole('button', { name: '新增', exact: true }).click();
    await page.locator('#delivery-customer').fill('C001');
    await page.getByRole('button', { name: /C001 客户一/ }).click();
    await page.getByLabel('送货地址 / 实际收货厂区 *').fill('隔离验收收货仓');
    await page.getByRole('button', { name: '根据客户订单生成', exact: true }).click();
    await page.getByRole('button', { name: '是', exact: true }).click();
    const generator = page.getByRole('dialog', { name: '根据客户订单生成明细', exact: true });
    await generator.getByLabel('客户 PO', { exact: true }).fill('QA-MIXED-950');
    await generator.getByRole('button', { name: '查询', exact: true }).click();
    await generator.locator('tbody input[type=checkbox]').first().check();
    assert.equal(Number(await generator.getByLabel('本次备品数', { exact: true }).inputValue()), 50);
    await generator.getByLabel('本次送货数量', { exact: true }).fill('330');
    await generator.getByLabel('本次备品数', { exact: true }).fill('20');
    await generator.getByRole('button', { name: '生成', exact: true }).click();
    await page.getByRole('button', { name: '确定', exact: true }).click();
    const sheet = page.locator('.delivery-sheet');
    await page.screenshot({ path: 'tmp/spare-delivery-desktop.png', fullPage: true });
    assert.ok(await sheet.getByText('6600.00', { exact: true }).count());
    const cells = await sheet.locator('tbody tr').first().locator('td').allTextContents();
    assert.ok(cells.includes('350'));
    await page.setViewportSize({ width: 390, height: 844 });
    await page.screenshot({ path: 'tmp/spare-delivery-mobile.png', fullPage: true });
    const bounds = await sheet.boundingBox();
    assert.ok(bounds.x >= 0 && bounds.x + bounds.width <= 391);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), false);
    await page.setViewportSize({ width: 1440, height: 1000 });
    await page.getByRole('button', { name: '保存', exact: true }).last().click();
    await page.getByText('已创建送货单', { exact: true }).waitFor();
    await page.getByRole('button', { name: '客户订单', exact: true }).click();
    await page.getByRole('button', { name: '新增', exact: true }).click();
    await page.locator('.order-lines input[type=number]').first().waitFor();
    assert.equal(await page.locator('.order-lines input[type=number][min="0"]').count() > 0, true);
    await page.screenshot({ path: 'tmp/spare-order-desktop.png', fullPage: true });
    await page.getByLabel('客户代码', { exact: false }).fill('C001');
    await page.getByRole('button', { name: /C001客户一|C001 客户一/ }).click();
    await page.getByRole('textbox', { name: '客户 PO*', exact: true }).fill('QA-BROWSER-SPARE');
    await page.getByLabel('送货地址', { exact: false }).fill('隔离验收收货仓');
    await page.locator('.order-lines').getByLabel('物料编码', { exact: true }).fill('FG-001');
    await page.getByRole('button', { name: /FG-001交付产品|FG-001 交付产品/ }).click();
    const labels = await page.locator('.order-lines th').allTextContents();
    const cell = label => page.locator('.order-lines tbody tr').first().locator('td').nth(labels.indexOf(label));
    await cell('订购数量').locator('input').fill('0');
    await cell('备品数量').locator('input').fill('50');
    await page.getByLabel('承诺交期', { exact: false }).fill('2026-09-08');
    const savedOrder = page.waitForResponse(response => response.url().endsWith('/api/sales-order/') && response.request().method() === 'POST');
    await page.getByRole('button', { name: '保存草稿', exact: true }).click();
    const invalid = await page.locator('input:invalid,select:invalid').evaluateAll(nodes => nodes.map(node => node.closest('label')?.textContent || node.validationMessage));
    assert.deepEqual(invalid, []);
    const savedResponse = await savedOrder;
    assert.ok(savedResponse.ok(), await savedResponse.text());
    await page.getByRole('button', { name: '保存草稿', exact: true }).waitFor({ state: 'hidden' });
    const ordersResponse = await page.request.get(apiUrl + '/api/sales-order/', { headers });
    const orders = await ordersResponse.json();
    const created = (orders.results || orders).find(order => order.customer_po === 'QA-BROWSER-SPARE');
    assert.ok(created);
    const detail = await (await page.request.get(`${apiUrl}/api/sales-order/${created.id}/`, { headers })).json();
    assert.equal(Number(detail.lines[0].quantity), 0);
    assert.equal(Number(detail.lines[0].spare_quantity), 50);
    assert.deepEqual(errors, []);
    console.log('PASS: mixed quantities, spare default, free spare amount, save, desktop/mobile bounds, order zero inputs.');
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
