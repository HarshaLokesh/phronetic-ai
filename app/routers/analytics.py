from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import httpx
import json
import logging

from app.database.database import get_db
from app.models.note import User, Transaction, Budget
from app.auth import get_current_active_user
from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/currency/convert")
async def convert_currency(
    amount: float = Query(..., gt=0),
    from_currency: str = Query(..., min_length=3, max_length=3),
    to_currency: str = Query(..., min_length=3, max_length=3)
):
    """Convert currency using external API"""
    try:
        async with httpx.AsyncClient() as client:
            # Use free currency conversion API
            response = await client.get(
                f"{settings.currency_api_url}/{from_currency.upper()}"
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Currency conversion service unavailable"
                )
            
            data = response.json()
            rates = data.get("rates", {})
            
            if to_currency.upper() not in rates:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Currency {to_currency} not supported"
                )
            
            conversion_rate = rates[to_currency.upper()]
            converted_amount = amount * conversion_rate
            
            result = {
                "original_amount": amount,
                "original_currency": from_currency.upper(),
                "converted_amount": round(converted_amount, 2),
                "target_currency": to_currency.upper(),
                "conversion_rate": conversion_rate,
                "last_updated": data.get("date")
            }
            
            logger.info(f"Currency conversion: {amount} {from_currency} -> {converted_amount} {to_currency}")
            return result
            
    except Exception as e:
        logger.error(f"Currency conversion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/transactions/category-breakdown")
