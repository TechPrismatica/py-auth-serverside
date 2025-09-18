from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserInfoSchema(BaseModel):
    model_config = ConfigDict(extra="allow")
    username: str = None
    email: Optional[str] = None
    user_id: str
    scopes: Optional[list[str]] = None
