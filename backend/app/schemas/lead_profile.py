"""Pydantic schemas for enriched lead profile data."""
from pydantic import Field
from typing import List, Optional

from .base import BaseSchema
from .enriched_data import ProfileSchema, ProductSchema, PainPointsSchema, CommunicationSchema

# --- 1. Nested Models for Person Data ---
class ExperienceView(BaseSchema):
    title: str = Field(description="Job title held at the company")
    company: str = Field(description="Name of the employer")
    start_date: Optional[str] = Field(None, description="Start date of the role (YYYY-MM-DD)")
    end_date: Optional[str] = Field("Present", description="End date of the role, or 'Present' if current")
    is_current: bool = Field(description="Indicates whether the role is ongoing")

class EducationView(BaseSchema):
    school_name: str = Field(description="Name of the educational institution")
    degree: Optional[str] = Field(None, description="Degree or certification obtained")

class LanguageView(BaseSchema):
    language: str = Field(description="Language name (e.g., Spanish, English)")
    proficiency: Optional[str] = Field(None, description="Self-reported proficiency level")

# --- 2. Nested Models for Company Data ---
class CompanyView(BaseSchema):
    name: str = Field(description="Company legal name")
    domain: Optional[str] = Field(None, description="Primary website domain")
    industry: str = Field(description="Industry classification (e.g., Food and Beverage)")
    size: str = Field(description="Employee count range (e.g., '10,001+ employees')")
    revenue: Optional[str] = Field(None, description="Annual revenue range (e.g., '10B-100B')")
    headquarters: str = Field(description="City and country of headquarters")
    description: str = Field(description="Company description or overview")
    specialties: List[str] = Field(default_factory=list, description="List of company specialties")
    business_tags: List[str] = Field(default_factory=list, description="Derived business tags (e.g., B2C, CPG, Sustainability)")

# --- 3. The Main View Model for the Frontend ---
class LeadProfileView(BaseSchema):
    # Person Identity
    name: str = Field(description="Full name of the lead")
    current_title: str = Field(description="Current job title")
    location: str = Field(description="Geographic location (city, country)")
    linkedin_url: Optional[str] = Field(None, description="URL to LinkedIn profile")
    headline: Optional[str] = Field(None, description="Professional headline from profile")
    summary: Optional[str] = Field(None, description="Profile summary or bio")
    
    # Nested Arrays (Sliced in transformer)
    recent_experience: List[ExperienceView] = Field(default_factory=list, description="Most recent work experiences")
    education: List[EducationView] = Field(default_factory=list, description="Educational background")
    languages: List[LanguageView] = Field(default_factory=list, description="Languages spoken")
    
    # Nested Objects
    company: Optional[CompanyView] = Field(None, description="Current company details")
    
    # Full Intelligence Schemas
    profile: Optional[ProfileSchema] = Field(None, description="Role intelligence")
    products: List[ProductSchema] = Field(default_factory=list, description="Product intelligence")
    pain_points: Optional[PainPointsSchema] = Field(None, description="Pain points analysis")
    outreach: Optional[CommunicationSchema] = Field(None, description="Outreach strategy")