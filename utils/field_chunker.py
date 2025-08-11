# utils/field_chunker.py
"""
Field-aware text for bank-core schema transactions.json

Expected keys (any missing are handled safely):
- transactionId, accountId, personId
- transactionType, transactionStatus
- amount (float), debitCreditIndicator ("1" or "-1")
- transactionDateTime (ISO)
- currencyCode
- displayTransactionType
- merchantId, merchantName, merchantCategoryName
- isMerchantCredit, cardType, transactionCode
- isInstallmentConversionEligible, lastFourDigits, isRecurring
"""

from typing import Dict

def signed_amount(txn: Dict) -> float:
    amt = float(txn.get("amount", 0.0) or 0.0)
    dci = txn.get("debitCreditIndicator")
    try:
        mult = float(dci)
    except Exception:
        # Fallback for texty flags; tune if your data uses other labels
        mult = -1.0 if str(dci).strip().lower() in {"-1", "debit", "outflow"} else 1.0
    return round(amt * mult, 2)

def transaction_to_text(txn: Dict) -> str:
    """Weighted summary used for embeddings & context."""
    txid   = txn.get("transactionId", "")
    ttype  = txn.get("transactionType", "")
    status = txn.get("transactionStatus", "")
    date   = txn.get("transactionDateTime", "") or txn.get("date", "")
    ccy    = txn.get("currencyCode", "USD")
    merch  = txn.get("merchantName", "") or txn.get("merchant", "")
    mcat   = txn.get("merchantCategoryName", "")
    disp   = txn.get("displayTransactionType", "")
    recur  = txn.get("isRecurring", False)
    s_amt  = signed_amount(txn)

    # Weight merchant/type/category/amount
    return (
        f"Transaction {txid}. "
        f"Date: {date}. "
        f"Type: {ttype}. Type: {ttype}. "
        f"Status: {status}. "
        f"DisplayType: {disp}. "
        f"Merchant: {merch}. Merchant: {merch}. "
        f"Category: {mcat}. Category: {mcat}. "
        f"SignedAmount: {s_amt} {ccy}. SignedAmount: {s_amt} {ccy}. "
        f"Recurring: {bool(recur)}."
    )