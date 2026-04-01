from beanie import PydanticObjectId

from src.modules.inh_accounts_sdk import UserTokenData
from src.pydantic_base import BaseSchema


class CreateUser(BaseSchema):
    innohassle_id: str


class ViewUser(BaseSchema):
    id: PydanticObjectId
    innohassle_id: str


class UserAuthData(BaseSchema):
    user_id: PydanticObjectId | None
    user_token_data: UserTokenData
