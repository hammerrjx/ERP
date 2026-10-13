const { test } = require('node:test');
const assert = require('node:assert/strict');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');

test('return sheet selects native association, sends only editable values and locks posted rows', async () => {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1680, height: 1000 } });
    const errors = [], writes = [];
    page.on('pageerror', e => errors.push(e.message));
    page.on('console', e => { if (e.type() === 'error') errors.push(e.text()); });
    let doc;
    await page.route('**/api/**', async route => {
      const req = route.request(), url = new URL(req.url()), path = url.pathname;
      if (!path.startsWith('/api/')) return route.continue();
      let json = [];
      if (path === '/api/partner/') json = [{ id: 1, code: 'C001', name: '测试客户', kind: 'customer', currency: 1, tax_rate: '13' }];
      if (path === '/api/currency/') json = [{ id: 1, code: 'RMB', name: '人民币' }];
      if (path === '/api/location/') json = [{ id: 1, code: 'FG01', name: '测试成品仓', source_site: '1000' }];
      if (path.endsWith('/defaults/')) json = { posting_enabled: true, groups: [{ code: 'IT01', name: '测试业务员' }], addresses: [], default_print_person: '测试打印人' };
      if (path.endsWith('/candidates/')) json = { count: 1, page: 1, results: [{ id: '1:1', material: 1, customer_material: 1, material_code: 'MAT-001', material_name: '测试物料', material_specification: '规格', customer_material_code: 'CP-001', terminal_customer_code: 'END-001', terminal_customer_name: '终端物料', uom_name: '箱', inventory_uom_name: '个', uom_rate_m: '12', uom_rate_d: '1', return_location: 1 }] };
      if (path === '/api/no-order-return/' && req.method() === 'POST') {
        const body = req.postDataJSON(); writes.push(body);
        assert.equal(body.exchange_rate, undefined); assert.equal(body.number, undefined);
        assert.equal(body.lines[0].uom_rate_m, undefined);
        assert.equal(body.lines[0].customer_material, 1);
        doc = { ...body, id: 1, revision: 1, status: 'draft', number: 'MYSN26090001', posted: false, exchange_rate: '1', lines: body.lines.map(l => ({ ...l, id: 1, line_number: 10, material_code: 'MAT-001', material_name: '测试物料', customer_material_code: 'CP-001', terminal_customer_code: 'END-001', terminal_customer_name: '终端物料', uom_name: '箱', inventory_uom_name: '个', uom_rate_m: '12', uom_rate_d: '1' })) };
        return route.fulfill({ status: 201, json: doc });
      }
      if (path.endsWith('/approve/')) { doc = { ...doc, posted: true, posting_version: 1, status: 'approved', revision: 2 }; json = doc; }
      if (path === '/api/no-order-return/' && req.method() === 'GET') json = { count: doc ? 1 : 0, results: doc ? [doc] : [] };
      if (path === '/api/no-order-return/1/') json = doc;
      return route.fulfill({ json });
    });
    await page.goto(process.env.ERP_RETURN_FRONTEND_URL || 'http://127.0.0.1:5191');
    await page.evaluate(async () => (await import('/tests/fixtures/NoOrderReturnHarness.jsx')).mount());
    await page.getByRole('button', { name: '增加明细', exact: true }).waitFor();
    await page.getByRole('combobox', { name: '客户代码', exact: true }).fill('C001');
    await page.getByRole('option', { name: /C001/ }).click();
    await page.getByLabel('客户PO', { exact: true }).fill('PO-TEST');
    await page.getByRole('combobox', { name: '业务组别', exact: true }).fill('IT01');
    await page.getByRole('option', { name: /IT01/ }).click();
    await page.getByRole('button', { name: '增加明细', exact: true }).click();
    await page.getByRole('button', { name: '检索物料', exact: true }).click();
    await page.getByRole('dialog').getByRole('button', { name: /MAT-001/ }).click();
    await page.getByLabel('退货数量第10行', { exact: true }).fill('100');
    await page.getByLabel('单价第10行', { exact: true }).fill('1.005');
    assert.equal(await page.getByRole('cell', { name: '100.50', exact: true }).count(), 2);
    assert.equal(await page.getByRole('cell', { name: 'END-001', exact: true }).count(), 1);
    await page.getByRole('button', { name: '保存', exact: true }).click();
    await page.getByRole('status').getByText('已保存', { exact: true }).waitFor();
    assert.equal(writes.length, 1);
    await page.getByRole('button', { name: '审核', exact: true }).click();
    await page.getByText('已审核', { exact: true }).waitFor();
    assert.equal(await page.getByLabel('退货数量第10行', { exact: true }).isDisabled(), true);
    assert.equal(await page.getByRole('button', { name: '增加明细', exact: true }).isDisabled(), true);
    await page.screenshot({ path: 'outputs/no-order-return-plan/无订单退货桌面.png', fullPage: true });
    await page.setViewportSize({ width: 1024, height: 768 });
    await page.screenshot({ path: 'outputs/no-order-return-plan/无订单退货窄屏.png', fullPage: true });
    assert.deepEqual(errors, []);
  } finally { await browser.close(); }
});
