"""
Banking endpoints for the Banking User Account Dashboard
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from ..database import (
    bank_users_collection,
    bank_accounts_collection,
    bank_transactions_collection
)

router = APIRouter(
    prefix="/banking",
    tags=["banking"]
)

ph = PasswordHasher()


def verify_user(username: str) -> Dict[str, Any]:
    """Verify user exists and return user document"""
    user = bank_users_collection.find_one({"_id": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/login")
def bank_login(username: str, password: str) -> Dict[str, Any]:
    """Authenticate a banking user"""
    user = bank_users_collection.find_one({"_id": username})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    try:
        ph.verify(user["password"], password)
    except VerifyMismatchError:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {
        "username": user["username"],
        "display_name": user["display_name"],
        "email": user["email"],
        "phone": user["phone"],
        "address": user["address"]
    }


@router.get("/accounts/{username}")
def get_accounts(username: str) -> List[Dict[str, Any]]:
    """Get all accounts for a user"""
    verify_user(username)
    accounts = []
    for account in bank_accounts_collection.find({"owner_username": username}):
        account["account_number"] = account.pop("_id")
        accounts.append(account)
    return accounts


@router.get("/accounts/{username}/{account_number}/transactions")
def get_transactions(
    username: str,
    account_number: str,
    limit: Optional[int] = 10
) -> List[Dict[str, Any]]:
    """Get recent transactions for a specific account"""
    verify_user(username)

    account = bank_accounts_collection.find_one({"_id": account_number, "owner_username": username})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    transactions = list(
        bank_transactions_collection
        .find({"account_number": account_number})
        .sort("date", -1)
        .limit(limit)
    )

    for txn in transactions:
        txn["id"] = str(txn.pop("_id"))

    return transactions


@router.post("/transfer")
def transfer_funds(
    username: str,
    from_account: str,
    to_account: str,
    amount: float,
    description: Optional[str] = "Transfer"
) -> Dict[str, Any]:
    """Transfer funds between two accounts owned by the user"""
    verify_user(username)

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Transfer amount must be greater than zero")

    src = bank_accounts_collection.find_one({"_id": from_account, "owner_username": username})
    if not src:
        raise HTTPException(status_code=404, detail="Source account not found")

    dst = bank_accounts_collection.find_one({"_id": to_account, "owner_username": username})
    if not dst:
        raise HTTPException(status_code=404, detail="Destination account not found")

    # Enforce balance / credit-limit checks
    if src["account_type"] == "credit":
        credit_limit = src.get("credit_limit", 0)
        # balance is negative when in debt; going more negative reduces available credit
        available_credit = credit_limit + src["balance"]  # e.g. 5000 + (-950) = 4050
        if amount > available_credit:
            raise HTTPException(status_code=400, detail="Transfer would exceed credit limit")
    else:
        if src["balance"] < amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")

    new_src_balance = src["balance"] - amount
    new_dst_balance = dst["balance"] + amount

    from datetime import date
    import uuid
    today = date.today().isoformat()
    txn_id_src = f"TXN-{uuid.uuid4().hex[:8].upper()}"
    txn_id_dst = f"TXN-{uuid.uuid4().hex[:8].upper()}"

    # Use a client session for atomicity where supported
    with bank_accounts_collection.database.client.start_session() as session:
        try:
            with session.start_transaction():
                bank_accounts_collection.update_one(
                    {"_id": from_account}, {"$set": {"balance": new_src_balance}}, session=session
                )
                bank_accounts_collection.update_one(
                    {"_id": to_account}, {"$set": {"balance": new_dst_balance}}, session=session
                )
                bank_transactions_collection.insert_one({
                    "transaction_id": txn_id_src,
                    "account_number": from_account,
                    "type": "debit",
                    "amount": amount,
                    "description": description,
                    "category": "Transfer",
                    "date": today,
                    "balance_after": new_src_balance
                }, session=session)
                bank_transactions_collection.insert_one({
                    "transaction_id": txn_id_dst,
                    "account_number": to_account,
                    "type": "credit",
                    "amount": amount,
                    "description": description,
                    "category": "Transfer",
                    "date": today,
                    "balance_after": new_dst_balance
                }, session=session)
        except Exception:
            session.abort_transaction()
            raise HTTPException(status_code=500, detail="Transfer failed; no changes were made")

    return {
        "message": f"Successfully transferred ${amount:.2f}",
        "from_account": from_account,
        "to_account": to_account,
        "amount": amount,
        "new_from_balance": new_src_balance,
        "new_to_balance": new_dst_balance
    }
