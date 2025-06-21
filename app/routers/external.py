from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.database.database import get_db
from app.models.note import User, Transaction
from app.schemas.note import (
    TransactionCreate, Transaction as TransactionSchema,
    TransactionUpdate, Message
)
from app.auth import get_current_active_user
import logging

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/", response_model=TransactionSchema, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new transaction"""
    try:
        db_transaction = Transaction(
            user_id=current_user.id,
            **transaction.dict()
        )
        
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        
        logger.info(f"Transaction created: {db_transaction.id} by user {current_user.username}")
        return db_transaction
        
    except Exception as e:
        logger.error(f"Error creating transaction: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/", response_model=List[TransactionSchema])
def get_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    transaction_type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user transactions with optional filtering"""
    try:
        query = db.query(Transaction).filter(Transaction.user_id == current_user.id)
        
        # Apply filters
        if transaction_type:
            query = query.filter(Transaction.transaction_type == transaction_type)
        
        if category:
            query = query.filter(Transaction.category == category)
        
        if start_date:
            query = query.filter(Transaction.date >= start_date)
        
        if end_date:
            query = query.filter(Transaction.date <= end_date)
        
        # Order by date (newest first)
        query = query.order_by(Transaction.date.desc())
        
        transactions = query.offset(skip).limit(limit).all()
        
        logger.info(f"Retrieved {len(transactions)} transactions for user {current_user.username}")
        return transactions
        
    except Exception as e:
        logger.error(f"Error retrieving transactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{transaction_id}", response_model=TransactionSchema)
def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific transaction by ID"""
    try:
        transaction = db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id
        ).first()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        return transaction
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving transaction {transaction_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/{transaction_id}", response_model=TransactionSchema)
def update_transaction(
    transaction_id: int,
    transaction_update: TransactionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a transaction"""
    try:
        transaction = db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id
        ).first()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        # Update only provided fields
        update_data = transaction_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(transaction, field, value)
        
        db.commit()
        db.refresh(transaction)
        
        logger.info(f"Transaction updated: {transaction_id} by user {current_user.username}")
        return transaction
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating transaction {transaction_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{transaction_id}", response_model=Message)
def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a transaction"""
    try:
        transaction = db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id
        ).first()
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        db.delete(transaction)
        db.commit()
        
        logger.info(f"Transaction deleted: {transaction_id} by user {current_user.username}")
        return {"message": "Transaction deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting transaction {transaction_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/summary/period", response_model=dict)
def get_transaction_summary(
    period: str = Query("month", regex="^(day|week|month|year)$"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get transaction summary for a specific period"""
    try:
        now = datetime.now()
        
        # Calculate start date based on period
        if period == "day":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "month":
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:  # year
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get transactions for the period
        transactions = db.query(Transaction).filter(
            Transaction.user_id == current_user.id,
            Transaction.date >= start_date
        ).all()
        
        # Calculate summary
        total_income = sum(t.amount for t in transactions if str(t.transaction_type) == "income")
        total_expenses = sum(t.amount for t in transactions if str(t.transaction_type) == "expense")
        net_amount = total_income - total_expenses
        
        summary = {
            "period": period,
            "start_date": start_date.isoformat(),
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_amount": net_amount,
            "transaction_count": len(transactions),
            "currency": "USD"  # Default currency
        }
        
        logger.info(f"Transaction summary generated for user {current_user.username}: {period}")
        return summary
        
    except Exception as e:
        logger.error(f"Error generating transaction summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
