from typing import Optional, List
from pydantic import BaseModel, Field


# Document Classification
class DocumentClassification(BaseModel):
    document_type: str
    confidence: float


# Invoice Item
class InvoiceItem(BaseModel):
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    amount: Optional[float] = None


# Invoice Data
class InvoiceData(BaseModel):
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None

    seller_name: Optional[str] = None
    seller_address: Optional[str] = None

    buyer_name: Optional[str] = None
    buyer_address: Optional[str] = None

    subtotal: Optional[float] = None
    tax: Optional[float] = None
    discount: Optional[float] = None
    total: Optional[float] = None

    currency: Optional[str] = None

    items: List[InvoiceItem] = Field(default_factory=list)