"""Client-compatible inventory query columns and monthly aggregation."""
from collections import defaultdict
from decimal import Decimal

ZERO = Decimal('0')
BULK_COLUMNS = [('tmp_part', '物料编码'), ('pt_desc1', '物料名称'), ('pt_spec', '规格'),
    ('tmp_qty_oh', '可计划库存'), ('tmp_qty_req_total', '总需求'), ('tmp_qty_on_order', '订购或生产中'),
    ('tmp_qty_req_open', '请购中'), ('tmp_sfty_stk', '安全存量'), ('tmp_qty_remain', '库存余量'),
    ('tmp_qty_alloc', '已分配数'), ('tmp_qty_unalloc', '未分配数'), ('pt_desc2', '英文名称'),
    ('pt_max_qty', '最大库存数量'), ('pt_rop', '库存警戒数量'), ('pt_ord_min', '最小采购数量'),
    ('pt_ord_mult', '最小包装数量'), ('pt_um', '单位'), ('pt_loc', '默认库位'), ('loc_desc', '库位名称'), ('pt_loc_pos', '默认储位')]
DIMENSIONS = [('loc_cost_type', '库位成本分类'), ('loc_cost_type_name', '库位成本分类名称'),
    ('inb_loc', '库位'), ('loc_desc', '库位名称'), ('loc_type', '库位类型'), ('inb_part', '物料编码'),
    ('pt_desc1', '物料名称'), ('pt_prod_line', '产品类'), ('pt_spec', '物料规格'), ('pl_desc', '产品类名称'),
    ('pt_group', '产品组'), ('group_desc', '产品组名称'), ('pt_part_type', '零件类型'), ('part_type_desc', '零件类型名称'),
    ('ac_code', '会计科目'), ('ac_name', '会计科目名称'), ('pt_um', '库存单位'), ('inb_lot', '批号')]
MONTHLY_COLUMNS = DIMENSIONS + [
    (key, label) for suffix, label in [('beg', '期初'), ('in', '入库'), ('out', '出库')]
    for key, label in [(f'inb_qty_{suffix}', label+'数量'), (f'inb_cost_{suffix}', label+'成本'), ('unit_'+suffix, label+'单位成本')]]
MONTHLY_COLUMNS += [('inb_qty_adj', '盘点数量'), ('inb_cost_adj', '合计调整成本'),
    ('inb_qty_end', '期末数量'), ('inb_cost_end', '期末成本'), ('unit_end', '期末单位成本'),
    ('inb_avg_cost', '实际成本'), ('inb_std_cost', '标准成本'), ('diff_rate', '成本差异率%')]
MOVEMENTS = [('110', '计划外入库'), ('120', '采购收货'), ('121', '外协收货'), ('130', '退良品'),
    ('131', '退来料不良'), ('132', '退作业不良'), ('140', 'IQC检验入库'), ('150', '转仓入库'),
    ('160', '成品入库'), ('170', '产线入库'), ('210', '计划外出库'), ('220', '采购退货'),
    ('221', '外协退货'), ('230', '领料'), ('231', '超领'), ('240', 'IQC检验出库'),
    ('250', '转仓出库'), ('260', '销售送货'), ('261', '销售退货'), ('270', '产线出库'), ('310', '盘点')]
MONTHLY_COLUMNS += [(f'inb_{code}_{suffix}', label+name) for code, label in MOVEMENTS for suffix, name in [('qty', '数量'), ('amt', '成本')]]
MONTHLY_COLUMNS += [('inb_501_amt', '成本调整金额')]
MONTHLY_COLUMNS += [(f'inb_{period}_{component}{level}', label+name+'('+level_name+')')
    for period, label in [('beg', '期初'), ('end', '期末'), ('std', '标准')]
    for level, level_name in [('', '本层'), ('_ll', '低层')]
    for component, name in [('mtl', '材料成本'), ('lbr', '人工成本'), ('bdn', '制造费用'), ('sub', '外协成本')]]
BULK_NUMBERS = {k for k, _ in BULK_COLUMNS if k.startswith('tmp_qty') or k in {'tmp_sfty_stk', 'pt_max_qty', 'pt_rop', 'pt_ord_min', 'pt_ord_mult'}}
MONTHLY_NUMBERS = {k for k, _ in MONTHLY_COLUMNS} - {k for k, _ in DIMENSIONS}
AVERAGES = {'inb_avg_cost', 'inb_std_cost'} | {k for k in MONTHLY_NUMBERS if k.startswith('inb_std_')}
DERIVED = {'unit_beg', 'unit_in', 'unit_out', 'unit_end', 'diff_rate'}
GROUPS = {'inb_part': ['inb_part', 'pt_prod_line', 'pt_part_type', 'pt_group'],
    'loc_cost_type': ['loc_cost_type'], 'pt_prod_line': ['pt_prod_line'], 'pt_part_type': ['pt_part_type'],
    'pt_group': ['pt_group'], 'loc_type': ['loc_type'], 'inb_loc': ['inb_loc', 'loc_type', 'loc_cost_type'], 'inb_lot': ['inb_lot']}


