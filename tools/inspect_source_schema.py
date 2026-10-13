"""Create a read-only SQL Server schema catalog from local .env credentials."""

from collections import defaultdict
from pathlib import Path
import argparse
import json
import os

import pyodbc


ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"
OUTPUT_FILE = ROOT / "docs" / "source-schema-catalog.md"
PROFILE_FILE = ROOT / "tools" / "source_databases.json"


def read_dotenv(path):
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def load_dotenv(path):
    for key, value in read_dotenv(path).items():
        os.environ.setdefault(key, value)


def profiles():
    return json.loads(PROFILE_FILE.read_text(encoding="utf-8"))


def odbc_value(value):
    return "{" + str(value).replace("}", "}}") + "}"


def profile_connection_string(profile):
    configured = profiles()
    if profile not in configured:
        raise ValueError(f"Unknown source profile: {profile}. Choose: {', '.join(configured)}")
    config = configured[profile]
    parts = {"DRIVER": config["driver"], "SERVER": config["server"], "DATABASE": config["database"]}
    if config["authentication"] == "windows":
        parts["Trusted_Connection"] = "yes"
    elif config["authentication"] == "sql":
        credentials = read_dotenv(ROOT / config["credentials_file"])
        for attribute, key in (("UID", "ERP_SOURCE_DB_USER"), ("PWD", "ERP_SOURCE_DB_PASSWORD")):
            if not credentials.get(key):
                raise ValueError(f"Missing {key} in {config['credentials_file']}")
            parts[attribute] = credentials[key]
    else:
        raise ValueError(f"Unsupported authentication for {profile}")
    return "".join(f"{key}={odbc_value(value)};" for key, value in parts.items()) + (
        "APP=ERP-SchemaInspector;Connection Timeout=10;"
    )


def connection_string(profile=None):
    if profile is not None:
        return profile_connection_string(profile)
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


def render_catalog(objects, columns, foreign_keys, profile=None):
    grouped = defaultdict(list)
    for column in columns:
        grouped[(column[0], column[1])].append(column)
    candidates = list(objects) if profile else [(schema, name, kind) for schema, name, kind in objects if is_candidate(name, [column[2] for column in grouped[(schema, name)]])]
    lines = [
        "# 原 ERP 数据库结构目录",
        "",
        "此文件由 `tools/inspect_source_schema.py` 从系统元数据生成；未读取业务记录。",
        "",
        f"- 数据源：{profile or 'legacy .env'}",
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=profiles(), help="Named source; omitted uses legacy .env")
    parser.add_argument("--list", action="store_true", help="List configured sources without connecting")
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--check", action="store_true", help="Check connection and count visible tables/views")
    action.add_argument("--find", help="Find tables, views or columns by substring")
    args = parser.parse_args()
    if args.list:
        for name, config in profiles().items():
            print(f"{name}: {config['server']} / {config['database']} ({config['authentication']})")
        return
    if not args.profile:
        load_dotenv(ENV_FILE)
    with pyodbc.connect(connection_string(args.profile), readonly=True, timeout=10) as connection:
        connection.timeout = 30
        if args.check:
            print(connection.execute("SELECT DB_NAME(), (SELECT COUNT(*) FROM sys.tables), (SELECT COUNT(*) FROM sys.views)").fetchone())
            return
        objects, columns, foreign_keys = fetch_metadata(connection)
    if args.find:
        needle = args.find.casefold()
        for column in columns:
            if needle in ".".join(column[:3]).casefold():
                print(f"{column[0]}.{column[1]}.{column[2]}: {column[3]}")
        return
    output = ROOT / "outputs" / "source-schemas" / f"{args.profile}.md" if args.profile else OUTPUT_FILE
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_catalog(objects, columns, foreign_keys, args.profile), encoding="utf-8")
    print(f"已写入 {output}")
    print(f"发现 {len(objects)} 个对象、{len(foreign_keys)} 条外键关系。")


if __name__ == "__main__":
    main()
