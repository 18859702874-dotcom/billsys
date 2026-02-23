from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import Transaction, AssetCategory
from schemas import TransactionCreate, TransactionUpdate, TransactionOut, TransactionSummary

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


def _enrich(tx: Transaction, db: Session) -> dict:
    """将 Transaction ORM 对象转成 TransactionOut 所需字典"""
    cat_name = None
    parent_cat_name = None
    if tx.category_id and tx.category:
        cat_name = tx.category.name
        if tx.category.parent_id:
            parent = db.query(AssetCategory).get(tx.category.parent_id)
            if parent:
                parent_cat_name = parent.name
    return {
        "id": tx.id,
        "amount": tx.amount,
        "type": tx.type,
        "category_id": tx.category_id,
        "category_name": cat_name,
        "parent_category_name": parent_cat_name,
        "date": tx.date,
        "payment_method": tx.payment_method,
        "notes": tx.notes,
        "created_at": tx.created_at,
        "updated_at": tx.updated_at,
    }


@router.get("/summary", response_model=TransactionSummary)
def get_transaction_summary(
    year: int = Query(...),
    month: int = Query(...),
    db: Session = Depends(get_db),
):
    from datetime import date
    start = date(year, month, 1)
    import calendar
    last_day = calendar.monthrange(year, month)[1]
    end = date(year, month, last_day)

    rows = db.query(Transaction.type, func.sum(Transaction.amount)).filter(
        Transaction.date >= start,
        Transaction.date <= end,
    ).group_by(Transaction.type).all()

    total_expense = Decimal("0")
    total_income = Decimal("0")
    for tx_type, total in rows:
        if tx_type == "expense":
            total_expense = total or Decimal("0")
        elif tx_type == "income":
            total_income = total or Decimal("0")

    return {"year": year, "month": month, "total_expense": total_expense, "total_income": total_income}


@router.get("", response_model=List[TransactionOut])
def list_transactions(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Transaction)

    if year and month:
        from datetime import date
        import calendar
        start = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end = date(year, month, last_day)
        q = q.filter(Transaction.date >= start, Transaction.date <= end)
    elif year:
        from datetime import date
        start = date(year, 1, 1)
        end = date(year, 12, 31)
        q = q.filter(Transaction.date >= start, Transaction.date <= end)

    if category_id:
        q = q.filter(Transaction.category_id == category_id)

    if type:
        q = q.filter(Transaction.type == type)

    txs = q.order_by(Transaction.date.desc(), Transaction.id.desc()).all()
    return [_enrich(tx, db) for tx in txs]


@router.post("", response_model=TransactionOut)
def create_transaction(data: TransactionCreate, db: Session = Depends(get_db)):
    if data.category_id:
        cat = db.query(AssetCategory).get(data.category_id)
        if not cat:
            raise HTTPException(400, "分类不存在")

    tx = Transaction(
        amount=data.amount,
        type=data.type,
        category_id=data.category_id,
        date=data.date,
        payment_method=data.payment_method,
        notes=data.notes,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return _enrich(tx, db)


@router.put("/{tx_id}", response_model=TransactionOut)
def update_transaction(tx_id: int, data: TransactionUpdate, db: Session = Depends(get_db)):
    tx = db.query(Transaction).get(tx_id)
    if not tx:
        raise HTTPException(404, "交易记录不存在")

    if data.amount is not None:
        tx.amount = data.amount
    if data.type is not None:
        tx.type = data.type
    if "category_id" in data.model_fields_set:
        if data.category_id:
            cat = db.query(AssetCategory).get(data.category_id)
            if not cat:
                raise HTTPException(400, "分类不存在")
        tx.category_id = data.category_id
    if data.date is not None:
        tx.date = data.date
    if "payment_method" in data.model_fields_set:
        tx.payment_method = data.payment_method
    if "notes" in data.model_fields_set:
        tx.notes = data.notes

    db.commit()
    db.refresh(tx)
    return _enrich(tx, db)


@router.delete("/{tx_id}")
def delete_transaction(tx_id: int, db: Session = Depends(get_db)):
    tx = db.query(Transaction).get(tx_id)
    if not tx:
        raise HTTPException(404, "交易记录不存在")
    db.delete(tx)
    db.commit()
    return {"ok": True}
