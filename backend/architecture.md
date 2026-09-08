# Backend architecture

The backend is a small Django/DRF service. It borrows Odoo's useful boundaries
without copying Odoo's implementation:

- `Company`, `Currency`, `CurrencyRate`, `UomCategory`, `Uom`, `ProductCategory`,
  and `Location` are reusable master data.
- `Material` keeps the four form tabs from the legacy ERP: basic, engineering,
  inventory, and MRP. Foreign keys connect category, UoM, default location,
  supplier, and companies.
- `Partner` is the shared customer/supplier record. Contacts and bank accounts
  are one-to-many records; `PartnerCompany` is the multi-company bridge.
- `CustomerMaterial` stores the customer's external material code/name.
- `SupplierQuote` and `SupplierQuoteLine` model dated purchase/outsource quotes.
- `PayableVoucher` and `PayableVoucherLine` map the legacy `ap_mstr` / `apd_det`
  header-source relationship. Approved receipts add payable amounts and approved
  purchase returns subtract them; a source line can be used only once.
- `AuditedModel` provides a server-side approval state machine. `AuditEvent` is
  append-only application audit data.

PostgreSQL is the production database. SQLite is acceptable for local smoke
tests. CRUD stays synchronous; background jobs are intentionally deferred until
imports, notifications, or MRP planning have a measured need.

## Invariants enforced by the model layer

- Protected foreign keys prevent deleting referenced master data.
- Unit conversions must use the same UoM category and positive quantities.
- Material and partner company scope is explicit through bridge tables.
- Supplier quotes require approved supplier roles, valid dates, and exactly the
  price kind implied by purchase vs. outsource quote type.
- Approval transitions are server-side and reject invalid transitions.
- Payable generation separates supplier, currency, payment method, and tax rate;
  mixed payment methods can never share one automatically generated voucher.
- Material default location, category, UoM, and tax code are required fields.

## Code organization

- `backend/domain/` owns model implementations by business module: shared audit
  behavior in `base.py`, then master data, system, engineering, sales, delivery,
  purchase, and inventory. `backend/models.py` exposes the existing model names
  for Django discovery and established imports. Cross-module relations use
  Django string references; table names and the `backend` app label stay stable.
- `backend/master_data/serializers/` groups validation and API representations
  by the same modules, with separate sales quote and order serializers. Its
  `__init__.py` preserves the existing serializer import paths. `common.py`
  owns only shared model validation and the generic serializer factory.
- HTTP endpoints are organized in `backend/master_data/*_views.py` by system,
  master data, engineering, sales, purchasing, and inventory. The established
  `backend/master_data/views.py` remains a compatibility export for the router;
  API paths and permission resource names remain unchanged.
- `backend/master_data/api_common.py` owns the shared role permission check,
  audited create/update hooks, approval actions, and generic model ViewSet
  factory. Domain ViewSets use this shared behavior rather than duplicating it.

`makemigrations` should be run after installing the requirements. The API uses
the same model validation for browser forms and imports; frontend controls are
not treated as a security boundary.
