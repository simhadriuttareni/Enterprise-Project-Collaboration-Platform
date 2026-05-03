from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Backend is running!"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/api/v1/health")
def health_v1():
    return {"status": "healthy", "version": "1.0"}

@app.post("/api/v1/auth/signup")
def signup():
    return {"message": "Signup endpoint working"}

@app.post("/api/v1/auth/login")
def login():
    return {"access_token": "test_token", "token_type": "bearer"}