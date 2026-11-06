from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from contextlib import asynccontextmanager
from database import create_tables, get_session
# from auth import verify_api_key
from auth import get_current_user
# from models import Notes, NotesCreate, NotesRead, NotesUpdate
from models import (
    User, UserCreate, UserLogin, UserRead,
    Notes, NotesCreate, NotesRead, NotesUpdate
)

from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)

@asynccontextmanager
async def lifespan(app:FastAPI):
	print("lifespan started.........")
	create_tables()
	print("database table created successfully........")
	yield

app = FastAPI(title="notes taking app", description="an api for notes taking", lifespan=lifespan)

@app.get("/")
def root():
	return {"welcome":"welcome to notes taking application"}

# @app.post("/notes", response_model=NotesRead)
# def create_notes(note:NotesCreate, session:Session=Depends(get_session), api_key:str=Depends(verify_api_key)):
# 	new_note = Notes(**note.model_dump())
# 	session.add(new_note)
# 	session.commit()
# 	session.refresh(new_note)
# 	return new_note

@app.post("/notes", response_model=NotesRead)
def create_notes( note: NotesCreate,session: Session = Depends(get_session),current_user: User = Depends(get_current_user)):
    new_note = Notes(text=note.text,user_id=current_user.id)
    session.add(new_note)
    session.commit()
    session.refresh(new_note)
    return new_note

@app.get("/notes", response_model=list[NotesRead])
def get_notes(session: Session = Depends(get_session),current_user: User = Depends(get_current_user)):
    statement = select(Notes).where(Notes.user_id == current_user.id)
    notes = session.exec(statement).all()
    return notes

@app.get("/notes/{note_id}", response_model=NotesRead)
def get_notes_by_id(note_id: int,session: Session = Depends(get_session),current_user: User = Depends(get_current_user)):
    statement = select(Notes).where(Notes.serial_no == note_id,Notes.user_id == current_user.id)
    note = session.exec(statement).first()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    return note

# @app.post("/notes", response_model=NotesRead)
# def create_notes(note: NotesCreate,session: Session = Depends(get_session)):
#     new_note = Notes(**note.model_dump())
#     session.add(new_note)
#     session.commit()
#     session.refresh(new_note)
#     return new_note

# @app.get("/notes", response_model=list[NotesRead])
# def get_notes(session:Session=Depends(get_session)):
# 	statement = select(Notes)
# 	notes = session.exec(statement).all()
# 	return notes

# @app.get("/users/{user_id}/notes", response_model=list[NotesRead])
# def get_notes(user_id: int,session: Session = Depends(get_session)):
#     statement = select(Notes).where(Notes.user_id == user_id)
#     notes = session.exec(statement).all()
#     return notes

# @app.get("/notes/{note_id}", response_model=NotesRead)
# def get_notes_by_id(note_id:int, session:Session=Depends(get_session)):
# 	all_notes = session.exec(select(Notes)).all()
# 	# Notes.get_one(note_id)
# 	for note in all_notes:
# 		if note.serial_no == note_id:
# 			return note

@app.patch("/notes/{note_id}", response_model=NotesRead)
def update_note(note_id: int,text: str,session: Session = Depends(get_session),current_user: User = Depends(get_current_user)):
    statement = select(Notes).where(Notes.serial_no == note_id,Notes.user_id == current_user.id)
    note = session.exec(statement).first()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    note.text = text
    session.add(note)
    session.commit()
    session.refresh(note)
    return note

@app.delete("/notes/{note_id}")
def delete_note(note_id: int,session: Session = Depends(get_session),current_user: User = Depends(get_current_user)):
    statement = select(Notes).where(Notes.serial_no == note_id,Notes.user_id == current_user.id)
    note = session.exec(statement).first()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    session.delete(note)
    session.commit()

    return {"message": "Note deleted successfully"}

# @app.patch("/notes/{note_id}", response_model=NotesUpdate)
# def update_note(note_id:int, text:str, session:Session=Depends(get_session)):
# 	all_notes = session.exec(select(Notes)).all()
# 	for note in all_notes:
# 		if note.serial_no == note_id:
# 			note.text = text
# 			session.add(note)
# 			session.commit()
# 			session.refresh(note)
# 			return note

# @app.delete("/notes/{note_id}")
# def delete_note(note_id:int, session:Session=Depends(get_session)):
# 	all_notes = session.exec(select(Notes)).all()
# 	# del_note = [note for note in all_notes if note.serial_no == note_id]
# 	for note in all_notes:
# 		print("FFFFFFFFFFFFFFFFFFf")
# 		if note.serial_no == note_id:
# 			print(note)
# 			# import pdb;pdb.set_trace()
# 			session.delete(note)
# 			session.commit()
# 			session.refresh(note)


@app.post("/login")
def login_user(user: UserLogin,session: Session = Depends(get_session)):
    statement = select(User).where(User.email == user.email)
    existing_user = session.exec(statement).first()

    if not existing_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(user.password, existing_user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(existing_user.id)})

    return {"access_token": token,"token_type": "bearer"}


