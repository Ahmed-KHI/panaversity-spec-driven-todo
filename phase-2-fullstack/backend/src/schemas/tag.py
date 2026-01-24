"""
Tag schemas for request/response validation.
[Task]: T-A-007 (Phase V Tag Schemas)
[From]: specs/005-phase-v-cloud/phase5-cloud.specify.md §2.4,
        specs/005-phase-v-cloud/phase5-cloud.plan.md §3.1.2
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Optional, Optional


class TagCreate(BaseModel):
    """Create tag request."""
    name: str = Field(..., min_length=1, max_length=50, description="Tag name")
    color: Optional[str] = Field("#3B82F6", pattern="^#[0-9A-Fa-f]{6}$", description="Hex color code")


class TagUpdate(BaseModel):
    """Update tag request."""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="Tag name")
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$", description="Hex color code")


class TagResponse(BaseModel):
    """Tag response."""
    id: int
    name: str
    color: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class TagListResponse(BaseModel):
    """List of tags response."""
    tags: List[TagResponse]
    count: int
