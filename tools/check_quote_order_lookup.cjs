// Render real components with a read-only API snapshot; all API requests are intercepted.
const { chromium } = require('C:/Users/LENOVO/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const fs = require('node:fs');
const assert = require('node:assert/strict');
const snapshot = JSON.parse(fs.readFileSync('tmp/quote-order-chain-snapshot.json', 'utf8'));

(async () => {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    let quoteResult = 'matched';
    await page.route('**/api/**', async route => {
      const url = new URL(route.request().url());
      if (!url.pathname.startsWith('/api/')) return route.continue();
      assert.equal(route.request().method(), 'GET', 'Diagnostic must never write business data');
      const resource = url.pathname.split('/')[2];
      let data = snapshot[resource] ? [snapshot[resource]] : [];
      if (url.pathname.endsWith('/previous/')) {
        if (quoteResult === 'error') return route.fulfill({ status: 503, json: { detail: 'Test quote service unavailable' } });
        data = quoteResult === 'empty' ? {} : snapshot.exact;
      }
      await route.fulfill({ json: data });
    });
    await page.addInitScript(() => localStorage.setItem('erp-session', JSON.stringify({
      token: 'intercepted-readonly-diagnostic', username: 'diagnostic', permissions: ['*'],
    })));
    // Register before navigation, because lookups may finish before the form opens.
    const materialLoaded = page.waitForResponse(response => response.url().endsWith('/api/material/'));
    await page.goto('http://127.0.0.1:5175');
    await page.getByRole('button', { name: '销售管理', exact: true }).click();
    await page.getByRole('button', { name: '销售报价', exact: true }).click();
    await materialLoaded;
    await page.getByRole('button', { name: '新增', exact: true }).click();
    await page.getByLabel('物料编码', { exact: false }).first().fill(snapshot.material.code);
    assert.equal(await page.locator('.lookup-menu button').filter({ hasText: snapshot.material.code }).count(), 1);
    await page.getByRole('button', { name: '取消', exact: true }).click();
    await page.getByRole('button', { name: '客户订单', exact: true }).click();
    await page.getByRole('button', { name: '新增', exact: true }).click();
    await page.getByLabel('客户代码', { exact: false }).fill(snapshot.partner.code);
    await page.locator('.lookup-menu button').filter({ hasText: snapshot.partner.code }).click();
    const input = page.locator('.order-lines').getByLabel('物料编码', { exact: true });
    await input.fill(snapshot.material.code);
    await page.locator('.order-lines .lookup-menu button').filter({ hasText: snapshot.material.code }).click();
    assert.equal(await page.locator('.order-lines').getByLabel('客户物料编码', { exact: true }).inputValue(), snapshot['customer-material'].customer_code);
    await page.getByRole('button', { name: '采用有效报价', exact: true }).click();
    await page.locator('.order-lines').getByText(snapshot['sales-quote'].number, { exact: true }).waitFor();
    const labels = await page.locator('.order-lines th').allTextContents();
    const cell = label => page.locator('.order-lines tbody tr').first().locator('td').nth(labels.indexOf(label)).locator('input');
    assert.equal(Number(await cell('订单单价').inputValue()), 20);
    await cell('订购数量').fill('950');
    await cell('备品数量').fill('50');
    assert.equal(Number(await cell('含税金额').inputValue()), 19000);
    await page.screenshot({ path: 'tmp/quote-order-lookup-fixed.png', fullPage: true });
    for (const result of ['error', 'empty']) {
      quoteResult = result;
      await page.getByRole('button', { name: '采用有效报价', exact: true }).click();
      await page.getByRole('alert').waitFor();
      assert.equal(Number(await cell('订单单价').inputValue()), 20);
      assert.equal(Number(await cell('含税金额').inputValue()), 19000);
      assert.equal(await page.locator('.order-lines').getByText(snapshot['sales-quote'].number, { exact: true }).count(), 1);
    }
    console.log('Passed: original material remains unchanged and selectable; exact customer item and quote resolve; 950+50 costs 19000; lookup failures preserve price and show feedback. No database writes.');
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
