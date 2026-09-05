"""Inspect phase 1/2 source objects through the configured read-only SQL login."""

import json
import os
from pathlib import Path

import pyodbc

from inspect_source_schema import connection_string, load_dotenv


ROOT = Path(__file__).resolve().parent.parent
SOURCE_OBJECTS = (
    "bom_mstr",
    "dp_mstr",
    "loc_mstr",
    "po_mstr",
    "pod_det",
    "ps_mstr",
    "pt_mstr",
    "req_mstr",
    "reqd_det",
    "ro_det",
    "route_mstr",
)


def rows_as_dicts(cursor):
    names = [column[0] for column in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]


def main():
    load_dotenv(ROOT / ".env")
    configured_view = os.environ.get("ERP_SOURCE_DB_VIEW", "")
    with pyodbc.connect(connection_string(), readonly=True) as connection:
        cursor = connection.cursor()
        placeholders = ",".join("?" for _ in SOURCE_OBJECTS)
        columns = cursor.execute(
            f"""
            SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE,
                   IS_NULLABLE, ORDINAL_POSITION
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME IN ({placeholders})
            ORDER BY TABLE_NAME, ORDINAL_POSITION
            """,
            *SOURCE_OBJECTS,
        )
        result = {
            "configured_view": configured_view,
            "columns": rows_as_dicts(columns),
        }
        foreign_keys = cursor.execute(
            f"""
            SELECT OBJECT_NAME(fk.parent_object_id) AS source_table,
                   pc.name AS source_column,
                   OBJECT_NAME(fk.referenced_object_id) AS target_table,
                   rc.name AS target_column
            FROM sys.foreign_key_columns fkc
            JOIN sys.foreign_keys fk ON fk.object_id = fkc.constraint_object_id
            JOIN sys.columns pc
              ON pc.object_id = fkc.parent_object_id
             AND pc.column_id = fkc.parent_column_id
            JOIN sys.columns rc
              ON rc.object_id = fkc.referenced_object_id
             AND rc.column_id = fkc.referenced_column_id
            WHERE OBJECT_NAME(fk.parent_object_id) IN ({placeholders})
            ORDER BY source_table, source_column
            """,
            *SOURCE_OBJECTS,
        )
        result["foreign_keys"] = rows_as_dicts(foreign_keys)
        if configured_view and configured_view.replace("_", "").isalnum():
            matches = cursor.execute(
                """
                SELECT TABLE_SCHEMA, TABLE_NAME
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_NAME = ?
                ORDER BY CASE WHEN TABLE_TYPE = 'VIEW' THEN 0 ELSE 1 END, TABLE_SCHEMA
                """,
                configured_view,
            ).fetchall()
            result["configured_view_matches"] = [list(row) for row in matches]
            if matches:
                schema, name = matches[0]
                sample = cursor.execute(f"SELECT TOP 3 * FROM [{schema}].[{name}]")
                result["configured_view_sample"] = rows_as_dicts(sample)
            else:
                result["configured_view_error"] = "当前数据库中未找到配置的视图"
    print(json.dumps(result, ensure_ascii=False, default=str, indent=2))


if __name__ == "__main__":
    main()
