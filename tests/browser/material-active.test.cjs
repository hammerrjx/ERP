const { test } = require('node:test');
const assert = require('node:assert/strict');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');

test('engineering checkbox preserves false, approval lock, cancel, failure and other tabs', async () => {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    const errors = []; page.on('pageerror', e => errors.push(e.message));
    let row = { id: 965, code: 'PCC-000051', name: '工程属性测试物料', specification: '测试规格', active: false, status: 'approved' };
    let fail = false; const patches = []; let searches = 0;
    await page.route('**/api/**', async route => {
      const req = route.request(), path = new URL(req.url()).pathname;
      if (!path.startsWith('/api/')) return route.continue();
      if (path === '/api/material/') throw new Error('Must not fetch all materials');
      if (path === '/api/material/search/') { searches++; return route.fulfill({ json: {results:[row],count:1,page:1,page_size:50} }); }
      if (path === '/api/material/965/' && req.method() === 'GET') return route.fulfill({json:row});
      if (req.method() === 'PATCH') {
        const body = req.postDataJSON(); patches.push(body);
        if (fail) return route.fulfill({ status: 400, json: { detail: '测试保存失败' } });
        row = { ...row, ...body }; return route.fulfill({ json: row });
      }
      if (path.endsWith('/unapprove/')) { row.status = 'draft'; return route.fulfill({ json: row }); }
      return route.fulfill({ json: [] });
    });
    await page.goto(process.env.ERP_FRONTEND_URL || 'http://127.0.0.1:5173');
    const mount = permissions => page.evaluate(async p => (await import('/tests/fixtures/MaterialHarness.jsx')).mount(p), permissions);
    await mount(['*']);
    const button = name => page.getByRole('button', { name, exact: true });
    const engineering = () => button('工程属性').click();
    const checkbox = page.getByRole('checkbox', { name: '使用中', exact: true });
    assert.equal(searches, 0); await button('查询').click(); await button('PCC-000051').click(); await engineering();
    assert.equal(await checkbox.isChecked(), false); assert.equal(await checkbox.isDisabled(), true);
    await page.getByText('请先反审核，修改并保存后重新提交、审核。反审核期间，该物料暂不可用于新增请购、采购。').waitFor();
    await page.screenshot({ path: 'outputs/material-engineering-active-desktop.png' });
    for (const name of ['基本属性', '库存属性', 'MRP 属性']) {
      await button(name).click(); assert.equal(await checkbox.count(), 0);
      assert.equal(await page.locator('.mt-use-help').count(), 0);
    }
    await button('反审核').click(); await engineering(); await checkbox.check();
    page.on('dialog', d => d.accept()); await button('取消').click(); await engineering();
    assert.equal(await checkbox.isChecked(), false);
    await checkbox.check(); await button('保存').click(); await page.getByText('已保存物料', { exact: true }).waitFor();
    assert.equal(patches.at(-1).active, true);
    await engineering(); await checkbox.uncheck(); await button('保存').click();
    await page.waitForFunction(() => document.querySelector('.sw-notice')?.textContent === '已保存物料');
    assert.equal(patches.at(-1).active, false); assert.equal(row.active, false);
    await engineering(); await checkbox.check(); fail = true; await button('保存').click();
    await page.getByText('测试保存失败', { exact: true }).waitFor(); assert.equal(row.active, false);
    assert.equal(await page.locator('.sw-notice').count(), 0);
    await button('取消').click(); await button('新增').click(); await engineering();
    assert.equal(await checkbox.isChecked(), true);
    await page.setViewportSize({ width: 390, height: 844 });
    await page.screenshot({ path: 'outputs/material-engineering-active-mobile.png' });
    const box = await page.locator('.mt-use-state').boundingBox(); assert.ok(box.x >= 0 && box.x + box.width <= 390);
    await mount(['material.view']); await button('查询').click(); await button('PCC-000051').click(); await engineering();
    assert.equal(await checkbox.isDisabled(), true);
    assert.deepEqual(errors, []);
  } finally { await browser.close(); }
});
