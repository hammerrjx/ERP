"""Import a reviewed source sample into a pilot or explicitly selected empty SQLite inventory."""

import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.utils import timezone

from backend.models import Company, Warehouse, Location, Uom, UomCategory, ProductCategory, Material, Department
from backend.domain.inventory import StockBalance, StockTransaction
from backend.domain.warehouse_documents import InventoryDictionary, InventoryDocument, InventoryDocumentLine, LegacyInventoryRecord


def key(value):
    return str(value or "").rstrip()


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument("source", type=Path)
        parser.add_argument("--allow-live-sample", action="store_true")
        parser.add_argument("--sqlite-target", type=Path, help="Explicit SQLite target path; inventory must be empty")

    @transaction.atomic
    def handle(self, *args, **options):
        sqlite_target = options.get("sqlite_target")
        if sqlite_target:
            if connection.vendor != "sqlite" or Path(connection.settings_dict["NAME"]).resolve() != sqlite_target.resolve():
                raise CommandError("SQLite target must match the active database exactly")
            if any(model.objects.exists() for model in (StockBalance, StockTransaction, InventoryDocument, LegacyInventoryRecord)):
                raise CommandError("SQLite inventory is not empty; importing another opening is forbidden")
        elif connection.vendor != "microsoft" or connection.settings_dict["NAME"] != "erp_inventory_pilot":
            raise CommandError("Use erp_inventory_pilot or explicitly select an empty --sqlite-target")
        data = json.loads(options["source"].read_text(encoding="utf-8"))
        if data["source"] != "coerp_dgyzx1":
            raise CommandError("Unexpected source database")
        if not data["consistent_snapshot"] and not options["allow_live_sample"]:
            raise CommandError("Live extraction is only allowed as an explicitly marked non-production sample")
        if InventoryDocument.objects.filter(kind="opening").exists():
            raise CommandError("Pilot opening already imported; do not replay it")
        actor = "dgyzx1-pilot-import"
        approved = {"status": "approved", "created_by": actor}
        report = {"source": data["source"], "consistent_snapshot": data["consistent_snapshot"], "warnings": [], "excluded_balances": [], "material_mapping": []}
        sites = {}
        for row in data["si_mstr"]:
            company, _ = Company.objects.get_or_create(code=key(row["si_company"]), defaults={"name": key(row["si_desc"]), **approved})
            warehouse, _ = Warehouse.objects.get_or_create(code=key(row["si_site"]), defaults={"name": key(row["si_desc"]), "company": company, **approved})
            sites[key(row["si_site"])] = warehouse
        locations = {}
        for row in data["loc_mstr"]:
            code, site = key(row["loc_loc"]), key(row["loc_site"])
            existing = Location.objects.filter(code=code).first()
            if existing and existing.source_site and existing.source_site != site:
                raise CommandError(f"Location site conflict: {code}")
            obj, _ = Location.objects.update_or_create(code=code, defaults={
                "name": key(row["loc_desc"]), "source_site": site, "warehouse": sites[site],
                "location_type": {"FG": "fg", "RAW": "rm", "ASM": "wip", "WIP": "wip", "RMA": "ng", "SCR": "ng"}.get(key(row["loc_type"]), "warehouse"),
                "location_attribute": key(row["loc_char2"]) or key(row["loc_type"]),
                "participate_mrp": row["loc_nettable"], "usable": row["loc_avail"],
                "allow_negative": row["loc_overissue"], "disabled_for_inventory": row["loc_disabled"],
                "manager": key(row["loc_keeper"]), "department": key(row["loc_char1"]), **approved})
            locations[(site, code)] = obj
        units = {}
        for row in data["um_mstr"]:
            code = key(row["um_um"])
            existing = Uom.objects.filter(code=code).first()
            # Unknown conversions must not be inferred from a shared 'quantity' category.
            category = existing.category if existing else UomCategory.objects.get_or_create(code=f"SRC-{code}", defaults={"name": f"源单位-{code}", **approved})[0]
            units[code], _ = Uom.objects.update_or_create(code=code, defaults={"name": key(row["um_desc"]), "description": key(row["um_desc"]), "category": category, **approved})
        categories = {}
        for row in data["pl_mstr"]:
            code = key(row["pl_prod_line"])
            categories[code], _ = ProductCategory.objects.update_or_create(code=code, defaults={
                "name": key(row["pl_desc"]), "default_uom": units.get(key(row["pl_um"])),
                "default_location": locations.get(("1000", key(row["pl_loc"]))),
                "supply_method": {"P": "purchase", "M": "production", "S": "outsource"}.get(row["pl_pm_code"], "purchase"),
                "batch_control": row["pl_lot_serial"], "batch_rule": key(row["pl_lot_grp"]), **approved})
        for row in data["dp_mstr"]:
            Department.objects.get_or_create(code=key(row["dp_code"]), defaults={"name": key(row["dp_name"]), **approved})
        for row in data["gend_det"]:
            InventoryDictionary.objects.update_or_create(dictionary=key(row["gend_gen"]), code=key(row["gend_option"]), defaults={"name": key(row["gend_name"]), "disabled": row["gend_disabled"]})
        materials = {}
        for row in data["pt_mstr"]:
            code = key(row["pt_part"])
            candidates = list(Material.objects.filter(old_code=code))
            exact = Material.objects.filter(code=code).first()
            if exact and exact not in candidates:
                candidates.append(exact)
            if len(candidates) > 1:
                raise CommandError(f"Ambiguous material source mapping: {code}")
            category = categories.get(key(row["pt_prod_line"]))
            unit = units.get(key(row["pt_um"]))
            location = locations.get(("1000", key(row["pt_loc"]))) or (category.default_location if category else None)
            if not location:
                balance_row = next((b for b in data["ld_det"] if key(b["ld_part"]) == code), None)
                if balance_row:
                    location = locations.get((key(balance_row["ld_site"]), key(balance_row["ld_loc"])))
            if not category or not unit or not location:
                report["warnings"].append({"material": code, "reason": "Missing category, unit or default location; preserved in source snapshot"})
                continue
            if candidates:
                material = candidates[0]
                if material.uom_id != unit.pk:
                    report["warnings"].append({"material": code, "reason": "Existing material unit differs; excluded from inventory sample"})
                    continue
            else:
                material = Material.objects.create(code=code, old_code=code, name=key(row["pt_desc1"]),
                    english_name=key(row["pt_desc2"])[:160], specification=key(row["pt_spec"]),
                    category=category, uom=unit, default_location=location,
                    batch_control=row["pt_lot_serial"], batch_rule=key(row["pt_lot_grp"]),
                    no_stock_movement=row["pt_memo_item"], default_storage_position=key(row["pt_loc_pos"]),
                    supply_method={"P": "purchase", "M": "production", "S": "outsource"}.get(row["pt_pm_code"], "purchase"),
                    purchase_lead_days=max(row["pt_pur_lt"], 0), production_lead_days=max(row["pt_mfg_lt"], 0), **approved)
            materials[code] = material
            report["material_mapping"].append({"source": code, "id": material.pk, "code": material.code, "category": category.code})
        date = datetime.fromisoformat(data["finished_at"]).date()
        opening = InventoryDocument.objects.create(kind="opening", document_date=date, status="posted", created_by=actor,
            posted_by=actor, posted_at=timezone.now(), source_key="coerp_dgyzx1:pilot-opening",
            notes="并行试运样本期初；非一致快照，不作为正式期初", source_payload={"source_started_at": data["started_at"], "source_finished_at": data["finished_at"], "consistent_snapshot": data["consistent_snapshot"]})
        archived = []
        for table, prefix, pk_names in [("ld_det", "ld", ("ld_site", "ld_loc", "ld_part", "ld_lot")),
                ("tr_hist", "tr", ("tr_trnbr",)), ("tr_hist_rec", "tr", ("tr_trnbr",)),
                ("mov_mstr", "mov", ("mov_mov",)), ("movd_det", "movd", ("movd_mov", "movd_line")),
                ("adj_mstr", "adj", ("adj_adj",)), ("adjd_det", "adjd", ("adjd_adj", "adjd_line"))]:
            for row in data[table]:
                source_key = json.dumps([key(row[n]) for n in pk_names], ensure_ascii=False, separators=(",", ":"))
                raw_date = row.get("tr_effdate") or row.get("mov_date") or row.get("adj_date")
                archived.append(LegacyInventoryRecord(source_database=data["source"], source_table=table, source_key=source_key,
                    material=materials.get(key(row.get(f"{prefix}_part"))),
                    location=locations.get((key(row.get(f"{prefix}_site")), key(row.get(f"{prefix}_loc")))),
                    effective_date=datetime.fromisoformat(raw_date).date() if raw_date else None, payload=row))
        LegacyInventoryRecord.objects.bulk_create(archived, batch_size=100)
        imported = 0
        for row in data["ld_det"]:
            qty = Decimal(row["ld_qty_oh"])
            material = materials.get(key(row["ld_part"]))
            location = locations.get((key(row["ld_site"]), key(row["ld_loc"])))
            reason = None
            if not material or not location:
                reason = "Missing mapped material or location"
            elif qty < 0:
                reason = "Negative legacy balance"
            elif material.no_stock_movement:
                reason = "Non-stock material"
            elif material.batch_control and not key(row["ld_lot"]):
                reason = "Batch-controlled material has empty legacy batch"
            if reason:
                report["excluded_balances"].append({"key": [row["ld_site"], row["ld_loc"], row["ld_part"], row["ld_lot"]], "quantity": str(qty), "reason": reason})
                continue
            if StockBalance.objects.filter(material=material, location=location, batch_number=key(row["ld_lot"])).exists():
                raise CommandError("Existing stock conflicts with opening import")
            line = InventoryDocumentLine.objects.create(document=opening, line_number=(imported + 1) * 10,
                material=material, uom=material.uom, to_location=location, quantity=qty, batch_number=key(row["ld_lot"]))
            StockBalance.objects.create(material=material, location=location, uom=material.uom, batch_number=line.batch_number, quantity=qty)
            StockTransaction.objects.create(material=material, location=location, uom=material.uom, batch_number=line.batch_number,
                quantity=qty, balance_after=qty, movement_type="opening", source_model=opening._meta.label_lower,
                source_id=str(opening.pk), source_line_id=str(line.pk), actor=actor, effective_date=date)
            imported += 1
        report.update({"opening_document": opening.number, "imported_balance_rows": imported, "archive_rows": len(archived),
                       "sample_materials_mapped": len(materials), "categories_covered": sorted({r["category"] for r in report["material_mapping"]}), "source_coverage": data["coverage"]})
        path = options["source"].parent / "import-report.json"
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        self.stdout.write(f"Imported {len(materials)} materials, {imported} balances, {len(archived)} historical rows; report: {path}")
