from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone

class User(SQLModel, table=True):
    id:Optional[int]=Field(default=None, primary_key=True)
    username:str=Field(index=True, unique=True)
    email:str
    password:str

class UserCreate(SQLModel):
    username:str
    password:str
    email:str

class UserLogin(SQLModel):
    email: str
    password: str


class UserRead(SQLModel):
    id: int
    username: str
    email: str


class UserUpdate(SQLModel):
    username: Optional[str] = None
    email: Optional[str] = None


class Notes(SQLModel, table=True):
    serial_no:Optional[int]=Field(default=None, primary_key=True)
    text:str
    # notes_user:str=Field(index=True)
    user_id: int = Field(foreign_key="user.id",index=True)
    creation_date:datetime=Field(default_factory=lambda:datetime.now(timezone.utc))

class NotesCreate(SQLModel):
    text:str
    user_id: int
    # notes_user:str=Field(index=True)

class NotesRead(SQLModel):
    serial_no:Optional[int]
    text:str
    # notes_user:str
    user_id: int

    creation_date:datetime

class NotesUpdate(SQLModel):
    text:str

class NotesDelete(SQLModel):
    text:str



