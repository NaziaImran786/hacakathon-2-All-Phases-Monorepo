from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from datetime import timedelta

from auth import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from models import Task, User, create_db_and_tables, engine
from src.api.chat import router as chat_router
# Import Phase III models for table creation (excluding Task to avoid registry collision)
from src.models import Conversation, Message


app = FastAPI()

# Include chat router
app.include_router(chat_router)

# CORS Configuration - explicitly allow frontend origin
# This fixes CORS blocks for Phase III chatbot integration
origins = [
    "https://hacakathon-2-all-phases-uock.vercel.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers including Authorization
    expose_headers=["*"],
    max_age=600,  # Cache preflight requests for 10 minutes
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


def get_session():
    with Session(engine) as session:
        yield session


from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class SignupResponse(BaseModel):
    """Response model for signup - returns success message only."""
    message: str

@app.post("/signup", response_model=SignupResponse)
def signup(user: UserCreate, session: Session = Depends(get_session)):
    """
    Register a new user.
    Follows stateless architecture - opens fresh session, commits, closes.
    Does NOT return token; user must explicitly login after signup.
    """
    print(f'Received signup request for: {user.username}')
    db_user = session.exec(select(User).where(User.username == user.username)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    # Return success message only - no token. User must login separately.
    return SignupResponse(message="User created successfully")



@app.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/me", response_model=User)
async def read_users_me(current_user: str = Depends(get_current_user), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == current_user)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/api/{user_id}/tasks/", response_model=Task)
def create_task(
    user_id: int,
    task: Task,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    # In a real app, current_user would be an object with an ID,
    # and we'd verify user_id against current_user.id
    # For now, we'll assume current_user.username is sufficient for demonstration
    # and user_id is passed correctly.

    # Strict Constraint: Ensure user_id from path matches the authenticated user's ID
    # This requires looking up the user from the database using current_user (username)
    # to get their ID. For now, we'll use a placeholder logic.
    db_user = session.exec(select(User).where(User.username == current_user)).first()
    if not db_user or db_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create tasks for this user"
        )

    task.owner_id = user_id
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@app.get("/api/{user_id}/tasks/", response_model=List[Task])
def read_tasks(
    user_id: int,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    # Strict Constraint: Ensure user_id from path matches the authenticated user's ID
    db_user = session.exec(select(User).where(User.username == current_user)).first()
    if not db_user or db_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view tasks for this user"
        )

    tasks = session.exec(select(Task).where(Task.owner_id == user_id)).all()
    return tasks


@app.put("/api/{user_id}/tasks/{task_id}", response_model=Task)
def update_task(
    user_id: int,
    task_id: int,
    task: Task,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    # Strict Constraint: Ensure user_id from path matches the authenticated user's ID
    db_user = session.exec(select(User).where(User.username == current_user)).first()
    if not db_user or db_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update tasks for this user"
        )

    db_task = session.get(Task, task_id)
    if not db_task or db_task.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found or not owned by user")

    db_task.title = task.title
    db_task.description = task.description
    db_task.completed = task.completed
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task


@app.delete("/api/{user_id}/tasks/{task_id}")
def delete_task(
    user_id: int,
    task_id: int,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    # Strict Constraint: Ensure user_id from path matches the authenticated user's ID
    db_user = session.exec(select(User).where(User.username == current_user)).first()
    if not db_user or db_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete tasks for this user"
        )

    db_task = session.get(Task, task_id)
    if not db_task or db_task.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found or not owned by user")

    session.delete(db_task)
    session.commit()
    return {"message": "Task deleted successfully"}


@app.patch("/api/{user_id}/tasks/{task_id}/complete", response_model=Task)
def toggle_task_completion(
    user_id: int,
    task_id: int,
    current_user: str = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    # Strict Constraint: Ensure user_id from path matches the authenticated user's ID
    db_user = session.exec(select(User).where(User.username == current_user)).first()
    if not db_user or db_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify tasks for this user"
        )

    db_task = session.get(Task, task_id)
    if not db_task or db_task.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found or not owned by user")

    db_task.completed = not db_task.completed
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task