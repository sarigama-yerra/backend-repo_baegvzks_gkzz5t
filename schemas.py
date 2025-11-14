"""
Database Schemas for Aham Eva

Each Pydantic model corresponds to a MongoDB collection with the same lowercased
name. These schemas define the data contract for the application.
"""
from pydantic import BaseModel, Field, HttpUrl, EmailStr
from typing import Optional, List
from datetime import date


class ProgramModule(BaseModel):
    day: int = Field(..., ge=1, description="Day number in the program")
    title: str
    summary: Optional[str] = None
    focus: Optional[str] = Field(None, description="Theme or practice focus")


class Program(BaseModel):
    title: str
    slug: str = Field(..., description="URL-friendly identifier")
    tagline: Optional[str] = None
    description: Optional[str] = None
    duration_days: int = Field(..., ge=1)
    price_usd: float = Field(..., ge=0)
    cover_image: Optional[HttpUrl] = None
    modules: List[ProgramModule] = []
    featured: bool = False


class TherapyOffering(BaseModel):
    title: str
    slug: str
    description: Optional[str] = None
    format: str = Field(..., description="e.g., 1:1, group")
    duration_minutes: int = Field(..., ge=15)
    price_usd: float = Field(..., ge=0)


class Product(BaseModel):
    title: str
    slug: str
    description: Optional[str] = None
    price_usd: float = Field(..., ge=0)
    kind: str = Field(..., description="digital_audio | pdf | bundle")
    download_url: Optional[HttpUrl] = None
    cover_image: Optional[HttpUrl] = None


class JournalPost(BaseModel):
    title: str
    slug: str
    excerpt: Optional[str] = None
    content_md: str
    cover_image: Optional[HttpUrl] = None
    published_on: Optional[date] = None


class Booking(BaseModel):
    full_name: str
    email: EmailStr
    therapy_slug: str
    preferred_date: str
    note: Optional[str] = None
    timezone: Optional[str] = None


class ContactMessage(BaseModel):
    full_name: str
    email: EmailStr
    subject: Optional[str] = None
    message: str
