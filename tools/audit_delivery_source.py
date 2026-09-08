"""Compare local delivery history with SQL Server without modifying either database."""
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
    headers = {row["number"]: dict(row) for row in local.execute("SELECT * FROM backend_deliveryorder")}
    lines = {(row["number"], row["line_number"]): dict(row) for row in local.execute(
        "SELECT h.number,d.* FROM backend_deliveryorderline d JOIN backend_deliveryorder h ON h.id=d.delivery_id")}
    local.close()
    found, differences = set(), []
    with pyodbc.connect(connection_string(), readonly=True, timeout=10) as source:
        source.timeout = 30
        cursor = source.cursor()
        numbers = list(headers)
        for offset in range(0, len(numbers), 500):
            chunk = numbers[offset:offset + 500]
            markers = ",".join("?" for _ in chunk)
            cursor.execute(f"SELECT dn_dn,dn_char1,dn_char2,dn_char3,dn_char4,dn_txt,dn_rmks FROM dn_mstr WHERE dn_dn IN ({markers})", chunk)
            for number, mode, srm, address, kind, address_code, notes in cursor.fetchall():
                found.add(number)
                expected = {"delivery_mode": {"1": "direct", "2": "supplier"}.get(mode, mode),
                            "document_type": {"正常送货": "normal", "正常退货": "return", "红冲单据": "red_flush"}.get(kind, kind),
                            "srm_number": srm, "delivery_address": address, "address_code": address_code, "notes": notes}
                for field, value in expected.items():
                    if str(headers[number][field] or "").strip() != str(value or "").strip():
                        differences.append({"number": number, "field": field, "local": headers[number][field], "source": value})
            cursor.execute(f"SELECT dnd_dn,dnd_line,dnd_qty_ship,dnd_qty_spare_ship,dnd_rmks FROM dnd_det WHERE dnd_dn IN ({markers})", chunk)
            for number, line_number, amount, spare, notes in cursor.fetchall():
                local_line = lines.get((number, line_number))
                if local_line is None:
                    differences.append({"number": number, "line": line_number, "field": "missing_local_line"})
                    continue
                for field, value in (("actual_quantity", amount), ("actual_spare_quantity", spare)):
                    if Decimal(str(local_line[field])) != value:
                        differences.append({"number": number, "line": line_number, "field": field, "local": str(local_line[field]), "source": str(value)})
                if str(local_line["notes"] or "").strip() != str(notes or "").strip():
                    differences.append({"number": number, "line": line_number, "field": "notes", "local": local_line["notes"], "source": notes})
    report = {"read_only": True, "local_headers": len(headers), "matched_source_headers": len(found),
              "unmatched_numbers": sorted(set(headers) - found), "differences": differences}
    destination = ROOT / "outputs" / "delivery-source-audit.json"
    destination.parent.mkdir(exist_ok=True)
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps({"local_headers": len(headers), "matched_source_headers": len(found),
                      "differences": len(differences), "report": str(destination)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
