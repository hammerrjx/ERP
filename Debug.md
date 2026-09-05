推荐的 Debug 审阅流程
记录问题的完整复现信息：入口页面、操作步骤、输入数据、实际结果、期望结果、浏览器控制台和 API 响应。

为具体问题建立一个能稳定失败的测试。例如：
python backend\manage.py test backend.test_sales_flows

后端优先检查 serializer、model clean()、审批动作和事务边界。

前端检查网络请求、权限判断、异步竞态、错误状态和浏览器控制台。

修复前先让回归测试失败，修复后确认测试变绿。

再运行完整验证：
python backend\manage.py check
python backend\manage.py test
npm run build
