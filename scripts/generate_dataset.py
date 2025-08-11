# scripts/generate_dataset.py
import json
import random
import argparse
from datetime import datetime, timedelta
from uuid import uuid4

# --- Merchants and categories ---
MERCHANTS = [
    ("Amazon", "ELECTRONICS"),
    ("Costco", "GROCERIES"),
    ("Walmart", "GROCERIES"),
    ("Starbucks", "DINING"),
    ("Delta Airlines", "TRAVEL"),
    ("Uber", "TRAVEL"),
    ("Apple", "ELECTRONICS"),
    ("Best Buy", "ELECTRONICS"),
    ("Southwest Airlines", "TRAVEL"),
    ("Shell", "FUEL"),
    ("Netflix", "ENTERTAINMENT"),
    ("Home Depot", "HOME_IMPROVEMENT"),
    ("Marriott", "TRAVEL"),
    ("Subway", "DINING"),
    ("Target", "GROCERIES")
]

CARD_TYPES = ["DIGITAL", "DEBIT", "CREDIT"]
CURRENCY = "USD"

def rand_date(start: datetime, end: datetime) -> datetime:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, max(0, delta)))

def txn_id() -> str:
    return str(uuid4())

def last4() -> str:
    return f"{random.randint(0, 9999):04d}"

def gen_intervals(start_dt: datetime, months: int):
    # Monthly “statement-like” cadence
    d = start_dt
    for _ in range(months):
        yield d
        # Move roughly one month ahead (30 days to keep it simple)
        d = d + timedelta(days=30)

def make_txn(
    tdt: datetime,
    ttype: str,
    amount_abs: float,
    debit_credit_indicator: int,
    merchant_name: str | None = None,
    merchant_category: str | None = None,
    display_type: str | None = None,
    is_recurring: bool = False,
    account_id: str = "acct-0001",
    person_id: str = "person-0001",
) -> dict:
    """Produce a single transaction in your bank-core schema."""
    return {
        "transactionId": txn_id(),
        "accountId": account_id,
        "personId": person_id,
        "transactionType": ttype,                   # PURCHASE | PAYMENT | INTEREST | INSTALLMENT
        "transactionStatus": "POSTED",
        "amount": round(float(amount_abs), 2),      # always positive absolute amount
        "endingBalance": round(random.uniform(100, 5000), 2),
        "debitCreditIndicator": str(int(debit_credit_indicator)),  # "1" (charge/credit to account) or "-1" (payment/outflow)
        "transactionDateTime": tdt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "currencyCode": CURRENCY,
        "displayTransactionType": display_type or ttype.lower(),
        "merchantId": str(random.randint(10000, 99999)),
        "merchantName": merchant_name or "",
        "merchantCategoryName": merchant_category or "",
        "isMerchantCredit": False,
        "cardType": random.choice(CARD_TYPES),
        "transactionCode": str(random.randint(20000, 39999)),
        "isInstallmentConversionEligible": False,
        "lastFourDigits": last4(),
        "isRecurring": bool(is_recurring),
    }

def generate_dataset(
    n: int = 200,
    start: str = "2023-01-01",
    end: str = None,
    account_id: str = "acct-0001",
    person_id: str = "person-0001",
    seed: int | None = 42,
):
    """
    Generate a realistic mix of PURCHASE / PAYMENT / INTEREST / INSTALLMENT transactions.
    Semantics:
      - PURCHASE, INTEREST, INSTALLMENT -> debitCreditIndicator = "1"  (adds to balance)
      - PAYMENT                         -> debitCreditIndicator = "-1" (reduces balance)
      - 'amount' remains positive; the sign is implied by debitCreditIndicator
    """
    if seed is not None:
        random.seed(seed)

    start_dt = datetime.fromisoformat(start)
    end_dt = datetime.utcnow() if end is None else datetime.fromisoformat(end)

    txns: list[dict] = []

    # 1) Seed some monthly INTEREST charges
    for d in gen_intervals(rand_date(start_dt, end_dt - timedelta(days=360)), months=12):
        interest_amt = round(random.uniform(5, 25), 2)
        txns.append(
            make_txn(
                d, "INTEREST", interest_amt, +1,
                merchant_name="Interest charge",
                merchant_category="OTHER",
                display_type="interest_charged",
                is_recurring=True,
                account_id=account_id, person_id=person_id,
            )
        )

    # 2) Seed a few INSTALLMENT series (e.g., 6 or 12 months)
    for _ in range(2):
        months = random.choice([6, 12])
        base_start = rand_date(start_dt, end_dt - timedelta(days=months * 30))
        total_purchase = round(random.uniform(300, 2500), 2)
        per_month = round(total_purchase / months, 2)
        # first record the INSTALLMENT entries
        for d in gen_intervals(base_start, months):
            txns.append(
                make_txn(
                    d, "INSTALLMENT", per_month, +1,
                    merchant_name=random.choice(MERCHANTS)[0],
                    merchant_category="INSTALLMENT",
                    display_type="installment",
                    is_recurring=True,
                    account_id=account_id, person_id=person_id,
                )
            )

    # 3) Random PURCHASES + PAYMENTS distributed uniformly
    for _ in range(max(0, n - len(txns))):
        d = rand_date(start_dt, end_dt)
        (mname, mcat) = random.choice(MERCHANTS)

        # favor small Dining/Fuel amounts; larger for Electronics/Travel
        if mcat in ("DINING", "FUEL"):
            amt = round(random.uniform(3, 50), 2)
        elif mcat in ("ELECTRONICS", "TRAVEL", "HOME_IMPROVEMENT"):
            amt = round(random.uniform(80, 3500), 2)
        else:
            amt = round(random.uniform(10, 400), 2)

        # choose type: mostly PURCHASE, some PAYMENTS to offset, occasional INTEREST already added above
        ttype = random.choices(
            population=["PURCHASE", "PAYMENT", "PURCHASE", "PURCHASE"],
            weights=[0.55, 0.20, 0.15, 0.10],
            k=1
        )[0]

        if ttype == "PAYMENT":
            # Payment reduces balance => indicator -1 (amount still positive)
            txns.append(
                make_txn(
                    d, "PAYMENT", round(random.uniform(20, 1200), 2), -1,
                    merchant_name="Payment Received",
                    merchant_category="PAYMENT",
                    display_type="payment",
                    is_recurring=False,
                    account_id=account_id, person_id=person_id,
                )
            )
        else:
            txns.append(
                make_txn(
                    d, ttype, amt, +1,
                    merchant_name=mname,
                    merchant_category=mcat,
                    display_type="purchase" if ttype == "PURCHASE" else ttype.lower(),
                    is_recurring=False,
                    account_id=account_id, person_id=person_id,
                )
            )

    # Sort by date
    txns.sort(key=lambda t: t["transactionDateTime"])

    return txns

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--start", default="2023-01-01")
    ap.add_argument("--end", default=None)
    ap.add_argument("--account-id", default="acct-0001")
    ap.add_argument("--person-id", default="person-0001")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default="data/transactions.json")
    args = ap.parse_args()

    txns = generate_dataset(
        n=args.n,
        start=args.start,
        end=args.end,
        account_id=args.account_id,
        person_id=args.person_id,
        seed=args.seed,
    )
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(txns, f, indent=2)
    print(f"✔ Wrote {len(txns)} transactions to {args.out}")

if __name__ == "__main__":
    main()