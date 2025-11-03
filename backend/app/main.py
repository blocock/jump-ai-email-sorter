from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routers import auth, categories, emails, accounts
from app.config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Email Sorter", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(emails.router)
app.include_router(accounts.router)


@app.get("/")
async def root():
    return {"message": "AI Email Sorter API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

