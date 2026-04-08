from fastapi import APIRouter, HTTPException
from fastapi_derive_responses import AutoDeriveResponsesAPIRoute

from src.api import docs
from src.api.dependencies import USER_AUTH
from src.modules.inh_accounts_sdk import UserSchema, inh_accounts

router = APIRouter(
    prefix="/user",
    tags=["User"],
    route_class=AutoDeriveResponsesAPIRoute,
)
_description = """
User data, registration, login, logout.
"""
docs.TAGS_INFO.append({"description": _description, "name": str(router.tags[0])})


@router.get("/me", responses={200: {"description": "Current user info"}})
async def get_me(auth: USER_AUTH) -> UserSchema:
    """
    Get current user info if authenticated
    """

    user = await inh_accounts.get_user(auth.innohassle_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
