# ERP 审查修复记录（2026-09-08）

范围：用户授权处理新版清单全部 15 项。权限边界、移动端排查不在本轮范围。
本轮仅编辑前端、测试与测试入口配置，没有修改后端业务逻辑。
工作区此前已有后端重构等未提交变更，本次交付保留它们，不将其归为本轮修复。

## 修复项与 diff 摘要

| ID | 变更文件 | 变更说明 | 验证 | 结果 |
|---|---|---|---|---|
| F1 | src/app/App.jsx | 登录成功调用已存在的 resetData，删除失效变量引用 | 浏览器登录失败/成功、持久化会话、工作台断言 | 通过 |
| F2 | src/components/Field.jsx | 检索文本失焦后恢复真实选中值；删除无效 resetOnBlur 配置 | 浏览器先输入未选择值，再选择另一项，核对显示和 ID | 通过 |
| F3 | src/modules/purchase/MaterialImport.jsx | 新预检开始清除旧 batch；失败时无确认入口 | 浏览器 A 成功、B 失败、C 重试，只允许确认 C | 通过 |
| F4 | src/components/PendingControls.jsx；ResourceModals、OrderWorkflowModal、ResourceTable；各保存表单；App.jsx；styles.css | 共用 AsyncForm/PendingButton 锁定未完成操作，表单返回真实 Promise，保留错误后的输入 | 浏览器双提交只调用一次、失败后解锁、再次提交；所有前端构建 | 通过 |
| F5 | src/modules/sales/SalesQuoteModal.jsx | 历史报价依赖包含日期/币种；区分加载、空结果、失败并支持重试 | 浏览器检查查询参数、503 错误及重试 | 通过 |
| F6 | src/modules/sales/SalesOrderModal.jsx | 按完整表头条件、行对象身份及请求标识接收取价响应；删除无用行索引 | 浏览器延迟返回报价，期间修改日期，确认旧价未覆盖 | 通过 |
| F7 | src/app/App.jsx、useResourceData.js | 删除/审批后失效对应 lookup；重置延迟加载标识 | 浏览器缓存删除后重载为空，会话重置清空 lookups | 通过 |
| F8 | src/app/App.jsx | 编辑器内操作或删除成功后关闭旧编辑窗口并刷新列表 | 浏览器真实 App 审核/删除流程与列表断言 | 通过 |
| F10 | src/shared/presentation.js | 业务日期使用后端已有 Asia/Shanghai 时区 | Node 测试上海午夜前后与跨年 | 通过 |
| T1 | tests/interaction.test.cjs、src/api/presentation.test.js、package.json | 增加 8 个桌面交互测试及日期边界测试，不绕过登录回调 | 下方完整输出 | 通过 |
| T2 | backend/test_sales_flows.py | 两个相似用例合并为两个 subTest 场景；断言具体错误与订单/明细无残留 | 定向与全量 Django 测试 | 通过 |
| T3 | backend/test_support.py | 共享测试支持使用临时 MEDIA_ROOT，注册类级清理 | 上传/导入测试包含在全量 Django 测试内 | 通过 |
| T4 | backend/test_support.py | 测试默认显式关闭过账，开启场景继续局部覆盖 | 外部 ERP_DELIVERY_POST_STOCK=1 下全量回归 | 通过 |
| T5 | backend/test_engineering.py | 验证逆序创建后的排序、重复序号、良率上下限、BOM 自引用、零/最小用量及拒绝后行数 | 定向 14 项及全量 Django 测试 | 通过 |
| R1 | backend/test_support.py、tests.py、test_engineering.py | 复用 ApiSupport 的 post/setup；路线不再创建无用组件 | 全量 Django 测试 | 通过 |

合并后 Django 测试方法由 105 减为 104，两个拒绝业务场景仍通过 subTest 保留。
没有为了降低用例数删除不同业务链路。共享异步表单减少了各窗口重复维护 pending 状态的代码。

## 验证命令与真实输出

```powershell
.venv/Scripts/python.exe backend/manage.py test backend.test_engineering backend.test_sales_flows --noinput
```

```text
Ran 14 tests in 7.404s
OK
Found 14 test(s).
System check identified no issues (0 silenced).
```

```powershell
.venv/Scripts/python.exe backend/manage.py test backend --noinput
```

```text
Ran 104 tests in 73.522s
OK
Found 104 test(s).
System check identified no issues (0 silenced).
```

```powershell
$env:ERP_DELIVERY_POST_STOCK='1'
.venv/Scripts/python.exe backend/manage.py test backend --noinput
```

```text
Ran 104 tests in 72.583s
OK
Found 104 test(s).
System check identified no issues (0 silenced).
```

```powershell
npm test
npm run build
```

```text
✔ JSON, uploads and exports preserve server errors (29.2591ms)
✔ empty responses, multipart bodies and binary downloads retain their contracts (2.4387ms)
✔ business dates use Shanghai midnight, including year boundaries (18.0894ms)
ℹ tests 3
ℹ pass 3
ℹ fail 0
ℹ skipped 0
vite v8.2.1 building client environment for production...
✓ built in 690ms
```

浏览器测试前先启动 Vite。使用已安装的 Playwright 和 Edge，无需业务后端；所有 /api/ 请求均被拦截。

```powershell
npm run dev -- --host 127.0.0.1 --port 5176
# 另一终端；PLAYWRIGHT_MODULE 可指向本机已有 playwright 模块
$env:PLAYWRIGHT_MODULE='C:/Users/LENOVO/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright'
node --test tests/interaction.test.cjs
# 等价入口：npm run test:browser
```

```text
✔ login failure preserves form; successful login saves session and opens dashboard (2167.9911ms)
✔ lookup restores selected code after uncommitted search and supports selecting another option (740.349ms)
✔ failed replacement import cannot confirm old batch; retry confirms the new batch (700.0477ms)
✔ shared form prevents duplicate requests and unlocks after failure without losing input (782.2025ms)
✔ history refetches for date and currency, shows errors and retries (752.6998ms)
✔ order ignores a quote response after its date changes (682.4128ms)
✔ lookup invalidation reloads deleted records and login reset clears cache (555.7437ms)
✔ editor closes after successful action and delete and list refreshes (2048.9778ms)
ℹ tests 8
ℹ pass 8
ℹ fail 0
ℹ skipped 0
```

已有桌面报价检查同样运行通过：

```powershell
$env:ERP_FRONTEND_URL='http://127.0.0.1:5176'
node tools/check_quote_order_lookup.cjs
```

```text
Passed: original material remains unchanged and selectable; exact customer item and quote resolve; 950+50 costs 19000; lookup failures preserve price and show feedback. No database writes.
```

浏览器测试开发中曾出现选择框测试夹具挂载错误，修正夹具后重新运行 8 项全部通过。
Git CRLF warning、导入命令 info 不计为测试失败。未修改权限规则，也未恢复移动端排查。
