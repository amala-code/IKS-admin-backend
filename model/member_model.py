
from typing import Optional
from pydantic import BaseModel, EmailStr


class Member(BaseModel):
    name: str
    address: str
    email: EmailStr
    phone: str
    id: str  # Custom ID field
    year_of_joining: int
    amount_paid_total: float
    member_true: bool
    amount_paid_registration: float
    amount_paid_subscription: float
    amount_subscription: bool

class MemberUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    year_of_joining: Optional[int] = None
    amount_paid_total: Optional[float] = None
    member_true: Optional[bool] = None
    amount_paid_registration: Optional[float] = None
    amount_paid_subscription: Optional[float] = None
    amount_subscription: Optional[bool] = None