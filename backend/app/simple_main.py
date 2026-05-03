from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
import jwt
from pydantic import BaseModel, EmailStr
from typing import Optional, List

app = FastAPI()

# CORS - Allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "your-super-secret-key-change-this-production-min-32-chars"
ALGORITHM = "HS256"
security = HTTPBearer()

# Store users in memory for testing (replace with database later)
users_db = {}
projects_db = {}
tasks_db = {}
project_counter = 1
task_counter = 1

# ========== Models ==========
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    is_active: bool
    created_at: str

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    owner_id: int
    created_at: str

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    project_id: int
    status: str = "todo"
    priority: str = "medium"
    due_date: Optional[str] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    priority: str
    project_id: int
    created_by: int
    created_at: str

# ========== Helper Functions ==========
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(payload = Depends(verify_token)):
    user_id = payload.get("user_id")
    if user_id not in users_db:
        raise HTTPException(status_code=401, detail="User not found")
    return users_db[user_id]

# ========== Auth Routes ==========
@app.post("/api/v1/auth/signup")
def signup(user: UserCreate):
    # Check if user exists
    for existing_user in users_db.values():
        if existing_user["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")
        if existing_user["username"] == user.username:
            raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create new user
    user_id = len(users_db) + 1
    users_db[user_id] = {
        "id": user_id,
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "password": user.password,  # In real app, hash this!
        "is_active": True,
        "created_at": datetime.now().isoformat()
    }
    
    # Create token
    token = create_access_token({"sub": user.email, "user_id": user_id})
    
    return {
        "access_token": token,
        "refresh_token": token,
        "token_type": "bearer"
    }

@app.post("/api/v1/auth/login")
def login(username: str, password: str):
    # Find user
    user = None
    for u in users_db.values():
        if u["email"] == username or u["username"] == username:
            if u["password"] == password:  # In real app, verify hash!
                user = u
                break
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create token
    token = create_access_token({"sub": user["email"], "user_id": user["id"]})
    
    return {
        "access_token": token,
        "refresh_token": token,
        "token_type": "bearer"
    }

# ========== User Routes ==========
@app.get("/api/v1/users/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "username": current_user["username"],
        "full_name": current_user["full_name"],
        "is_active": current_user["is_active"],
        "created_at": current_user["created_at"]
    }

# ========== Project Routes ==========
@app.get("/api/v1/projects/")
def get_projects(current_user: dict = Depends(get_current_user)):
    user_projects = [p for p in projects_db.values() if p["owner_id"] == current_user["id"]]
    return user_projects

@app.post("/api/v1/projects/")
def create_project(project: ProjectCreate, current_user: dict = Depends(get_current_user)):
    global project_counter
    new_project = {
        "id": project_counter,
        "name": project.name,
        "description": project.description,
        "owner_id": current_user["id"],
        "created_at": datetime.now().isoformat()
    }
    projects_db[project_counter] = new_project
    project_counter += 1
    return new_project

@app.get("/api/v1/projects/{project_id}")
def get_project(project_id: int, current_user: dict = Depends(get_current_user)):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    project = projects_db[project_id]
    if project["owner_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    return project

@app.put("/api/v1/projects/{project_id}")
def update_project(project_id: int, project: ProjectCreate, current_user: dict = Depends(get_current_user)):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    if projects_db[project_id]["owner_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    projects_db[project_id]["name"] = project.name
    projects_db[project_id]["description"] = project.description
    return projects_db[project_id]

@app.delete("/api/v1/projects/{project_id}")
def delete_project(project_id: int, current_user: dict = Depends(get_current_user)):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    if projects_db[project_id]["owner_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    del projects_db[project_id]
    return {"message": "Project deleted"}

# ========== Task Routes ==========
@app.get("/api/v1/tasks/project/{project_id}")
def get_tasks(project_id: int, current_user: dict = Depends(get_current_user)):
    project_tasks = [t for t in tasks_db.values() if t["project_id"] == project_id]
    return project_tasks

@app.post("/api/v1/tasks/")
def create_task(task: TaskCreate, current_user: dict = Depends(get_current_user)):
    global task_counter
    new_task = {
        "id": task_counter,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "project_id": task.project_id,
        "created_by": current_user["id"],
        "created_at": datetime.now().isoformat()
    }
    tasks_db[task_counter] = new_task
    task_counter += 1
    return new_task

@app.put("/api/v1/tasks/{task_id}")
def update_task(task_id: int, task: TaskCreate, current_user: dict = Depends(get_current_user)):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    tasks_db[task_id]["title"] = task.title
    tasks_db[task_id]["description"] = task.description
    tasks_db[task_id]["status"] = task.status
    tasks_db[task_id]["priority"] = task.priority
    return tasks_db[task_id]

@app.delete("/api/v1/tasks/{task_id}")
def delete_task(task_id: int, current_user: dict = Depends(get_current_user)):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    del tasks_db[task_id]
    return {"message": "Task deleted"}

# ========== Health Check ==========
@app.get("/health")
def health():
    return {"status": "healthy", "users": len(users_db), "projects": len(projects_db)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)