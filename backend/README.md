# ERP backend

## Local run

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
python backend\manage.py migrate
python backend\manage.py runserver
```

The API is available under `/api/` and covers stage 1 organization/master data
plus stage 2 sales, purchasing, receipts, returns, payable vouchers, and inventory workflows.

Payable vouchers map to the legacy `ap_mstr` / `apd_det` structure. The
`payable-voucher/auto-generate/` action accepts approved receipt and purchase
return line IDs, keeps each source line unique, and splits vouchers by supplier,
currency, payment method, and tax rate.

## Checks

```powershell
python backend\manage.py check
python backend\manage.py test
```
