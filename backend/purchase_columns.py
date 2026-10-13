import json
from pathlib import Path

_columns = json.loads((Path(__file__).resolve().parent.parent / "shared/purchase-columns.json").read_text(encoding="utf8"))
ORDER_COLUMNS = _columns["order"]
ALLOCATION_COLUMNS = _columns["allocation"]
