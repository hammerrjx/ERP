const { test } = require('node:test');

const assert = require('node:assert/strict');

const fs = require('node:fs');

const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');



test('real isolated API: query, supplier, preview, generate, linked tables, save and approve', async () => {

  const fixture = JSON.parse(fs.readFileSync(process.env.ERP_PURCHASE_FIXTURE || 'outputs/purchase-replan-20260922/browser-fixture.json', 'utf8'));

  const browser = await chromium.launch({ channel: 'msedge', headless: true });

  try {

    const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });

    const errors = []; page.on('pageerror', e => { errors.push(e.message); console.error(e.message) });

    await page.addInitScript(token => localStorage.setItem('erp-session',JSON.stringify({token,username:'flow-admin',permissions:['*']})),fixture.token);

    await page.goto(process.env.ERP_PURCHASE_FRONTEND_URL || 'http://127.0.0.1:5194');

    await page.getByRole('button',{name:'采购管理',exact:true}).click();

    await page.locator('.subnav').getByRole('button',{name:'请购单转采购单',exact:true}).click();
    const calculations = await page.evaluate(async () => {
      const { amounts, converted, sum } = await import('/src/modules/purchase/PurchaseControls.jsx');
      return { total: sum([[2,2340],[850,12],[6,720]].map(([q,p]) => amounts(q,p,13).untaxed_amount)),
        converted: converted('20','1','10'), zero: amounts('2','0','13').amount,
        exponential: sum(['1e3','2.5']) };
    });
    assert.deepEqual(calculations, {total:'16991.18000000',converted:'2.00000000',zero:'0.00000000',exponential:'1002.50000000'});
    await page.getByLabel('请购单号起', { exact: true }).fill(fixture.request_number);

    await page.getByLabel('请购单号止', { exact: true }).fill(fixture.request_number);

    await page.getByRole('button', { name: '查询', exact: true }).click();

    await page.getByText('RHY-000018', { exact: true }).waitFor();

    await page.getByRole('button', { name: '全选本页', exact: true }).click();

    await page.getByRole('button', { name: '检索统一采购部门', exact: true }).click();

    await page.getByRole('dialog').getByRole('button', { name: /PTEST/ }).click();

    for (const [line,price] of [[10,'2340'],[20,'12'],[30,'720']]) {

      await page.getByLabel(`本次单价${fixture.request_number}行${line}`, { exact: true }).fill(price);

    }

    await page.screenshot({ path:'outputs/purchase-recovery-20260922/browser-conversion.png', fullPage:true });

    await page.getByRole('button', { name: '提交', exact: true }).click();

    await page.getByRole('dialog', { name: '继续生成采购单', exact: true }).waitFor();

    await page.screenshot({ path:'outputs/purchase-recovery-20260922/browser-preview.png', fullPage:true });

    await page.getByLabel('预览新单价第3行',{exact:true}).fill('720');

    await page.getByRole('button',{name:'重新核价',exact:true}).click();

    await page.getByRole('button', { name:'继续生成', exact:true }).click();

    await page.getByRole('dialog', { name:'查看采购单', exact:true }).waitFor();

    await page.getByRole('button', { name:'是', exact:true }).click();

    const upper=page.getByRole('region',{name:'采购明细',exact:true});

    const lower=page.getByRole('region',{name:'关联请购明细',exact:true});

    await upper.getByRole('button',{name:'RHY-000018',exact:true}).waitFor();

    assert.equal(await upper.locator('thead th').count(),55);

    assert.equal(await lower.locator('thead th').count(),17);

    await upper.getByRole('button',{name:'RHY-000011',exact:true}).click();

    await lower.getByRole('cell',{name:'磨削液Hysol/EP690/18L/桶/品牌：嘉实多',exact:true}).waitFor();

    assert.equal(await lower.locator('tbody:not(.pu-grid-space) tr').count(),1);

    assert.equal(await lower.getByLabel('来源采购数量第10行',{exact:true}).inputValue(),'6.00000000');

    await page.screenshot({path:'outputs/purchase-recovery-20260922/browser-order-1920.png',fullPage:true});

    await page.setViewportSize({width:1366,height:768});

    await page.screenshot({path:'outputs/purchase-recovery-20260922/browser-order-1366.png',fullPage:true});

    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth<=window.innerWidth),true);

    assert.ok((await lower.boundingBox()).y + (await lower.boundingBox()).height < 768, 'lower allocation grid stays in viewport');

    assert.ok(await page.locator('.pu-status').isVisible());

    await page.getByLabel('含税单价第30行',{exact:true}).fill('720');

    await page.getByRole('button',{name:'保存',exact:true}).click();

    await page.getByRole('status').getByText('已保存',{exact:true}).waitFor();

    await page.getByRole('button',{name:'审核',exact:true}).click();

    await page.locator('.pu-stamp.approved').waitFor();

    assert.equal(await page.getByLabel('订购数量第30行',{exact:true}).isDisabled(),true);

    await page.screenshot({path:'outputs/purchase-recovery-20260922/browser-approved.png',fullPage:true});

    await page.getByRole('button',{name:'预览',exact:true}).click();

    assert.ok(await page.locator('.pu-print-sheet').isVisible());

    await page.screenshot({path:'outputs/purchase-recovery-20260922/browser-print.png',fullPage:true});

    await page.emulateMedia({media:'print'});

    await page.pdf({path:'outputs/purchase-replan-20260922/采购单打印样例.pdf',preferCSSPageSize:true});

    assert.deepEqual(errors,[]);

  } finally { await browser.close(); }

});

