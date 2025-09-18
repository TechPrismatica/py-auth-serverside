from pydantic import BaseModel


class Token(BaseModel):
    user_id: str
    token: str
