from pydantic import BaseModel
from typing import Optional

class Login(BaseModel):
    usuario:str
    senha:Optional[str]

class SessionModel(BaseModel):
    usuario:str