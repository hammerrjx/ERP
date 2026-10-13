"""Read-only enrichment for imported requests; never infer source order identity by material."""
from decimal import Decimal
from django.core.exceptions import ValidationError


def enrich_requests(requests):
    imported = [r for r in requests if r.requisition.source_profile == 'coerp_dgyzx1']
    if not imported:
        return
    import pyodbc
    from tools.inspect_source_schema import connection_string
    try:
        with pyodbc.connect(connection_string('coerp_dgyzx1'), timeout=10) as connection:
            connection.timeout = 15
            cursor = connection.cursor()
            cursor.execute('SELECT TOP 1 poc_price_clue, poc_max_price_perm FROM dbo.poc_ctrl')
            control = cursor.fetchone()
            cursor.execute('SELECT TOP 1 sys_cu_price FROM dbo.sys_ctrl')
            if cursor.fetchone()[0]:
                raise ValidationError('源账套已启用铜价计算，请先同步铜价规则后转单')
            for start in range(0, len(imported), 300):
                batch = imported[start:start+300]
                conditions = ' OR '.join('(r.req_pr_nbr=? AND r.req_line=?)' for _ in batch)
                params = [v for r in batch for v in (r.requisition.number, r.line_number)]
                cursor.execute('''SELECT r.req_pr_nbr, r.req_line, r.req_wo_nbr, r.req_wo_lot,
                    COALESCE(w.wo_part, s.sod_part, '') AS parent_code,
                    COALESCE(p.pt_desc1, '') AS parent_name, COALESCE(p.pt_spec, '') AS parent_specification,
                    COALESCE(w.wo_qty_ord, s.sod_qty_ord, 0) AS original_quantity,
                    COALESCE(NULLIF(s.sod_cust_part,''),NULLIF(cp.cp_cust_part,''),ws.sod_cust_part,'') AS customer_material,
                    COALESCE(cm.cm_char4, '') AS business_type
                    FROM dbo.req_mstr r
                    LEFT JOIN dbo.wo_mstr w ON w.wo_nbr=r.req_wo_nbr AND w.wo_lot=r.req_wo_lot
                    LEFT JOIN dbo.sod_det s ON s.sod_nbr=r.req_wo_nbr AND CONVERT(varchar(40),s.sod_line)=r.req_wo_lot
                    LEFT JOIN dbo.pt_mstr p ON p.pt_part=COALESCE(w.wo_part,s.sod_part)
                    LEFT JOIN dbo.so_mstr so ON so.so_nbr=s.sod_nbr
                    LEFT JOIN dbo.cm_mstr cm ON cm.cm_addr=so.so_cust
                    LEFT JOIN dbo.fcd_det f ON f.fcd_nbr=r.req_wo_nbr AND CONVERT(varchar(40),f.fcd_line)=r.req_wo_lot
                    LEFT JOIN dbo.fc_mstr fc ON fc.fc_nbr=f.fcd_nbr
                    OUTER APPLY (SELECT TOP 1 cp_cust_part FROM dbo.cp_mstr
                        WHERE cp_cust=fc.fc_cust AND cp_part=f.fcd_part ORDER BY cp_crt_date DESC,cp_cust_part) cp
                    LEFT JOIN dbo.sod_det ws ON ws.sod_nbr=w.wo_so_nbr AND ws.sod_line=w.wo_so_line
                    WHERE ''' + conditions, params)
                names = [c[0] for c in cursor.description]
                rows = {(row[0], row[1]): dict(zip(names, row)) for row in cursor.fetchall()}
                for req in batch:
                    row = rows.get((req.requisition.number, req.line_number))
                    if row is None:
                        raise ValidationError('源请购行已不存在，请重新同步来源资料')
                    req.purchase_source = {k: format(v, 'f') if isinstance(v, Decimal) else v or '' for k,v in row.items()}
                    req.purchase_price_clue = control[0] or '1'
                    req.purchase_high_price_permission = control[1] or ''
                parts = sorted({r.material_snapshot.get('pt_part') for r in batch if r.material_snapshot.get('pt_part')})
                if parts:
                    cursor.execute('SELECT vp_part,vp_vend,vp_vend_part FROM dbo.vp_mstr WHERE vp_pst=1 AND vp_part IN (' + ','.join('?' for _ in parts) + ')', parts)
                    mappings = {(p,v): code for p,v,code in cursor.fetchall()}
                    for req in batch:
                        req.purchase_supplier_materials = {v: code for (p,v),code in mappings.items() if p == req.material_snapshot.get('pt_part')}
                accounts=sorted({r.material.category.inventory_account for r in batch if r.material_id and r.material.category.inventory_account})
                if accounts:
                    cursor.execute('SELECT ac_code,ac_name FROM dbo.ac_mstr WHERE ac_code IN (' + ','.join('?' for _ in accounts) + ')', accounts)
                    names=dict(cursor.fetchall())
                    for req in batch:
                        req.purchase_inventory_account_name=names.get(req.material.category.inventory_account,'') if req.material_id else ''
    except pyodbc.Error as exc:
        raise ValidationError('无法读取dgyzx1请购关联资料，请检查源数据库连接后重试') from exc
