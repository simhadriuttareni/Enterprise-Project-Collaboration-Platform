# 🚀 Enterprise Project Collaboration Platform- Production Ready Full-Stack Application

![React](https://img.shields.io/badge/React-18-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.3-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)



## ✨ Features

### 🔐 Authentication
- Secure JWT-based authentication
- Password hashing with bcrypt
- Protected routes and API endpoints

### 📁 Project Management
- Create, read, update, delete projects
- Project descriptions and metadata
- Owner-based access control

### ✅ Task Tracking
- Tasks with status (Todo/In Progress/Review/Done)
- Priority levels (Low/Medium/High/Urgent)
- Due dates and overdue detection
- Real-time task updates

### 👥 Team Collaboration
- Add/remove team members
- Role-based access (Admin/Member)
- Real-time member list updates
- User search functionality

### 📊 Dashboard Analytics
- Task completion statistics
- Overdue task tracking
- Project progress indicators
- Recent activity feed

## 🏗️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 18, Tailwind CSS, Framer Motion, Axios |
| **Backend** | FastAPI (Python 3.11), JWT, bcrypt |
| **Database** | PostgreSQL, SQLAlchemy ORM |
| **Deployment** | Vercel (Frontend), Render (Backend), Neon (Database) |

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (or use Neon.tech for free cloud DB)

### Backend Setup

```bash
# Clone repository
git clone https://github.com/simhadriuttareni/Team-Task-Manager.git
cd Team-Task-Manager/backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo DATABASE_URL=postgresql://postgres:password@localhost:5432/teamtaskmanager > .env
echo SECRET_KEY=your-secret-key-here >> .env

# Run server
uvicorn app.simple_no_jwt:app --reload --port 8000
