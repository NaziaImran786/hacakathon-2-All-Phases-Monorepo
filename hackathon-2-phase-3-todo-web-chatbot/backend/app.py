from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import timedelta
from pydantic import BaseModel

# Internal imports - Make sure these paths match your project
from auth import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from models import Task, User
from src.api.chat import router as chat_router
# Database async helpers (database.py mein banaye hain)
from src.db.database import get_session, init_models

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic: Async table creation
    await init_models()
    yield
    # Shutdown logic (if any) can go here

app = FastAPI(lifespan=lifespan)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(chat_router)

# --- Pydantic Models ---
class UserCreate(BaseModel):
    username: str
    password: str

class SignupResponse(BaseModel):
    message: str

# --- Routes ---

@app.get("/")
async def home():
    return {"status": "Backend is running successfully in Async mode!"}

@app.post("/signup", response_model=SignupResponse)
async def signup(user: UserCreate, session: AsyncSession = Depends(get_session)):
    print(f'Received signup request for: {user.username}')
    
    # Async Query Execution
    statement = select(User).where(User.username == user.username)
    result = await session.execute(statement)
    db_user = result.scalars().first()
    
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    
    session.add(new_user)
    await session.commit()
    # Refresh is now an awaitable call
    await session.refresh(new_user)
    
    return SignupResponse(message="User created successfully")

@app.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    statement = select(User).where(User.username == form_data.username)
    result = await session.execute(statement)
    user = result.scalars().first()
    
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
async def read_users_me(
    current_user: str = Depends(get_current_user), 
    session: AsyncSession = Depends(get_session)
):
    statement = select(User).where(User.username == current_user)
    result = await session.execute(statement)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/api/{user_id}/tasks/", response_model=Task)
async def create_task(
    user_id: int,
    task: Task,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    statement = select(User).where(User.username == current_user)
    result = await session.execute(statement)
    db_user = result.scalars().first()
    
    if not db_user or db_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )

    task.owner_id = user_id
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task

@app.get("/api/{user_id}/tasks/", response_model=List[Task])
async def read_tasks(
    user_id: int,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    statement = select(User).where(User.username == current_user)
    result = await session.execute(statement)
    db_user = result.scalars().first()
    
    if not db_user or db_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    task_statement = select(Task).where(Task.owner_id == user_id)
    task_result = await session.execute(task_statement)
    return task_result.scalars().all()

@app.delete("/api/{user_id}/tasks/{task_id}")
async def delete_task(
    user_id: int,
    task_id: int,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # Authorization check
    user_stmt = select(User).where(User.username == current_user)
    user_res = await session.execute(user_stmt)
    db_user = user_res.scalars().first()
    
    if not db_user or db_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Get task using session.get (which is awaitable in AsyncSession)
    db_task = await session.get(Task, task_id)
    if not db_task or db_task.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    await session.delete(db_task)
    await session.commit()
    return {"message": "Task deleted successfully"}

# Task Update (Description change karne ke liye)
@app.put("/api/{user_id}/tasks/{task_id}", response_model=Task)
async def update_task(
    user_id: int,
    task_id: int,
    task_update: Task,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # Authorization check
    user_stmt = select(User).where(User.username == current_user)
    user_res = await session.execute(user_stmt)
    db_user = user_res.scalars().first()
    
    if not db_user or db_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    db_task = await session.get(Task, task_id)
    if not db_task or db_task.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db_task.title = task_update.title
    db_task.description = task_update.description
    db_task.completed = task_update.completed
    
    session.add(db_task)
    await session.commit()
    await session.refresh(db_task)
    return db_task

# Task Complete/Undo (Status change karne ke liye)
@app.patch("/api/{user_id}/tasks/{task_id}/complete", response_model=Task)
async def complete_task(
    user_id: int,
    task_id: int,
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # Authorization check
    user_stmt = select(User).where(User.username == current_user)
    user_res = await session.execute(user_stmt)
    db_user = user_res.scalars().first()
    
    if not db_user or db_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    db_task = await session.get(Task, task_id)
    if not db_task or db_task.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db_task.completed = not db_task.completed # Toggle status
    session.add(db_task)
    await session.commit()
    await session.refresh(db_task)
    return db_task
