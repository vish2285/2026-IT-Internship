from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from datetime import datetime

from .database import get_db, engine
from .models import Internship, Base
from .routers import internships

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Internship Hub API",
    description="API for managing internship opportunities in Cybersecurity, IT, and Neuroscience",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(internships.router, prefix="/api/v1", tags=["internships"])

@app.get("/")
async def root():
    return {"message": "Internship Hub API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

