"""Material code allocation compatible with the legacy pt_mstr view.

The legacy database remains the source of truth for the next serial.  A local
allocation is used only when that read-only source is unavailable, so a new
installation can still be used while the connection is being configured.
"""

from __future__ import annotations

import os
import re
import threading
import time
import logging


_CACHE = {}
_CACHE_LOCK = threading.Lock()
_CACHE_TTL = 30
logger = logging.getLogger(__name__)


def _load_env():
    root = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(root, ".env")
    try:
        with open(path, encoding="utf-8") as stream:
            for line in stream:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    except OSError:
        return


def _source_codes(prefix):
    """Read pt_part values from the configured view, returning None on failure."""
    now = time.monotonic()
    with _CACHE_LOCK:
        cached = _CACHE.get(prefix)
        if cached and now - cached[0] < _CACHE_TTL:
            return cached[1]
    _load_env()
    values = []
    try:
        import pyodbc

        required = ("ERP_SOURCE_DB_HOST", "ERP_SOURCE_DB_PORT", "ERP_SOURCE_DB_NAME", "ERP_SOURCE_DB_USER", "ERP_SOURCE_DB_PASSWORD")
        if not all(os.getenv(key) for key in required):
            raise RuntimeError("source database is not configured")
        view = os.getenv("ERP_SOURCE_DB_VIEW", "V_AI_PT_MSTR")
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", view):
            raise RuntimeError("invalid source view name")
        # V_AI_PT_MSTR is published in the legacy coerp_base database while
        # the application login may default to a site database.
        catalog = os.getenv("ERP_SOURCE_DB_CATALOG", "coerp_base").strip()
        if catalog and not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", catalog):
            raise RuntimeError("invalid source catalog name")
        object_name = f"[{catalog}].[dbo].[{view}]" if catalog else f"[dbo].[{view}]"
        connection_string = (
            "DRIVER={SQL Server};"
            f"SERVER={os.environ['ERP_SOURCE_DB_HOST']},{os.environ['ERP_SOURCE_DB_PORT']};"
            f"DATABASE={os.environ['ERP_SOURCE_DB_NAME']};"
            f"UID={os.environ['ERP_SOURCE_DB_USER']};"
            f"PWD={os.environ['ERP_SOURCE_DB_PASSWORD']};"
            "APP=ERP-MaterialCode;Connection Timeout=3;"
        )
        with pyodbc.connect(connection_string, readonly=True, timeout=3) as connection:
            cursor = connection.cursor()
            result = cursor.execute(f"SELECT TOP 0 * FROM {object_name}")
            actual_columns = [item[0] for item in result.description or ()]
            normalized_columns = [str(name).lower() for name in actual_columns]
            part_index = next((index for index, name in enumerate(normalized_columns) if name in {"pt_part", "part", "material_code", "物料编码"}), None)
            if part_index is None:
                raise RuntimeError("source view has no material code column")
            part_column = actual_columns[part_index]
            result = cursor.execute(f"SELECT [{part_column}] FROM {object_name} WHERE [{part_column}] LIKE ?", (f"{prefix}-%",))
            values = [str(row[0]).strip() for row in result.fetchall() if row[0]]
    except Exception as exc:
        values = None
        logger.warning("无法读取物料编码源视图（前缀 %s），将使用本地回退：%s", prefix, exc)
    with _CACHE_LOCK:
        _CACHE[prefix] = (time.monotonic(), values)
    return values


def _allocation_state(prefix, local_codes):
    """Return the next serial and width from the authoritative source when available."""
    prefix = (prefix or "").strip()
    if not prefix:
        return ""
    marker = f"{prefix}-"
    source_codes = _source_codes(prefix)
    # A successful source read is authoritative.  Local values are only a
    # temporary fallback for an unavailable source connection.
    source_values = [str(code).strip() for code in (source_codes or []) if str(code).strip().startswith(marker)]
    local_values = [str(code).strip() for code in local_codes if str(code).strip().startswith(marker)]
    codes = source_values if source_codes is not None else local_values
    parsed = []
    for code in codes:
        suffix = code[len(marker):]
        if suffix.isdigit():
            parsed.append((int(suffix), len(suffix)))
    serial = max((item[0] for item in parsed), default=0)
    width = max((item[1] for item in parsed if item[0] == serial), default=4)
    if source_codes is not None and parsed:
        # Include locally allocated values only when they form a contiguous
        # run immediately after the source maximum.  This prevents stale
        # four/six-digit local values from overriding the legacy maximum,
        # while avoiding duplicates before a new row reaches the source view.
        local_serials = {}
        for code in local_values:
            suffix = code[len(marker):]
            if suffix.isdigit():
                local_serials[int(suffix)] = len(suffix)
        while serial + 1 in local_serials:
            serial += 1
            width = max(width, local_serials[serial])
    return serial, width


def allocate_material_codes(prefix, local_codes, count):
    """Allocate a contiguous code range while reading each source prefix once."""
    if count <= 0:
        return []
    serial, width = _allocation_state(prefix, local_codes)
    return [f"{prefix}-{number:0{width}d}" for number in range(serial + 1, serial + count + 1)]


def allocate_material_code(prefix, local_codes):
    """Return the next code, preserving the source prefix and serial width."""
    codes = allocate_material_codes(prefix, local_codes, 1)
    return codes[0] if codes else ""
