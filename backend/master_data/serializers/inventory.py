from backend.models import StockBalance, StockCount, StockCountLine, StockTransaction, StockTransfer, StockTransferLine

from .common import serializer_for

StockBalanceSerializer = serializer_for(StockBalance)


StockTransactionSerializer = serializer_for(StockTransaction)


StockTransferSerializer = serializer_for(StockTransfer)


StockTransferLineSerializer = serializer_for(StockTransferLine)


StockCountSerializer = serializer_for(StockCount)


StockCountLineSerializer = serializer_for(StockCountLine)
