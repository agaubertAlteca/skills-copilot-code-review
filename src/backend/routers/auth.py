"""
Authentication endpoints for the High School Management System API
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Dict, Any

from ..authentication import get_current_teacher
from ..database import create_session, revoke_session, teachers_collection, verify_password

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)
bearer_scheme = HTTPBearer(auto_error=False)


@router.post("/login")
def login(username: str, password: str) -> Dict[str, Any]:
    """Login a teacher account"""
    # Find the teacher in the database
    teacher = teachers_collection.find_one({"_id": username})

    # Verify password using Argon2 verifier from database.py
    if not teacher or not verify_password(teacher.get("password", ""), password):
        raise HTTPException(
            status_code=401, detail="Invalid username or password")

    # Return teacher information (excluding password)
    return {
        "username": teacher["username"],
        "display_name": teacher["display_name"],
        "role": teacher["role"],
        "session_token": create_session(teacher["username"]),
    }


@router.get("/check-session")
def check_session(teacher: Dict[str, Any] = Depends(get_current_teacher)) -> Dict[str, Any]:
    """Return the account associated with the authenticated session."""
    return {
        "username": teacher["username"],
        "display_name": teacher["display_name"],
        "role": teacher["role"]
    }


@router.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> Dict[str, str]:
    """Revoke the current session token."""
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    revoke_session(credentials.credentials)
    return {"message": "Logged out"}
