from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel, EmailStr

app = FastAPI(title="Team Task Manager API", version="1.0.0")

# CORS - Allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== In-memory Storage ==========
users_db: Dict[int, dict] = {}
projects_db: Dict[int, dict] = {}
tasks_db: Dict[int, dict] = {}
team_members_db: Dict[int, dict] = {}
sessions_db: Dict[str, int] = {}  # token -> user_id

user_counter = 1
project_counter = 1
task_counter = 1
team_member_counter = 1

# ========== Helper Functions ==========
def is_overdue(due_date_str: Optional[str]) -> bool:
    """Check if a due date is overdue"""
    if not due_date_str:
        return False
    try:
        due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
        return due_date < datetime.now()
    except:
        return False

# ========== Pydantic Models ==========
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

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

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
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

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None
    assignee_id: Optional[int] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    priority: str
    project_id: int
    created_by: int
    assignee_id: Optional[int] = None
    due_date: Optional[str] = None
    created_at: str
    is_overdue: bool = False

class TeamMemberCreate(BaseModel):
    user_id: int
    role: str = "member"

class TeamMemberResponse(BaseModel):
    id: int
    project_id: int
    user_id: int
    role: str
    full_name: str
    email: str
    username: str

# ========== Helper Functions ==========
def get_user_from_token(authorization: Optional[str] = Header(None)):
    """Extract user from authorization token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="No token provided")
    
    token = authorization.replace("Bearer ", "")
    if token not in sessions_db:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = sessions_db[token]
    if user_id not in users_db:
        raise HTTPException(status_code=401, detail="User not found")
    
    return users_db[user_id]

def is_project_member(project_id: int, user_id: int) -> bool:
    """Check if user is a member of the project"""
    # Check if user is owner
    project = projects_db.get(project_id)
    if project and project["owner_id"] == user_id:
        return True
    
    # Check team members
    for member in team_members_db.values():
        if member["project_id"] == project_id and member["user_id"] == user_id:
            return True
    return False

def is_project_admin(project_id: int, user_id: int) -> bool:
    """Check if user is admin of the project"""
    project = projects_db.get(project_id)
    if project and project["owner_id"] == user_id:
        return True
    for member in team_members_db.values():
        if member["project_id"] == project_id and member["user_id"] == user_id and member["role"] == "admin":
            return True
    return False

# ========== Auth Routes ==========
@app.post("/api/v1/auth/signup")
def signup(user: UserCreate):
    global user_counter
    
    # Check if user exists
    for existing_user in users_db.values():
        if existing_user["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")
        if existing_user["username"] == user.username:
            raise HTTPException(status_code=400, detail="Username already taken")
    
    # Create new user
    user_id = user_counter
    users_db[user_id] = {
        "id": user_id,
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "password": user.password,
        "is_active": True,
        "avatar_url": None,
        "created_at": datetime.now().isoformat()
    }
    user_counter += 1
    
    # Create session token
    token = f"token_{user_id}_{datetime.now().timestamp()}"
    sessions_db[token] = user_id
    
    return {
        "access_token": token,
        "refresh_token": token,
        "token_type": "bearer"
    }

@app.post("/api/v1/auth/login")
def login(username: str, password: str):
    # Find user by email or username
    user = None
    for u in users_db.values():
        if u["email"] == username or u["username"] == username:
            if u["password"] == password:
                user = u
                break
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user["is_active"]:
        raise HTTPException(status_code=401, detail="Account is deactivated")
    
    # Create session token
    token = f"token_{user['id']}_{datetime.now().timestamp()}"
    sessions_db[token] = user["id"]
    
    return {
        "access_token": token,
        "refresh_token": token,
        "token_type": "bearer"
    }

@app.post("/api/v1/auth/logout")
def logout(authorization: Optional[str] = Header(None)):
    if authorization:
        token = authorization.replace("Bearer ", "")
        if token in sessions_db:
            del sessions_db[token]
    return {"message": "Logged out successfully"}

# ========== User Routes ==========
@app.get("/api/v1/users/me")
def get_current_user(current_user: dict = Depends(get_user_from_token)):
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "username": current_user["username"],
        "full_name": current_user["full_name"],
        "is_active": current_user["is_active"],
        "avatar_url": current_user.get("avatar_url"),
        "created_at": current_user["created_at"]
    }

@app.put("/api/v1/users/me")
def update_current_user(
    user_update: UserUpdate,
    current_user: dict = Depends(get_user_from_token)
):
    if user_update.full_name:
        current_user["full_name"] = user_update.full_name
    if user_update.avatar_url:
        current_user["avatar_url"] = user_update.avatar_url
    
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "username": current_user["username"],
        "full_name": current_user["full_name"],
        "is_active": current_user["is_active"],
        "avatar_url": current_user.get("avatar_url"),
        "created_at": current_user["created_at"]
    }

@app.get("/api/v1/users/search")
def search_users(
    q: str,
    current_user: dict = Depends(get_user_from_token)
):
    """Search for users by email or username"""
    results = []
    q_lower = q.lower()
    
    for user in users_db.values():
        if user["id"] == current_user["id"]:
            continue
        if q_lower in user["email"].lower() or q_lower in user["username"].lower():
            results.append({
                "id": user["id"],
                "email": user["email"],
                "username": user["username"],
                "full_name": user["full_name"],
                "avatar_url": user.get("avatar_url")
            })
    
    return results[:10]

# ========== Project Routes ==========
@app.get("/api/v1/projects/")
def get_projects(current_user: dict = Depends(get_user_from_token)):
    """Get all projects where user is owner or member"""
    user_projects = []
    project_ids = set()
    
    # Projects where user is owner
    for p in projects_db.values():
        if p["owner_id"] == current_user["id"]:
            if p["id"] not in project_ids:
                user_projects.append(p)
                project_ids.add(p["id"])
    
    # Projects where user is team member
    for member in team_members_db.values():
        if member["user_id"] == current_user["id"]:
            project = projects_db.get(member["project_id"])
            if project and project["id"] not in project_ids:
                user_projects.append(project)
                project_ids.add(project["id"])
    
    return user_projects

@app.post("/api/v1/projects/")
def create_project(
    project: ProjectCreate,
    current_user: dict = Depends(get_user_from_token)
):
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
def get_project(
    project_id: int,
    current_user: dict = Depends(get_user_from_token)
):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    
    # Check if user has access
    if not is_project_member(project_id, current_user["id"]):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get task counts
    project_tasks = [t for t in tasks_db.values() if t["project_id"] == project_id]
    total_tasks = len(project_tasks)
    completed_tasks = len([t for t in project_tasks if t["status"] == "done"])
    overdue_tasks = len([t for t in project_tasks if is_overdue(t.get("due_date")) and t["status"] != "done"])
    
    return {
        "id": project["id"],
        "name": project["name"],
        "description": project["description"],
        "owner_id": project["owner_id"],
        "created_at": project["created_at"],
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "overdue_tasks": overdue_tasks,
        "total_members": len([m for m in team_members_db.values() if m["project_id"] == project_id]) + 1
    }

@app.put("/api/v1/projects/{project_id}")
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    current_user: dict = Depends(get_user_from_token)
):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    
    # Check if user is owner or admin
    if not is_project_admin(project_id, current_user["id"]):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if project_update.name:
        project["name"] = project_update.name
    if project_update.description is not None:
        project["description"] = project_update.description
    
    return project

@app.delete("/api/v1/projects/{project_id}")
def delete_project(
    project_id: int,
    current_user: dict = Depends(get_user_from_token)
):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects_db[project_id]
    
    # Only owner can delete
    if project["owner_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Only project owner can delete")
    
    # Delete all tasks in project
    task_ids_to_delete = [t_id for t_id, t in tasks_db.items() if t["project_id"] == project_id]
    for t_id in task_ids_to_delete:
        del tasks_db[t_id]
    
    # Delete all team members
    member_ids_to_delete = [m_id for m_id, m in team_members_db.items() if m["project_id"] == project_id]
    for m_id in member_ids_to_delete:
        del team_members_db[m_id]
    
    # Delete project
    del projects_db[project_id]
    
    return {"message": "Project deleted successfully"}

# ========== Team Member Routes ==========
@app.get("/api/v1/projects/{project_id}/members")
def get_project_members(
    project_id: int,
    current_user: dict = Depends(get_user_from_token)
):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check access
    if not is_project_member(project_id, current_user["id"]):
        raise HTTPException(status_code=403, detail="Access denied")
    
    members = []
    
    # Add owner
    owner = users_db.get(projects_db[project_id]["owner_id"])
    if owner:
        members.append({
            "id": 0,
            "project_id": project_id,
            "user_id": owner["id"],
            "role": "owner",
            "full_name": owner["full_name"],
            "email": owner["email"],
            "username": owner["username"]
        })
    
    # Add team members
    for member in team_members_db.values():
        if member["project_id"] == project_id:
            user = users_db.get(member["user_id"])
            if user:
                members.append({
                    "id": member["id"],
                    "project_id": project_id,
                    "user_id": user["id"],
                    "role": member["role"],
                    "full_name": user["full_name"],
                    "email": user["email"],
                    "username": user["username"]
                })
    
    return members

@app.post("/api/v1/projects/{project_id}/members/{user_id}")
def add_team_member(
    project_id: int,
    user_id: int,
    role: str = "member",
    current_user: dict = Depends(get_user_from_token)
):
    global team_member_counter
    
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if current user is owner or admin
    if not is_project_admin(project_id, current_user["id"]):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check if user exists
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already a member
    for member in team_members_db.values():
        if member["project_id"] == project_id and member["user_id"] == user_id:
            raise HTTPException(status_code=400, detail="User already in project")
    
    # Add member
    new_member = {
        "id": team_member_counter,
        "project_id": project_id,
        "user_id": user_id,
        "role": role
    }
    team_members_db[team_member_counter] = new_member
    team_member_counter += 1
    
    return {"message": "Member added successfully"}

@app.delete("/api/v1/projects/{project_id}/members/{user_id}")
def remove_team_member(
    project_id: int,
    user_id: int,
    current_user: dict = Depends(get_user_from_token)
):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if current user is owner or admin
    if not is_project_admin(project_id, current_user["id"]):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Cannot remove owner
    if projects_db[project_id]["owner_id"] == user_id:
        raise HTTPException(status_code=400, detail="Cannot remove project owner")
    
    # Find and remove member
    member_id_to_delete = None
    for m_id, member in team_members_db.items():
        if member["project_id"] == project_id and member["user_id"] == user_id:
            member_id_to_delete = m_id
            break
    
    if member_id_to_delete:
        del team_members_db[member_id_to_delete]
        return {"message": "Member removed successfully"}
    
    raise HTTPException(status_code=404, detail="Member not found")

# ========== Task Routes ==========
@app.get("/api/v1/tasks/project/{project_id}")
def get_tasks(
    project_id: int,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee_id: Optional[int] = None,
    current_user: dict = Depends(get_user_from_token)
):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check access
    if not is_project_member(project_id, current_user["id"]):
        raise HTTPException(status_code=403, detail="Access denied")
    
    tasks = []
    for task in tasks_db.values():
        if task["project_id"] == project_id:
            if status and task["status"] != status:
                continue
            if priority and task["priority"] != priority:
                continue
            if assignee_id and task.get("assignee_id") != assignee_id:
                continue
            # Add is_overdue field
            task_copy = task.copy()
            task_copy["is_overdue"] = is_overdue(task.get("due_date")) and task["status"] != "done"
            tasks.append(task_copy)
    
    return tasks

@app.post("/api/v1/tasks/")
def create_task(
    task: TaskCreate,
    current_user: dict = Depends(get_user_from_token)
):
    global task_counter
    
    if task.project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check access
    if not is_project_member(task.project_id, current_user["id"]):
        raise HTTPException(status_code=403, detail="Access denied")
    
    new_task = {
        "id": task_counter,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "project_id": task.project_id,
        "created_by": current_user["id"],
        "assignee_id": None,
        "due_date": task.due_date,
        "created_at": datetime.now().isoformat(),
        "is_overdue": is_overdue(task.due_date) and task.status != "done"
    }
    tasks_db[task_counter] = new_task
    task_counter += 1
    
    return new_task

@app.get("/api/v1/tasks/{task_id}")
def get_task(
    task_id: int,
    current_user: dict = Depends(get_user_from_token)
):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id].copy()
    project = projects_db.get(task["project_id"])
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not is_project_member(task["project_id"], current_user["id"]):
        raise HTTPException(status_code=403, detail="Access denied")
    
    task["is_overdue"] = is_overdue(task.get("due_date")) and task["status"] != "done"
    return task

@app.put("/api/v1/tasks/{task_id}")
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: dict = Depends(get_user_from_token)
):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    project = projects_db.get(task["project_id"])
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not is_project_member(task["project_id"], current_user["id"]):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if task_update.title is not None:
        task["title"] = task_update.title
    if task_update.description is not None:
        task["description"] = task_update.description
    if task_update.status is not None:
        task["status"] = task_update.status
    if task_update.priority is not None:
        task["priority"] = task_update.priority
    if task_update.due_date is not None:
        task["due_date"] = task_update.due_date
    if task_update.assignee_id is not None:
        task["assignee_id"] = task_update.assignee_id
    
    return task

@app.delete("/api/v1/tasks/{task_id}")
def delete_task(
    task_id: int,
    current_user: dict = Depends(get_user_from_token)
):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    project = projects_db.get(task["project_id"])
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Allow owner, task creator, or admin to delete
    if not (project["owner_id"] == current_user["id"] or 
            task["created_by"] == current_user["id"] or 
            is_project_admin(task["project_id"], current_user["id"])):
        raise HTTPException(status_code=403, detail="Not authorized to delete this task")
    
    del tasks_db[task_id]
    return {"message": "Task deleted successfully"}

@app.post("/api/v1/tasks/{task_id}/assign/{user_id}")
def assign_task(
    task_id: int,
    user_id: int,
    current_user: dict = Depends(get_user_from_token)
):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    project = projects_db.get(task["project_id"])
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not is_project_admin(task["project_id"], current_user["id"]):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user is project member
    if not is_project_member(task["project_id"], user_id):
        raise HTTPException(status_code=400, detail="User must be a project member")
    
    task["assignee_id"] = user_id
    return {"message": "Task assigned successfully"}

# ========== Dashboard Routes ==========
@app.get("/api/v1/tasks/dashboard/overdue")
def get_overdue_tasks(current_user: dict = Depends(get_user_from_token)):
    """Get all overdue tasks for current user"""
    overdue_tasks = []
    
    for task in tasks_db.values():
        # Check if task is visible to user
        project = projects_db.get(task["project_id"])
        if project and (task.get("assignee_id") == current_user["id"] or 
                        project["owner_id"] == current_user["id"] or
                        is_project_member(task["project_id"], current_user["id"])):
            if is_overdue(task.get("due_date")) and task["status"] != "done":
                task_copy = task.copy()
                task_copy["is_overdue"] = True
                overdue_tasks.append(task_copy)
    
    return overdue_tasks

# ========== Health Check Routes ==========
@app.get("/")
def root():
    return {"message": "Team Task Manager API", "status": "running", "version": "1.0.0"}

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "users": len(users_db),
        "projects": len(projects_db),
        "tasks": len(tasks_db),
        "team_members": len(team_members_db)
    }