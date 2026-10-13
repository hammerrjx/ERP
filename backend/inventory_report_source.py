"""Source field mapping shared by the importer and reconciliation tests."""
import hashlib
import json
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP

ZERO = Decimal('0')


def text(value):
    return '' if value is None else str(value).strip()


def number(value):
    return None if value is None or value == '' else Decimal(str(value))


def total(row, fields):
    values = [number(row.get(key)) for key in fields]
    return None if any(value is None for value in values) else sum(values, ZERO)


def amount(quantity, unit_cost):
    return None if unit_cost is None else (quantity * unit_cost).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def money_text(value):
    return None if value is None else format(value, 'f')


class SourceReportMapper:
    def __init__(self, masters, as_of):
        self.masters = masters
        self.as_of = date.fromisoformat(as_of[:10])
        self.materials = {text(r['pt_part']): r for r in masters['pt_mstr']}
        self.locations = {(text(r['loc_site']), text(r['loc_loc'])): r for r in masters['loc_mstr']}
        self.categories = {text(r['pl_prod_line']): text(r['pl_desc']) for r in masters['pl_mstr']}
        self.units = {text(r['um_um']): text(r['um_desc']) for r in masters['um_mstr']}
        self.users = {text(r['usr_user']): text(r['usr_name']) for r in masters['usr_mstr']}
        self.dictionary = {(text(r['gend_gen']), text(r['gend_option'])): text(r['gend_name']) for r in masters['gend_det']}
        self.costs = {(text(r['ptp3_site']), text(r['ptp3_part'])): total(r,
            [f'ptp3_{component}_std{level}' for component in ('mtl', 'lbr', 'bdn', 'sub') for level in ('tl', 'll')])
            for r in masters.get('ptp3_det', [])}
        self.customer_codes = defaultdict(set)
        for row in masters.get('cp_mstr', []):
            self.customer_codes[text(row['cp_part'])].add(text(row['cp_cust']) + ': ' + text(row['cp_cust_part']))
        self.partners = {}
        for kind, table, code, name in (('supplier', 'vd_mstr', 'vd_addr', 'vd_sort'),
                                      ('customer', 'cm_mstr', 'cm_addr', 'cm_sort'),
                                      ('department', 'dp_mstr', 'dp_code', 'dp_name')):
            self.partners[kind] = {text(r[code]): text(r[name]) for r in masters.get(table, [])}
        self.prices = defaultdict(list)
        for row in masters.get('sc_mstr', []):
            if row.get('sc_pst') and text(row['sc_start'])[:10] <= self.as_of.isoformat() <= text(row['sc_expire'])[:10]:
                self.prices[text(row['sc_part'])].append(row)
        self.tier_quotes = {text(r['scd_nbr']) for r in masters.get('scd_det', [])}

    def price(self, part):
        """Only an unambiguous current quote can supply a reference stock price.

        Prices stay in their quote currency; no unverified FX conversion or
        arbitrary customer selection is applied to the stock report.
        """
        rows = self.prices.get(part, [])
        if not rows:
            return None, '', '无有效已审核报价'
        if len(rows) != 1:
            return None, '', '多条有效报价，待确定客户/报价'
        row = rows[0]
        currency = text(row['sc_curr'])
        if text(row['sc_nbr']) in self.tier_quotes:
            return None, currency, '阶梯报价，待确定数量档位'
        numerator, denominator = number(row.get('sc_um_rate_m')), number(row.get('sc_um_rate_d'))
        price, tax = number(row.get('sc_price')), number(row.get('sc_vat_rate'))
        if not numerator or numerator <= 0 or not denominator or denominator <= 0 or price is None or tax is None or tax <= -100:
            return None, currency, '报价换算资料异常'
        if row.get('sc_vat'):
            price /= 1 + tax / 100
        # Business quantity * m / d = stock quantity, so price uses d / m.
        price = (price * denominator / numerator).quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP)
        return price, currency, '报价 ' + text(row['sc_nbr'])

    def common(self, row, movement):
        prefix = 'tr' if movement else 'ld'
        part, site, loc = (text(row.get(prefix + '_' + key)) for key in ('part', 'site', 'loc'))
        material = self.materials.get(part, {})
        location = self.locations.get((site, loc), {})
        category, group, part_type, keeper = (text(material.get('pt_' + key)) for key in ('prod_line', 'group', 'part_type', 'keeper'))
        loc_type = text(location.get('loc_type'))
        unit = text(row.get('tr_um_stk') if movement else material.get('pt_um'))
        return dict(site=site, material_code=part, material_name=text(material.get('pt_desc1')),
                    specification=text(material.get('pt_spec')), category_code=category,
                    category_name=self.categories.get(category, ''), group_code=group,
                    group_name=self.dictionary.get(('PT_GROUP', group), ''), part_type=part_type,
                    part_type_name=self.dictionary.get(('PART_TYPE', part_type), ''), keeper_code=keeper,
                    keeper_name=self.users.get(keeper, ''), location_code=loc,
                    location_name=text(location.get('loc_desc')), location_type=loc_type,
                    location_type_name=self.dictionary.get(('LOC_TYPE', loc_type), loc_type),
                    uom_name=self.units.get(unit, unit), uom_code=unit,
                    batch_number=text(row.get('tr_lotserial' if movement else 'ld_lot')))

    def map(self, table, row):
        movement = table != 'ld_det'
        result = self.common(row, movement)
        quantity = number(row['tr_qty_loc' if movement else 'ld_qty_oh'])
        if quantity is None:
            raise ValueError('Source stock quantity cannot be empty')
        result['quantity'] = money_text(quantity)
        if not movement:
            part = result['material_code']
            cost = self.costs.get((result['site'], part))
            price, currency, status = self.price(part)
            result.update(storage_position=text(self.materials.get(part, {}).get('pt_loc_pos')),
                          standard_cost=money_text(cost), inventory_amount=money_text(amount(quantity, cost)),
                          sales_price=money_text(price), sales_amount=money_text(amount(quantity, price)),
                          currency=currency, price_status=status,
                          customer_material_code='; '.join(sorted(self.customer_codes.get(part, []))))
            key = json.dumps([result[k] for k in ('site', 'location_code', 'material_code', 'batch_number')], ensure_ascii=False)
            key = hashlib.sha256(key.encode()).hexdigest()
        else:
            code, partner = text(row['tr_type']), text(row.get('tr_addr'))
            kind, name = '', ''
            if code in {'110', '210', '150', '250'}:
                kind, name = 'department', self.partners['department'].get(partner, '')
            if code in {'120', '220', '170', '270', '121', '221', '140', '240'} or not name:
                candidate = self.partners['supplier'].get(partner)
                if candidate is not None:
                    kind, name = 'supplier', candidate
            if code in {'260', '261'} or not name:
                candidate = self.partners['customer'].get(partner)
                if candidate is not None:
                    kind, name = 'customer', candidate
            cost = total(row, [f'tr_{component}_{level}' for component in ('mtl', 'lbr', 'bdn', 'sub') for level in ('tl', 'll')])
            value = total(row, [f'tr_{component}_amt{level}' for component in ('mtl', 'lbr', 'bdn', 'sub') for level in ('', '_ll')])
            result.update(movement_type=code, movement_name=self.dictionary.get(('TR_TYPE', code), code),
                receipt_quantity=money_text(max(quantity, ZERO)), issue_quantity=money_text(max(-quantity, ZERO)),
                document_date=text(row.get('tr_effdate'))[:10], posted_at=text(row.get('tr_date')),
                document_number=text(row.get('tr_ref')), order_number=text(row.get('tr_nbr')),
                order_line=text(row.get('tr_line')), flag=text(row.get('tr_lot')),
                display_document_number=text(row.get('tr_nbr' if code == '501' else 'tr_ref')),
                document_line=text(row.get('tr_line' if code == '501' else 'tr_ref_line')),
                partner_code=partner, partner_kind=kind, partner_name=name, notes=text(row.get('tr_rmks')),
                unit_cost=money_text(cost), movement_amount=money_text(value),
                transaction_price=money_text(number(row.get('tr_price'))), currency=text(row.get('tr_curr')))
            key = f"{int(row['tr_trnbr']):020d}"
        result.update(source_table=table, source_key=key)
        return result

    def lookups(self):
        definitions = [('material', 'pt_mstr', 'pt_part', 'pt_desc1', '', 'pt_spec'),
                       ('category', 'pl_mstr', 'pl_prod_line', 'pl_desc', '', ''),
                       ('location', 'loc_mstr', 'loc_loc', 'loc_desc', 'loc_site', ''),
                       ('keeper', 'usr_mstr', 'usr_user', 'usr_name', '', ''),
                       ('supplier', 'vd_mstr', 'vd_addr', 'vd_sort', '', ''),
                       ('customer', 'cm_mstr', 'cm_addr', 'cm_sort', '', ''),
                       ('department', 'dp_mstr', 'dp_code', 'dp_name', '', ''),
                       ('lot', 'lots', 'code', '', 'site', '')]
        for kind, table, code, name, site, spec in definitions:
            rank, previous = 0, None
            for row in self.masters.get(table, []):
                value = text(row[code])
                if value != previous:
                    rank += 1
                    previous = value
                yield dict(kind=kind, code=value, name=text(row.get(name)), site=text(row.get(site)),
                           specification=text(row.get(spec)), source_order=rank)
        dictionary_kinds = {'TR_TYPE': 'movement_type', 'PART_TYPE': 'part_type', 'PT_GROUP': 'group'}
        counters = defaultdict(int)
        for row in self.masters['gend_det']:
            kind = dictionary_kinds.get(text(row['gend_gen']))
            if kind:
                counters[kind] += 1
                yield dict(kind=kind, code=text(row['gend_option']), name=text(row['gend_name']), source_order=counters[kind])
