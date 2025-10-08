from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel

from ..database import get_db
from ..models import Internship

router = APIRouter()

@router.get("/internships", response_model=List[dict])
async def get_internships(
    field: Optional[str] = Query(None, description="Filter by field: Cybersecurity, IT, or Neuroscience"),
    location: Optional[str] = Query(None, description="Filter by location"),
    active_only: bool = Query(True, description="Show only active internships"),
    db: Session = Depends(get_db)
):
    """Get all internships with optional filtering"""
    query = db.query(Internship)
    
    if active_only:
        query = query.filter(Internship.is_active == True)
    
    if field:
        query = query.filter(Internship.field == field)
    
    if location:
        query = query.filter(Internship.location.ilike(f"%{location}%"))
    
    internships = query.order_by(Internship.posted_date.desc()).all()
    return [internship.to_dict() for internship in internships]

@router.get("/internships/{internship_id}", response_model=dict)
async def get_internship(internship_id: int, db: Session = Depends(get_db)):
    """Get a specific internship by ID"""
    internship = db.query(Internship).filter(Internship.id == internship_id).first()
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")
    return internship.to_dict()

@router.post("/internships", response_model=dict)
async def create_internship(
    title: str,
    company: str,
    location: str,
    field: str,
    apply_url: str,
    description: Optional[str] = None,
    deadline: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Create a new internship listing"""
    if field not in ["Cybersecurity", "IT", "Neuroscience"]:
        raise HTTPException(status_code=400, detail="Field must be one of: Cybersecurity, IT, Neuroscience")
    
    internship = Internship(
        title=title,
        company=company,
        location=location,
        field=field,
        apply_url=apply_url,
        description=description,
        deadline=deadline,
        posted_date=datetime.now().date()
    )
    
    db.add(internship)
    db.commit()
    db.refresh(internship)
    
    return internship.to_dict()

@router.put("/internships/{internship_id}", response_model=dict)
async def update_internship(
    internship_id: int,
    title: Optional[str] = None,
    company: Optional[str] = None,
    location: Optional[str] = None,
    field: Optional[str] = None,
    apply_url: Optional[str] = None,
    description: Optional[str] = None,
    deadline: Optional[date] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Update an existing internship"""
    internship = db.query(Internship).filter(Internship.id == internship_id).first()
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")
    
    if field and field not in ["Cybersecurity", "IT", "Neuroscience"]:
        raise HTTPException(status_code=400, detail="Field must be one of: Cybersecurity, IT, Neuroscience")
    
    update_data = {
        "title": title,
        "company": company,
        "location": location,
        "field": field,
        "apply_url": apply_url,
        "description": description,
        "deadline": deadline,
        "is_active": is_active
    }
    
    for field_name, value in update_data.items():
        if value is not None:
            setattr(internship, field_name, value)
    
    db.commit()
    db.refresh(internship)
    
    return internship.to_dict()

@router.delete("/internships/{internship_id}")
async def delete_internship(internship_id: int, db: Session = Depends(get_db)):
    """Delete an internship (soft delete by setting is_active to False)"""
    internship = db.query(Internship).filter(Internship.id == internship_id).first()
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")
    
    internship.is_active = False
    db.commit()
    
    return {"message": "Internship deactivated successfully"}

@router.get("/internships/stats/summary")
async def get_stats(db: Session = Depends(get_db)):
    """Get statistics about internships"""
    total = db.query(Internship).filter(Internship.is_active == True).count()
    cybersecurity = db.query(Internship).filter(Internship.field == "Cybersecurity", Internship.is_active == True).count()
    it = db.query(Internship).filter(Internship.field == "IT", Internship.is_active == True).count()
    neuroscience = db.query(Internship).filter(Internship.field == "Neuroscience", Internship.is_active == True).count()
    
    return {
        "total_active": total,
        "by_field": {
            "Cybersecurity": cybersecurity,
            "IT": it,
            "Neuroscience": neuroscience
        }
    }

# Pydantic models for request/response
class ApplicationStatusUpdate(BaseModel):
    application_status: str

@router.patch("/internships/{internship_id}/status")
async def update_application_status(
    internship_id: int,
    status_update: ApplicationStatusUpdate,
    db: Session = Depends(get_db)
):
    """Update application status for a specific internship"""
    internship = db.query(Internship).filter(Internship.id == internship_id).first()
    
    if not internship:
        raise HTTPException(status_code=404, detail="Internship not found")
    
    # Validate status
    valid_statuses = ["not_applied", "applied", "started", "completed"]
    if status_update.application_status not in valid_statuses:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    internship.application_status = status_update.application_status
    db.commit()
    
    return {
        "id": internship.id,
        "title": internship.title,
        "company": internship.company,
        "application_status": internship.application_status,
        "message": f"Application status updated to '{status_update.application_status}'"
    }
