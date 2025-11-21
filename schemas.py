"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

# Existing example schemas (kept for reference)

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Clean energy specific schemas used by the site

class EnergyProduct(BaseModel):
    """
    Clean energy product/service
    Collection name: "energyproduct"
    """
    name: str = Field(..., description="Product or service name")
    sector: str = Field(..., description="Sector: solar, wind, storage, electrification, hydrogen")
    summary: str = Field(..., description="Short summary of benefits")
    specs: Optional[List[str]] = Field(default=None, description="Key specifications list")
    image: Optional[str] = Field(default=None, description="Image URL")
    featured: bool = Field(default=False, description="Show prominently in portfolio")

class ImpactStory(BaseModel):
    """
    Case study / news item
    Collection name: "impactstory"
    """
    title: str
    location: Optional[str] = None
    sector: Optional[str] = None
    summary: str
    media_url: Optional[str] = None
    partner: Optional[str] = None

class Office(BaseModel):
    """
    Office locations for global reach
    Collection name: "office"
    """
    region: str
    city: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

class Inquiry(BaseModel):
    """
    Contact and inquiry submissions
    Collection name: "inquiry"
    """
    name: str
    email: EmailStr
    company: Optional[str] = None
    topic: str = Field(..., description="General Inquiry, Partnerships, Careers, Support")
    message: str
    consent: bool = Field(default=False, description="GDPR consent for storing contact info")
