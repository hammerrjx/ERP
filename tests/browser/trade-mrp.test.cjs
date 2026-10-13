const { test } = require('node:test');
const assert = require('node:assert/strict');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');

test('trade MRP real API: navigation, four views, partial selection, adjustment, generation and repeat preview', async () => {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.addInitScript(() => localStorage.setItem('erp-session', JSON.stringify({ token: 'trade-mrp-isolated-test-token', username: 'flow-admin', permissions: ['*'] })));
    await page.goto(process.env.MRP_BROWSER_URL || 'http://127.0.0.1:5196');
    await page.getByRole('button', { name: '采购管理', exact: true }).click();
    await page.locator('.subnav').getByRole('button', { name: '贸易端MRP', exact: true }).click();
    await page.getByText('更多查询条件 · 客户 / 料号映射', { exact: true }).click();
    await page.getByLabel('物料编码或名称', { exact: true }).fill('FG-001');
    await page.getByRole('button', { name: '查询', exact: true }).click();
    const detail = page.getByRole('region', { name: '需求明细', exact: true });
    await detail.getByRole('cell', { name: 'MRP-TEST-01', exact: true }).first().waitFor();
    assert.equal(await detail.locator('tbody tr').count(), 2);
    await page.getByText('更多查询条件 · 客户 / 料号映射', { exact: true }).click();
    await page.screenshot({ path: 'outputs/trade-mrp-ui-20261006/browser-detail.png', fullPage: true });
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.screenshot({ path: 'outputs/trade-mrp-ui-20261006/browser-1920.png', fullPage: true });
    await page.setViewportSize({ width: 1440, height: 1000 });
    await page.getByRole('button', { name: '按单据汇总', exact: true }).click();
    assert.equal(await page.getByRole('region', { name: '按单据汇总', exact: true }).locator('tbody tr').count(), 2);
    await page.getByRole('button', { name: '按物料＋需求日期汇总', exact: true }).click();
    assert.equal(await page.getByRole('region', { name: '按物料＋需求日期汇总', exact: true }).locator('tbody tr').count(), 2);
    await page.getByRole('button', { name: '需求明细', exact: true }).click();
    await page.getByLabel('选择 MRP-TEST-02/10', { exact: true }).uncheck();
    const input = page.getByLabel('本次请购 MRP-TEST-01/10', { exact: true });
    assert.equal(Number(await input.inputValue()), 5);
    await page.getByRole('button', { name: '相同值', exact: true }).click();
    await page.getByLabel('相同请购数量', { exact: true }).fill('4.125');
    await page.getByRole('button', { name: '应用到已选来源', exact: true }).click();
    assert.equal(await input.inputValue(), '4.125');
    await page.getByLabel('人工调整原因（修改本次请购量时必填）').fill('浏览器隔离验收：分批购买');
    await page.screenshot({ path: 'outputs/trade-mrp-ui-20261006/browser-material.png', fullPage: true });
    await page.getByRole('button', { name: '生成预览', exact: true }).click();
    const dialog = page.getByRole('dialog', { name: '确认生成标准请购', exact: true });
    await dialog.waitFor();
    assert.equal(await dialog.getByText('MRP-TEST-02/10', { exact: true }).count(), 0);
    await page.screenshot({ path: 'outputs/trade-mrp-ui-20261006/browser-confirm.png', fullPage: true });
    await dialog.getByRole('button', { name: '确认生成 P 型请购', exact: true }).click();
    await page.getByRole('status').filter({ hasText: '已生成标准P型请购草稿' }).waitFor();
    const docs = await page.evaluate(async () => {
      const headers = { Authorization: 'Token trade-mrp-isolated-test-token' };
      const history = await (await fetch('/api/trade-mrp/', { headers })).json();
      const run = history.results.find(r => r.status === 'confirmed');
      return await (await fetch(`/api/purchase-requisition/${run.confirmation_snapshot.requisition_id}/`, { headers })).json();
    });
    assert.equal(docs.status, 'draft');
    assert.equal(Number(docs.lines[0].requested_qty), 4.125);
    assert.equal(docs.lines[0].sources.length, 1);
    assert.equal(docs.lines[0].sources[0].source_number, 'MRP-TEST-01');
    await page.getByRole('button', { name: '查询', exact: true }).click();
    await page.getByLabel('本次请购 MRP-TEST-01/10', { exact: true }).waitFor();
    await page.getByRole('button', { name: '按物料汇总', exact: true }).click();
    assert.equal(Number(await page.getByLabel('本次请购合计 FG-001', { exact: true }).innerText()), 20.875);
    await page.getByRole('button', { name: '查看构成', exact: true }).click();
    await page.getByRole('region', { name: '供需构成', exact: true }).waitFor();
    await page.getByRole('button', { name: '关闭构成', exact: true }).click();
    await page.getByRole('button', { name: '历史运算', exact: true }).click();
    await page.getByRole('region', { name: '历史运算', exact: true }).waitFor();
    await page.getByRole('button', { name: '关闭历史', exact: true }).click();
    assert.deepEqual(errors, []);
    await page.setViewportSize({ width: 1024, height: 768 });
    await page.screenshot({ path: 'outputs/trade-mrp-ui-20261006/browser-1024.png', fullPage: true });
    const concurrent = await page.evaluate(async () => {
      const post = async (path, body) => {
        const response = await fetch(`/api/trade-mrp/${path}`, { method: 'POST',
          headers: { Authorization: 'Token trade-mrp-isolated-test-token', 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
        return { status: response.status, data: await response.json() };
      };
      const a = await post('preview/', { material: 'FG-001' });
      const b = await post('preview/', { material: 'FG-001' });
      return (await Promise.all([post(`${a.data.id}/confirm/`, {}), post(`${b.data.id}/confirm/`, {})])).map(r => r.status).sort();
    });
    assert.deepEqual(concurrent, [201, 400]);
    await page.getByText('更多查询条件 · 客户 / 料号映射', { exact: true }).click();
    await page.getByLabel('物料编码或名称', { exact: true }).fill('UNIT-BLOCK');
    await page.getByRole('button', { name: '查询', exact: true }).click();
    await page.getByRole('alert').filter({ hasText: '单位换算不是有效1:1' }).waitFor();
    assert.equal(await page.getByRole('button', { name: '生成预览', exact: true }).isDisabled(), true);
    await page.screenshot({ path: 'outputs/trade-mrp-ui-20261006/browser-unit-block.png', fullPage: true });
  } finally { await browser.close(); }
});
