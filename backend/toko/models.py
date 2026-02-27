"""Pydantic Models untuk Toko Module"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

# ========== PRODUCT MODELS ==========
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(default=0, ge=0)
    cost_price: Optional[float] = Field(default=0, ge=0)
    stock: int = Field(default=0, ge=0)
    category: Optional[str] = None
    barcode: Optional[str] = None
    sku: Optional[str] = None
    min_stock: int = Field(default=0, ge=0)
    image_url: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    cost_price: Optional[float] = Field(None, ge=0)
    stock: Optional[int] = Field(None, ge=0)
    category: Optional[str] = None
    barcode: Optional[str] = None
    sku: Optional[str] = None
    min_stock: Optional[int] = Field(None, ge=0)
    image_url: Optional[str] = None
    is_active: Optional[int] = None

class Product(ProductBase):
    id: int
    user_id: int
    is_active: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ========== SALES MODELS ==========
class SaleItem(BaseModel):
    product_id: int
    name: str
    qty: int = Field(..., ge=1)
    price: float = Field(..., ge=0)
    subtotal: float = Field(..., ge=0)
    
    @validator('subtotal', always=True)
    def calculate_subtotal(cls, v, values):
        if 'qty' in values and 'price' in values:
            return values['qty'] * values['price']
        return v

class SaleCreate(BaseModel):
    items: List[SaleItem]
    discount: float = Field(default=0, ge=0)
    tax: float = Field(default=0, ge=0)
    payment_method: str = Field(default='cash')
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    notes: Optional[str] = None
    
    @validator('payment_method')
    def validate_payment_method(cls, v):
        allowed = ['cash', 'transfer', 'qris', 'credit_card', 'debit_card']
        if v not in allowed:
            raise ValueError(f'Payment method must be one of {allowed}')
        return v

class SaleResponse(BaseModel):
    id: int
    user_id: int
    invoice_number: str
    items: List[Dict[str, Any]]
    subtotal: float
    discount: float
    tax: float
    total: float
    profit: float
    payment_method: str
    customer_name: Optional[str]
    customer_phone: Optional[str]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True
        
    @validator('items', pre=True)
    def parse_items(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v

# ========== PURCHASE MODELS ==========
class PurchaseItem(BaseModel):
    product_id: int
    name: str
    qty: int = Field(..., ge=1)
    price: float = Field(..., ge=0)
    subtotal: float = Field(..., ge=0)

class PurchaseCreate(BaseModel):
    supplier_name: Optional[str] = None
    items: List[PurchaseItem]
    notes: Optional[str] = None
    payment_status: str = Field(default='pending')

# ========== INVENTORY MODELS ==========
class StockAdjustment(BaseModel):
    product_id: int
    change: int  # positif untuk tambah, negatif untuk kurangi
    reason: str

class InventoryLog(BaseModel):
    id: int
    user_id: int
    product_id: int
    change: int
    previous_stock: int
    new_stock: int
    reference_type: Optional[str]
    reference_id: Optional[int]
    reason: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# ========== CATEGORY MODELS ==========
class CategoryCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None

class Category(BaseModel):
    id: int
    user_id: int
    name: str
    parent_id: Optional[int]
    
    class Config:
        from_attributes = True

# ========== SUPPLIER MODELS ==========
class SupplierCreate(BaseModel):
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None

class Supplier(SupplierCreate):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ========== SUMMARY MODELS ==========
class DailySummary(BaseModel):
    date: str
    transaction_count: int
    total_sales: float
    total_profit: float

class ProductSummary(BaseModel):
    total_products: int
    active_products: int
    low_stock_count: int
    total_stock_value: float
    total_investment: float  # total modal

# ========== REQUEST/RESPONSE MODELS ==========
class ApiResponse(BaseModel):
    status: str
    message: Optional[str] = None
    data: Optional[Any] = None

class ScanVoiceRequest(BaseModel):
    text: str
    auto_save: bool = True

class ScanVoiceResponse(BaseModel):
    status: str
    transaction_id: Optional[int] = None
    preview: str
    items: List[Dict[str, Any]]
    total: float
    message: str
