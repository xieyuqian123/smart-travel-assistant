"""Schemas for the travel assistant."""

from typing import List, Optional
from pydantic import BaseModel, Field



class CoordinateSchema(BaseModel):
    """Schema for geographical coordinates."""
    
    lat: float = Field(..., description="Latitude")
    lng: float = Field(..., description="Longitude")
    address: Optional[str] = Field(None, description="Human-readable address")


class TripNodeSchema(BaseModel):
    """Schema for a specific activity or stop in the itinerary."""
    
    name: str = Field(..., description="Name of the activity or place")
    description: str = Field(..., description="Description of the activity")
    start_time: Optional[str] = Field(None, description="Start time in HH:MM format")
    end_time: Optional[str] = Field(None, description="End time in HH:MM format")
    coordinates: Optional[CoordinateSchema] = Field(None, description="Location coordinates")
    cost: Optional[str] = Field(None, description="Estimated cost or ticket price")
    type: Optional[str] = Field(None, description="Type of node, e.g., 'attraction', 'restaurant', 'transport'")


class DailyItinerarySchema(BaseModel):
    """Schema for a single day's itinerary."""
    
    day: int = Field(..., description="Day number of the trip")
    date: Optional[str] = Field(None, description="Date in YYYY-MM-DD format")
    summary: str = Field(..., description="Brief summary of the day's plan")
    nodes: List[TripNodeSchema] = Field(default_factory=list, description="List of activities for the day")


class NoteSchema(BaseModel):
    """Schema for important travel notes."""
    
    category: str = Field(..., description="Category of the note, e.g., 'weather', 'visa', 'safety'")
    content: str = Field(..., description="Content of the note")


class TripSchema(BaseModel):
    """Schema representing the details of a trip."""

    destination: str = Field(..., description="The primary destination for the trip")
    start_date: Optional[str] = Field(None, description="Start date of the trip in YYYY-MM-DD format")
    end_date: Optional[str] = Field(None, description="End date of the trip in YYYY-MM-DD format")
    budget: Optional[str] = Field(None, description="Approximate budget for the trip")
    interests: List[str] = Field(default_factory=list, description="List of user interests or activities")
    travelers: int = Field(default=1, description="Number of travelers")
    
    itinerary: List[DailyItinerarySchema] = Field(default_factory=list, description="Daily itinerary details")
    notes: List[NoteSchema] = Field(default_factory=list, description="Important travel notes")
