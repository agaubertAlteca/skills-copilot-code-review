"""Public announcement display and authenticated announcement management."""

from datetime import date
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field, validator

from ..authentication import get_current_teacher
from ..database import announcements_collection

router = APIRouter(prefix="/announcements", tags=["announcements"])


class AnnouncementInput(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    start_date: Optional[date] = None
    expiration_date: date

    @validator("message")
    def message_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Announcement message cannot be blank")
        return value


def serialize_announcement(document: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": document["_id"],
        "message": document["message"],
        "start_date": document.get("start_date"),
        "expiration_date": document["expiration_date"],
    }


def validate_date_range(announcement: AnnouncementInput) -> None:
    if announcement.start_date and announcement.start_date > announcement.expiration_date:
        raise HTTPException(
            status_code=422,
            detail="Start date must be on or before the expiration date",
        )


def announcement_fields(announcement: AnnouncementInput) -> Dict[str, Any]:
    return {
        "message": announcement.message,
        "start_date": announcement.start_date.isoformat() if announcement.start_date else None,
        "expiration_date": announcement.expiration_date.isoformat(),
    }


@router.get("", response_model=List[Dict[str, Any]])
def get_active_announcements() -> List[Dict[str, Any]]:
    """Return announcements currently within their optional start and required expiry dates."""
    today = date.today().isoformat()
    documents = announcements_collection.find({
        "expiration_date": {"$gte": today},
        "$or": [
            {"start_date": {"$lte": today}},
            {"start_date": None},
        ],
    }).sort([("expiration_date", 1), ("_id", 1)])
    return [serialize_announcement(document) for document in documents]


@router.get("/manage", response_model=List[Dict[str, Any]])
def list_announcements(
    _teacher: Dict[str, Any] = Depends(get_current_teacher),
) -> List[Dict[str, Any]]:
    """Return all announcements, including scheduled and expired ones."""
    documents = announcements_collection.find().sort(
        [("expiration_date", 1), ("_id", 1)]
    )
    return [serialize_announcement(document) for document in documents]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_announcement(
    announcement: AnnouncementInput,
    teacher: Dict[str, Any] = Depends(get_current_teacher),
) -> Dict[str, Any]:
    """Create an announcement. Requires an authenticated teacher session."""
    validate_date_range(announcement)
    document = {
        "_id": uuid4().hex,
        **announcement_fields(announcement),
        "created_by": teacher["username"],
    }
    announcements_collection.insert_one(document)
    return serialize_announcement(document)


@router.put("/{announcement_id}")
def update_announcement(
    announcement_id: str,
    announcement: AnnouncementInput,
    _teacher: Dict[str, Any] = Depends(get_current_teacher),
) -> Dict[str, Any]:
    """Replace an announcement. Requires an authenticated teacher session."""
    validate_date_range(announcement)
    result = announcements_collection.update_one(
        {"_id": announcement_id},
        {"$set": announcement_fields(announcement)},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")
    document = announcements_collection.find_one({"_id": announcement_id})
    return serialize_announcement(document)


@router.delete("/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_announcement(
    announcement_id: str,
    _teacher: Dict[str, Any] = Depends(get_current_teacher),
) -> Response:
    """Delete an announcement. Requires an authenticated teacher session."""
    result = announcements_collection.delete_one({"_id": announcement_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)