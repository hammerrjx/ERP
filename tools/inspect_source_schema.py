"""Create a read-only SQL Server schema catalog from local .env credentials."""

from collections import defaultdict
from pathlib import Path
import os

import pyodbc


ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"
OUTPUT_FILE = ROOT / "docs" / "source-schema-catalog.md"


def load_dotenv(path):
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def connection_string():
    required = ["ERP_SOURCE_DB_HOST", "ERP_SOURCE_DB_PORT", "ERP_SOURCE_DB_NAME", "ERP_SOURCE_DB_USER", "ERP_SOURCE_DB_PASSWORD"]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError(f".env 缺少配置项：{', '.join(missing)}")
    return (
        "DRIVER={SQL Server};"
        f"SERVER={os.environ['ERP_SOURCE_DB_HOST']},{os.environ['ERP_SOURCE_DB_PORT']};"
        f"DATABASE={os.environ['ERP_SOURCE_DB_NAME']};"
        f"UID={os.environ['ERP_SOURCE_DB_USER']};"
        f"PWD={os.environ['ERP_SOURCE_DB_PASSWORD']};"
        "APP=ERP-SchemaInspector;"
        "Connection Timeout=10;"
    )


def fetch_metadata(connection):
    cursor = connection.cursor()
    objects = cursor.execute("""
        SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE IN ('BASE TABLE', 'VIEW')
        ORDER BY TABLE_TYPE, TABLE_SCHEMA, TABLE_NAME
    """).fetchall()
    columns = cursor.execute("""
        SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, DATA_TYPE,
               IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION,
               NUMERIC_SCALE, ORDINAL_POSITION
        FROM INFORMATION_SCHEMA.COLUMNS
        ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION
    """).fetchall()
    foreign_keys = cursor.execute("""
        SELECT OBJECT_SCHEMA_NAME(fk.parent_object_id), OBJECT_NAME(fk.parent_object_id),
               pc.name, OBJECT_SCHEMA_NAME(fk.referenced_object_id),
               OBJECT_NAME(fk.referenced_object_id), rc.name
        FROM sys.foreign_key_columns fkc
        JOIN sys.foreign_keys fk ON fk.object_id = fkc.constraint_object_id
        JOIN sys.columns pc ON pc.object_id = fkc.parent_object_id AND pc.column_id = fkc.parent_column_id
        JOIN sys.columns rc ON rc.object_id = fkc.referenced_object_id AND rc.column_id = fkc.referenced_column_id
        ORDER BY 1, 2, pc.name
    """).fetchall()
    return objects, columns, foreign_keys


def is_candidate(name, columns):
    keywords = ("pt", "part", "item", "material", "prod", "cust", "customer", "vend", "supplier", "loc", "site", "warehouse", "curr", "currency", "uom", "unit", "um", "ex", "cp", "pl", "gend")
    text = " ".join([name, *columns]).lower()
    return any(keyword in text for keyword in keywords)


def render_catalog(objects, columns, foreign_keys):
    grouped = defaultdict(list)
    for column in columns:
        grouped[(column[0], column[1])].append(column)
    candidates = [(schema, name, kind) for schema, name, kind in objects if is_candidate(name, [column[2] for column in grouped[(schema, name)]])]
    lines = [
        "# 原 ERP 数据库结构目录",
        "",
        "此文件由 `tools/inspect_source_schema.py` 从系统元数据生成；未读取业务记录。",
        "",
        f"- 对象总数：{len(objects)}",
        f"- 候选对象：{len(candidates)}",
        f"- 外键约束：{len(foreign_keys)}",
        "",
        "## 候选对象",
        "",
    ]
    for schema, name, kind in candidates:
        lines.extend([f"### `{schema}.{name}` ({kind})", "", "| 序号 | 字段 | 类型 | 可空 |", "| ---: | --- | --- | --- |"])
        for column in grouped[(schema, name)]:
            data_type = column[3]
            if column[5]:
                data_type += f"({column[5]})"
            elif column[6]:
                data_type += f"({column[6]},{column[7] or 0})"
            lines.append(f"| {column[8]} | `{column[2]}` | {data_type} | {column[4]} |")
        lines.append("")
    lines.extend(["## 外键关系", "", "| 源对象.字段 | 目标对象.字段 |", "| --- | --- |"])
    for source_schema, source_table, source_column, target_schema, target_table, target_column in foreign_keys:
        lines.append(f"| `{source_schema}.{source_table}.{source_column}` | `{target_schema}.{target_table}.{target_column}` |")
    return "\n".join(lines) + "\n"


def main():
    load_dotenv(ENV_FILE)
    with pyodbc.connect(connection_string(), readonly=True) as connection:
        objects, columns, foreign_keys = fetch_metadata(connection)
    OUTPUT_FILE.write_text(render_catalog(objects, columns, foreign_keys), encoding="utf-8")
    print(f"已写入 {OUTPUT_FILE}")
    print(f"发现 {len(objects)} 个对象、{len(foreign_keys)} 条外键关系。")


if __name__ == "__main__":
    main()
