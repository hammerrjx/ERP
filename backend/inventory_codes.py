"""dgyzx1 inventory transaction codes used by the local operational ledger."""
PLAN_RECEIPT = "110"
PURCHASE_RECEIPT = "120"
PURCHASE_RETURN = "220"
TRANSFER_IN = "150"
TRANSFER_OUT = "250"
PLAN_ISSUE = "210"
SALES_DELIVERY = "260"
SALES_RETURN = "261"
COUNT_ADJUSTMENT = "310"
COST_ADJUSTMENT = "501"
LEGACY_TO_SOURCE = {
    "purchase_receipt": PURCHASE_RECEIPT,
    "purchase_return": PURCHASE_RETURN, "sales_delivery": SALES_DELIVERY,
    "sales_return": SALES_RETURN, "transfer_in": TRANSFER_IN,
    "transfer_out": TRANSFER_OUT, "count_adjustment": COUNT_ADJUSTMENT,
}
def source_code(value):
    return LEGACY_TO_SOURCE.get(value, value)
