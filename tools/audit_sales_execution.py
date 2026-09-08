"""Read-only comparison of local sales plans with source orders and sales history."""
import json
import sqlite3
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.inspect_source_schema import ENV_FILE, connection_string, load_dotenv
import pyodbc


def main():
    load_dotenv(ENV_FILE)
    local = sqlite3.connect(f"file:{(ROOT / 'backend/db.sqlite3').as_posix()}?mode=ro", uri=True)
    local.row_factory = sqlite3.Row
    rows = list(local.execute("""SELECT o.number,l.*,m.code material_code,cm.customer_code
        FROM backend_salesorderline l JOIN backend_salesorder o ON o.id=l.order_id
        JOIN backend_material m ON m.id=l.material_id
        LEFT JOIN backend_customermaterial cm ON cm.id=l.customer_material_id"""))
    local.close()
    current = {(row["number"], row["line_number"]): dict(row) for row in rows}
    numbers = sorted({row["number"] for row in rows})
    differences, missing, history_gaps = [], set(current), []
    with pyodbc.connect(connection_string(), readonly=True, timeout=10) as source:
        source.timeout = 45
        for offset in range(0, len(numbers), 300):
            batch = numbers[offset:offset + 300]
            markers = ",".join("?" for _ in batch)
            cursor = source.cursor().execute(f"""SELECT sod_nbr,sod_line,sod_qty_ord,sod_qty_spare,
                sod_qty_shp,sod_qty_spare_shp,sod_price,sod_part,sod_cust_part
                FROM sod_det WHERE sod_nbr IN ({markers})""", batch)
            for number, line, formal, spare, sent, spare_sent, price, material, customer_code in cursor.fetchall():
                key = (number, line)
                if key not in current:
                    continue
                missing.discard(key)
                row = current[key]
                for field, value in (("quantity", formal), ("spare_quantity", spare),
                                     ("delivered_quantity", sent), ("delivered_spare_quantity", spare_sent),
                                     ("unit_price", price)):
                    if Decimal(str(row[field])) != Decimal(str(value or 0)):
                        differences.append({"order": number, "line": line, "field": field,
                                            "local": str(row[field]), "source": str(value)})
                for field, value in (("material_code", material), ("customer_code", customer_code)):
                    if (row[field] or "").strip() != (value or "").strip():
                        differences.append({"order": number, "line": line, "field": field,
                                            "local": row[field], "source": value})
                if row["source_quote_line_id"]:
                    differences.append({"order": number, "line": line, "field": "source_quote_line",
                                        "local": row["source_quote_line_id"], "source": "Unverified source link; review required"})
            cursor.execute(f"""SELECT s.sod_nbr,s.sod_line,s.sod_qty_shp,s.sod_qty_spare_shp,
                COALESCE(h.formal,0),COALESCE(h.spare,0) FROM sod_det s
                LEFT JOIN (SELECT sdh_so_nbr,sdh_sod_line,SUM(sdh_qty_shp) formal,
                    SUM(sdh_qty_spare_shp) spare FROM sdh_hist
                    WHERE sdh_so_nbr IN ({markers}) GROUP BY sdh_so_nbr,sdh_sod_line) h
                ON h.sdh_so_nbr=s.sod_nbr AND h.sdh_sod_line=s.sod_line
                WHERE s.sod_nbr IN ({markers})""", batch + batch)
            for number, line, formal, spare, history_formal, history_spare in cursor.fetchall():
                if (number, line) in current and (formal != history_formal or spare != history_spare):
                    history_gaps.append({"order": number, "line": line, "formal": str(formal),
                                         "history_formal": str(history_formal), "spare": str(spare),
                                         "history_spare": str(history_spare)})
    report = {"read_only": True, "local_lines": len(rows), "differences": differences,
              "missing_source_lines": sorted(missing), "source_history_gaps": history_gaps}
    path = ROOT / "outputs/sales-execution-audit.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"local_lines": len(rows), "differences": len(differences),
                      "missing_source_lines": len(missing), "source_history_gaps": len(history_gaps),
                      "report": str(path)}, ensure_ascii=True))


if __name__ == "__main__":
    main()