test('cancel preview creates nothing; answering No keeps generated purchase order', async () => {
  const fixture=JSON.parse(fs.readFileSync(process.env.ERP_PURCHASE_FIXTURE || 'outputs/purchase-replan-20260922/browser-fixture.json','utf8'));
  const browser=await chromium.launch({channel:'msedge',headless:true});
  try {
    const page=await browser.newPage({viewport:{width:1366,height:768}});
    const headers={Authorization:`Token ${fixture.token}`};
    const request=async(path,body) => {
      const response=await page.request.post(`${process.env.ERP_PURCHASE_API_URL || 'http://127.0.0.1:8014'}/api${path}`,{headers,data:body||{}});
      assert.ok(response.ok(),await response.text());return response.json();
    };
    const material=(await (await page.request.get(`${process.env.ERP_PURCHASE_API_URL || 'http://127.0.0.1:8014'}/api/purchase-order/lookups/?kind=material&q=RHY-000018`,{headers})).json())[0];
    const req=await request('/purchase-requisition/',{request_date:'2026-09-22',department:fixture.department,lines:[{material:material.id,line_number:10,requested_qty:'1',needed_date:'2026-09-22'}]});
    await request(`/purchase-requisition/${req.id}/submit/`);await request(`/purchase-requisition/${req.id}/approve/`);
    const count=async() => (await (await page.request.get(`${process.env.ERP_PURCHASE_API_URL || 'http://127.0.0.1:8014'}/api/purchase-order/?workspace=1`,{headers})).json()).count;
    const before=await count();
    await page.goto(process.env.ERP_PURCHASE_FRONTEND_URL || 'http://127.0.0.1:5194');
    await page.evaluate(async token => (await import('/tests/fixtures/PurchaseHarness.jsx')).mount(token),fixture.token);
    await page.getByLabel('请购单号起',{exact:true}).fill(req.number);await page.getByLabel('请购单号止',{exact:true}).fill(req.number);
    await page.getByRole('button',{name:'查询',exact:true}).click();await page.getByText('RHY-000018',{exact:true}).waitFor();
    await page.getByRole('button',{name:'全选本页',exact:true}).click();
    await page.getByLabel(`本次单价${req.number}行10`,{exact:true}).fill('2340');
    await page.getByRole('button',{name:'提交',exact:true}).click();
    await page.getByRole('button',{name:'取消生成',exact:true}).click();assert.equal(await count(),before);
    await page.getByRole('button',{name:'提交',exact:true}).click();await page.getByRole('button',{name:'继续生成',exact:true}).click();
    await page.getByRole('button',{name:'否',exact:true}).click();assert.equal(await count(),before+1);
    assert.ok(await page.getByRole('heading',{name:'请购单转采购单',exact:true}).isVisible());
    assert.equal(await page.locator('.pu-generation-result button').count(),1);
  } finally {await browser.close();}
});
