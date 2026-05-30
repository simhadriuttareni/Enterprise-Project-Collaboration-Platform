# 🚀 Enterprise Project Collaboration Platform

A production-ready full-stack collaboration platform designed for teams to manage projects, track tasks, monitor productivity, and collaborate efficiently through secure role-based access control.

Built using **React, FastAPI, PostgreSQL, and JWT Authentication**, the platform provides enterprise-style project management capabilities similar to Jira, Trello, and ClickUp.

---

## 📌 Overview

Managing projects across teams requires secure collaboration, task visibility, progress tracking, and role-based permissions.

The Enterprise Project Collaboration Platform provides:

* Secure user authentication
* Project lifecycle management
* Task tracking and prioritization
* Team collaboration workflows
* Dashboard analytics and reporting
* Cloud deployment architecture

The system is designed with scalability, maintainability, and production-readiness in mind.

---

## ✨ Features

### 🔐 Authentication & Security

* JWT-based Authentication
* Secure Password Hashing using bcrypt
* Protected API Endpoints
* Role-Based Access Control (RBAC)
* User Session Management

---

### 📁 Project Management

* Create Projects
* Update Project Details
* Delete Projects
* Project Ownership Control
* Project Metadata Management

---

### ✅ Task Management

* Create Tasks
* Assign Tasks
* Update Task Status
* Delete Tasks

Task Workflow:

* Todo
* In Progress
* Review
* Done

Priority Levels:

* Low
* Medium
* High
* Urgent

Additional Features:

* Due Date Tracking
* Overdue Detection
* Task Filtering
* Status-Based Organization

---

### 👥 Team Collaboration

* Invite Team Members
* Remove Members
* Search Users
* Manage Team Access

Roles:

#### Admin

* Full Project Control
* Manage Team Members
* Create & Update Tasks
* Access Analytics

#### Member

* View Assigned Projects
* Manage Assigned Tasks
* Collaborate with Team

---

### 📊 Dashboard Analytics

Real-time project insights:

* Task Completion Statistics
* Overdue Task Monitoring
* Project Progress Tracking
* Team Productivity Overview
* Recent Activity Feed

---

## 🏗️ System Architecture

Frontend → React Application

↓

Backend → FastAPI REST APIs

↓

Database → PostgreSQL

↓

Cloud Infrastructure

* Vercel
* Render
* Neon PostgreSQL

---

## 🛠️ Tech Stack

### Frontend

* React 18
* Tailwind CSS
* Framer Motion
* Axios
* React Router

### Backend

* FastAPI
* Python 3.11
* JWT Authentication
* bcrypt
* Pydantic

### Database

* PostgreSQL
* SQLAlchemy ORM

### Deployment

* Vercel
* Render
* Neon Database

### Version Control

* Git
* GitHub

---

## 📂 Project Structure

```text
frontend/
│
├── src/
│   ├── components/
│   ├── pages/
│   ├── services/
│   ├── hooks/
│   └── assets/

backend/
│
├── app/
│   ├── routes/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── database/
│   └── auth/

└── requirements.txt
```

---

## 🚀 Local Setup

### Prerequisites

* Python 3.11+
* Node.js 18+
* PostgreSQL

---

## Backend Setup

Clone Repository

```bash
git clone https://github.com/simhadriuttareni/Enterprise-Project-Collaboration-Platform.git

cd Enterprise-Project-Collaboration-Platform/backend
```

Create Virtual Environment

```bash
python -m venv venv
```

Activate Environment

Windows:

```bash
venv\Scripts\activate
```

Mac/Linux:

```bash
source venv/bin/activate
```

Install Dependencies

```bash
pip install -r requirements.txt
```

Create .env File

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/db_name

SECRET_KEY=your-secret-key
```

Run Backend

```bash
uvicorn app.main:app --reload
```

---

## Frontend Setup

Navigate to Frontend

```bash
cd ../frontend
```

Install Packages

```bash
npm install
```

Start Frontend

```bash
npm run dev
```

Application will run at:

```text
http://localhost:5173
```

---

## 🔑 API Capabilities

### Authentication

* Register User
* Login User
* JWT Token Generation

### Projects

* Create Project
* Update Project
* Delete Project
* View Projects

### Tasks

* Create Task
* Update Task
* Delete Task
* Track Status

### Teams

* Add Members
* Remove Members
* Role Management

---

## 📈 Production Deployment

### Frontend

Hosted on:

Vercel

### Backend

Hosted on:

Render

### Database

Hosted on:

Neon PostgreSQL

This architecture enables independent scaling of frontend, backend, and database services.

---

## 🎯 Key Engineering Concepts Demonstrated

* Full-Stack Development
* REST API Design
* JWT Authentication
* Role-Based Access Control (RBAC)
* PostgreSQL Database Design
* ORM with SQLAlchemy
* Cloud Deployment
* Secure Password Management
* Production Application Architecture
* Team Collaboration Workflows

---

## 🚀 Future Enhancements

* Email Notifications
* Real-Time WebSocket Updates
* File Attachments
* Activity Audit Logs
* Docker Containerization
* CI/CD Pipelines
* Redis Caching
* Microservices Migration
* Kubernetes Deployment

---

## 👨‍💻 Author

**Simhadri Uttareni**

Backend & AI Engineer

### Tech Stack

Java • Spring Boot • PostgreSQL • Kafka • Redis • Docker • AWS • FastAPI • React

GitHub:
https://github.com/simhadriuttareni

LinkedIn:
https://www.linkedin.com/in/simhadri-uttareni

LeetCode:
https://leetcode.com/u/simhadri_02/

---

## ⭐ Final Note

This project was built to simulate real-world enterprise project management systems and demonstrate production-level software engineering practices including authentication, authorization, scalable backend architecture, cloud deployment, and collaborative workflow management.