def decimal(value):
    return Decimal(str(value or '0'))


def reconcile_bulk(rows, details):
    """Use the same captured contributions for summary and drill-down during live source reads."""
    totals = defaultdict(lambda: ZERO)
    approved_requisitions = defaultdict(lambda: ZERO)
    for detail in details:
        if detail['tab'] != 'stock' or detail['nettable']:
            totals[(detail['part'], detail['tab'])] += decimal(detail['quantity'])
        if detail.get('tab') == 'requisition' and detail.get('eligible_for_balance', True):
            approved_requisitions[detail['part']] += decimal(detail['quantity'])
    differences = []
    for row in rows:
        for tab, field in [('stock', 'tmp_qty_oh'), ('demand', 'tmp_qty_req_total'), ('order', 'tmp_qty_on_order'),
                           ('requisition', 'tmp_qty_req_open'), ('allocation', 'tmp_qty_alloc')]:
            value = totals[(row['tmp_part'], tab)]
            delta = decimal(row[field]) - value
            if abs(delta) > Decimal('0.000001'):
                differences.append({'part': row['tmp_part'], 'field': field, 'earlier_summary': str(row[field]), 'captured_detail_sum': str(value)})
            row[field] = str(value)
        row['tmp_qty_remain'] = str(decimal(row['tmp_qty_oh']) + decimal(row['tmp_qty_on_order'])
            + approved_requisitions[row['tmp_part']] - decimal(row['tmp_qty_req_total']) - decimal(row['tmp_sfty_stk']))
        row['tmp_qty_unalloc'] = str(decimal(row['tmp_qty_oh']) - decimal(row['tmp_qty_alloc']))
    return differences


def units(row):
    for suffix in ('beg', 'in', 'out', 'end'):
        qty = decimal(row.get('inb_qty_'+suffix))
        row['unit_'+suffix] = str(decimal(row.get('inb_cost_'+suffix)) / qty if qty else ZERO)
    actual, standard = decimal(row.get('inb_avg_cost')), decimal(row.get('inb_std_cost'))
    row['diff_rate'] = str(abs(actual-standard)*100/standard if standard else ZERO if not actual else Decimal(100))
    return row


def aggregate_monthly(rows, groups, masters):
    """ICIBIQ01: sums amounts; averages actual/standard costs; derives unit costs after grouping."""
    keys = sorted({key for group in groups for key in GROUPS[group]}) if groups else list(GROUPS)
    buckets = defaultdict(list)
    for row in rows:
        buckets[tuple(row.get(key, '') for key in keys)].append(row)
    result = []
    for key, members in buckets.items():
        row = dict(zip(keys, key))
        for field in MONTHLY_NUMBERS - DERIVED:
            value = sum((decimal(r.get(field)) for r in members), ZERO)
            row[field] = str(value / len(members) if field in AVERAGES else value)
        if not any(decimal(row[k]) for k in MONTHLY_NUMBERS - DERIVED - AVERAGES if not k.startswith(('inb_beg_', 'inb_end_'))):
            continue
        row.update(masters['materials'].get(row.get('inb_part'), {}))
        location = masters['locations'].get(row.get('inb_loc'), {})
        row['loc_desc'] = location.get('loc_desc', '')
        product = masters['categories'].get(row.get('pt_prod_line'), {})
        row['pl_desc'] = product.get('pl_desc', '')
        account = product.get('pl_ac_code_wcost', '')[:4] if row.get('loc_cost_type') == 'WIP' else product.get('pl_ac_code_inv', '')
        if row.get('loc_cost_type') == 'WIP' and row.get('inb_loc') in masters['suppliers']:
            account = product.get('pl_ac_code_comm', '')
        row['ac_code'] = location.get('loc_ac_code_inv') or account
        row['ac_name'] = masters['accounts'].get(row['ac_code'], '')
        for field, dictionary, code in [('loc_cost_type_name', 'cost_types', 'loc_cost_type'),
                ('group_desc', 'groups', 'pt_group'), ('part_type_desc', 'part_types', 'pt_part_type')]:
            row[field] = masters[dictionary].get(row.get(code), '')
        result.append(units(row))
    return result
