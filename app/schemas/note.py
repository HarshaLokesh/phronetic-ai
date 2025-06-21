from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class PeriodType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


# User Schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Transaction Schemas
class TransactionBase(BaseModel):
    amount: float = Field(..., gt=0)
    currency: str = Field(default="USD", max_length=3)
    description: str = Field(..., min_length=1, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    transaction_type: TransactionType
    date: datetime = Field(default_factory=datetime.now)


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = Field(None, max_length=3)
    description: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    transaction_type: Optional[TransactionType] = None
    date: Optional[datetime] = None


class Transaction(TransactionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Budget Schemas
class BudgetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    amount: float = Field(..., gt=0)
    currency: str = Field(default="USD", max_length=3)
    period: PeriodType = Field(default=PeriodType.MONTHLY)
    category: Optional[str] = Field(None, max_length=100)
    start_date: datetime
    end_date: Optional[datetime] = None


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    amount: Optional[float] = Field(None, gt=0)
    currency: Optional[str] = Field(None, max_length=3)
    period: Optional[PeriodType] = None
    category: Optional[str] = Field(None, max_length=100)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None


class Budget(BudgetBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# User Preference Schemas
class UserPreferenceBase(BaseModel):
    default_currency: str = Field(default="USD", max_length=3)
    timezone: str = Field(default="UTC", max_length=50)
    notification_enabled: bool = Field(default=True)
    theme: str = Field(default="light", max_length=20)
    language: str = Field(default="en", max_length=10)


class UserPreferenceCreate(UserPreferenceBase):
    pass


class UserPreferenceUpdate(BaseModel):
    default_currency: Optional[str] = Field(None, max_length=3)
    timezone: Optional[str] = Field(None, max_length=50)
    notification_enabled: Optional[bool] = None
    theme: Optional[str] = Field(None, max_length=20)
    language: Optional[str] = Field(None, max_length=10)


class UserPreference(UserPreferenceBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# API Response Schemas
class Message(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


# Analytics Schemas
class TransactionSummary(BaseModel):
    total_income: float
    total_expenses: float
    net_amount: float
    currency: str
    period: str
    transaction_count: int


class CategorySummary(BaseModel):
    category: str
    total_amount: float
    transaction_count: int
    percentage: float


class BudgetProgress(BaseModel):
    budget_id: int
    budget_name: str
    budget_amount: float
    spent_amount: float
    remaining_amount: float
    progress_percentage: float
    currency: str