def get_category_breakdown(
    period: str = Query("month", regex="^(day|week|month|year)$"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get transaction breakdown by category with data transformation"""
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
        
        # Get transactions grouped by category
        transactions = db.query(
            Transaction.category,
            func.sum(Transaction.amount).label('total_amount'),
            func.count(Transaction.id).label('transaction_count')
        ).filter(
            and_(
                Transaction.user_id == current_user.id,
                Transaction.date >= start_date,
                Transaction.transaction_type == "expense"
            )
        ).group_by(Transaction.category).all()
        
        # Calculate total expenses for percentage calculation
        total_expenses = sum(t.total_amount for t in transactions)
        
        # Transform data for better visualization
        breakdown = []
        for transaction in transactions:
            category = transaction.category or "Uncategorized"
            percentage = (transaction.total_amount / total_expenses * 100) if total_expenses > 0 else 0
            
            breakdown.append({
                "category": category,
                "total_amount": float(transaction.total_amount),
                "transaction_count": transaction.transaction_count,
                "percentage": round(percentage, 2),
                "color": get_category_color(category)  # Add color for UI
            })
        
        # Sort by amount (highest first)
        breakdown.sort(key=lambda x: x["total_amount"], reverse=True)
        
        result = {
            "period": period,
            "start_date": start_date.isoformat(),
            "total_expenses": total_expenses,
            "category_count": len(breakdown),
            "breakdown": breakdown
        }
        
        logger.info(f"Category breakdown generated for user {current_user.username}: {period}")
        return result
        
    except Exception as e:
        logger.error(f"Error generating category breakdown: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/budgets/progress")
def get_budget_progress(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get budget progress with data transformation"""
    try:
        # Get active budgets
        budgets = db.query(Budget).filter(
            and_(
                Budget.user_id == current_user.id,
                Budget.is_active == True
            )
        ).all()
        
        budget_progress = []
        
        for budget in budgets:
            # Calculate spent amount for this budget
            if budget.category is not None:
                spent_query = db.query(func.sum(Transaction.amount)).filter(
                    and_(
                        Transaction.user_id == current_user.id,
                        Transaction.category == budget.category,
                        Transaction.transaction_type == "expense",
                        Transaction.date >= budget.start_date
                    )
                )
                if budget.end_date is not None:
                    spent_query = spent_query.filter(Transaction.date <= budget.end_date)
                
                spent_amount = spent_query.scalar() or 0
            else:
                # For general budgets, consider all expenses
                spent_query = db.query(func.sum(Transaction.amount)).filter(
                    and_(
                        Transaction.user_id == current_user.id,
                        Transaction.transaction_type == "expense",
                        Transaction.date >= budget.start_date
                    )
                )
                if budget.end_date is not None:
                    spent_query = spent_query.filter(Transaction.date <= budget.end_date)
                
                spent_amount = spent_query.scalar() or 0
            
            budget_amount: float = budget.amount  # type: ignore
            remaining_amount = budget_amount - spent_amount
            progress_percentage = (spent_amount / budget_amount * 100) if budget_amount > 0 else 0
            
            # Determine status
            if progress_percentage >= 100:
                budget_status = "exceeded"
            elif progress_percentage >= 80:
                budget_status = "warning"
            else:
                budget_status = "good"
            
            budget_progress.append({
                "budget_id": budget.id,
                "budget_name": budget.name,
                "budget_amount": budget_amount,
                "spent_amount": float(spent_amount),
                "remaining_amount": float(remaining_amount),
                "progress_percentage": round(float(progress_percentage), 2),
                "currency": budget.currency,
                "category": budget.category,
                "period": budget.period,
                "status": budget_status,
                "start_date": budget.start_date.isoformat(),
                "end_date": budget.end_date.isoformat() if budget.end_date is not None else None
            })
        
        # Sort by progress percentage (highest first)
        budget_progress.sort(key=lambda x: x["progress_percentage"], reverse=True)
        
        result = {
            "total_budgets": len(budget_progress),
            "active_budgets": len([b for b in budget_progress if b["status"] == "good"]),
            "warning_budgets": len([b for b in budget_progress if b["status"] == "warning"]),
            "exceeded_budgets": len([b for b in budget_progress if b["status"] == "exceeded"]),
            "budgets": budget_progress
        }
        
        logger.info(f"Budget progress generated for user {current_user.username}")
        return result
        
    except Exception as e:
        logger.error(f"Error generating budget progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/data/transform")
def transform_financial_data(
    data: Dict[str, Any],
    transformation_type: str = Query(..., regex="^(summarize|categorize|normalize|aggregate)$"),
    current_user = Depends(get_current_active_user)
):
    """Transform financial data using various algorithms"""
    try:
        if transformation_type == "summarize":
            result = transform_summarize(data)
        elif transformation_type == "categorize":
            result = transform_categorize(data)
        elif transformation_type == "normalize":
            result = transform_normalize(data)
        elif transformation_type == "aggregate":
            result = transform_aggregate(data)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid transformation type"
            )
        
        logger.info(f"Data transformation completed: {transformation_type}")
        return {
            "transformation_type": transformation_type,
            "input_data": data,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Data transformation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


def get_category_color(category: str) -> str:
    """Get color for category visualization"""
    colors = {
        "Food": "#FF6B6B",
        "Transportation": "#4ECDC4",
        "Entertainment": "#45B7D1",
        "Shopping": "#96CEB4",
        "Bills": "#FFEAA7",
        "Healthcare": "#DDA0DD",
        "Education": "#98D8C8",
        "Travel": "#F7DC6F",
        "Uncategorized": "#BDC3C7"
    }
    return colors.get(category, "#BDC3C7")


def transform_summarize(data: Dict[str, Any]) -> Dict[str, Any]:
    """Summarize financial data"""
    if "transactions" not in data:
        return {"error": "No transactions data provided"}
    
    transactions = data["transactions"]
    
    total_income = sum(t.get("amount", 0) for t in transactions if t.get("type") == "income")
    total_expenses = sum(t.get("amount", 0) for t in transactions if t.get("type") == "expense")
    
    return {
        "total_transactions": len(transactions),
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_amount": total_income - total_expenses,
        "average_transaction": (total_income + total_expenses) / len(transactions) if transactions else 0
    }


def transform_categorize(data: Dict[str, Any]) -> Dict[str, Any]:
    """Categorize financial data"""
    if "transactions" not in data:
        return {"error": "No transactions data provided"}
    
    transactions = data["transactions"]
    categories = {}
    
    for transaction in transactions:
        category = transaction.get("category", "Uncategorized")
        amount = transaction.get("amount", 0)
        
        if category not in categories:
            categories[category] = {"total": 0, "count": 0}
        
        categories[category]["total"] += amount
        categories[category]["count"] += 1
    
    return {"categories": categories}


def transform_normalize(data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize financial data"""
    if "transactions" not in data:
        return {"error": "No transactions data provided"}
    
    transactions = data["transactions"]
    amounts = [t.get("amount", 0) for t in transactions]
    
    if not amounts:
        return {"error": "No valid amounts found"}
    
    min_amount = min(amounts)
    max_amount = max(amounts)
    
    normalized_transactions = []
    for transaction in transactions:
        amount = transaction.get("amount", 0)
        normalized_amount = (amount - min_amount) / (max_amount - min_amount) if max_amount != min_amount else 0
        
        normalized_transactions.append({
            **transaction,
            "normalized_amount": normalized_amount
        })
    
    return {
        "original_range": {"min": min_amount, "max": max_amount},
        "normalized_transactions": normalized_transactions
    }


def transform_aggregate(data: Dict[str, Any]) -> Dict[str, Any]:
    """Aggregate financial data by time periods"""
    if "transactions" not in data:
        return {"error": "No transactions data provided"}
    
    transactions = data["transactions"]
    period = data.get("period", "month")
    
    aggregated = {}
    
    for transaction in transactions:
        date_str = transaction.get("date", "")
        if not date_str:
            continue
        
        try:
            date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            
            if period == "day":
                key = date.strftime("%Y-%m-%d")
            elif period == "week":
                key = f"{date.year}-W{date.isocalendar()[1]}"
            elif period == "month":
                key = date.strftime("%Y-%m")
            else:  # year
                key = str(date.year)
            
            if key not in aggregated:
                aggregated[key] = {"income": 0, "expenses": 0, "count": 0}
            
            amount = transaction.get("amount", 0)
            transaction_type = transaction.get("type", "expense")
            
            if transaction_type == "income":
                aggregated[key]["income"] += amount
            else:
                aggregated[key]["expenses"] += amount
            
            aggregated[key]["count"] += 1
            
        except ValueError:
            continue
    
    return {"aggregated_data": aggregated, "period": period} 