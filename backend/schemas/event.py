from typing import Annotated, Optional, Literal
from pydantic import BaseModel, Field, HttpUrl, ConfigDict, model_validator
from datetime import date, time, datetime
# from UUID import UUID

# reusable custom types
TitleStr = Annotated[str, Field(min_length=3, max_length=150, strip_whitespace=True)]
VenueStr = Annotated[str, Field(min_length=2, max_length=200, strip_whitespace=True)]
# centralized event lifecycle states
EventStatus = Literal['scheduled', 'ongoing', 'completed', 'closed', 'cancelled']

# event schemas
class EventBase(BaseModel):
    title: TitleStr
    venue: VenueStr
    event_date: date
    event_time: time
    description: Annotated[Optional[str], Field(default=None, max_length=2000, strip_whitespace=True)]

class EventCreate(EventBase):
    quiz_types: list[str] = Field(default_factory=list)
    sequences: list[int] = Field(default_factory=list)

class EventUpdate(BaseModel):
    # PATCH schema: every field is optional for partial updates
    title: Optional[TitleStr] = None
    venue: Optional[VenueStr] = None
    event_date: Optional[date] = None
    event_time: Optional[time] = None
    description: Annotated[Optional[str], Field(default=None, max_length=2000, strip_whitespace=True)]
    status: Optional[EventStatus] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Annotated[Optional[str], Field(default=None, max_length=1000, strip_whitespace=True)]

    # cross-field validation prevents invalid DB states where an event is cancelled but has no timestamp
    @model_validator(mode='after')
    def check_cancellation_logic(self) -> 'EventUpdate':
        if self.status == 'cancelled':
            if not self.cancelled_at or not self.cancellation_reason:
                raise ValueError("Both 'cancelled_at' and 'cancellation_reason' must be provided when cancelling an event.")
        return self

class EventCancelSchema(BaseModel):
    cancellation_reason: Annotated[Optional[str], Field(default=None, max_length=1000, strip_whitespace=True)]

class EventOut(EventBase):
    id: str
    admin_id: str
    status: EventStatus
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# event rsvp schemas
class EventRSVPCreate(BaseModel):
    event_id: str

class EventRSVPOut(EventRSVPCreate):
    id: str
    student_id: str
    rsvped_at: datetime

    model_config = ConfigDict(from_attributes=True)

# event report schemas
class EventReportCreate(BaseModel):
    event_id: str
    report_content: Annotated[Optional[str], Field(default=None, max_length=5000, strip_whitespace=True)]
    file_url: Optional[HttpUrl] = None

class EventReportOut(BaseModel):
    id: str
    event_id: str
    report_content: Optional[str] = None
    file_url: Optional[str] = None
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)