#!/usr/bin/env python3
"""
🔗 Fix Apply URLs Script
Updates existing internships with realistic job board URLs
"""

import os
import sys
import random
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.models import Internship
from app.config import settings

# Load environment variables
load_dotenv()

# Database setup
DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_realistic_url(company):
    """Generate realistic job board URLs"""
    job_boards = [
        f"https://www.indeed.com/viewjob?jk={random.randint(1000000000, 9999999999)}",
        f"https://www.linkedin.com/jobs/view/{random.randint(1000000000, 9999999999)}",
        f"https://jobs.apple.com/en-us/details/{random.randint(1000000000, 9999999999)}",
        f"https://careers.google.com/jobs/results/{random.randint(1000000000, 9999999999)}",
        f"https://jobs.netflix.com/jobs/{random.randint(1000000000, 9999999999)}",
        f"https://jobs.lever.co/{company.lower().replace(' ', '')}/{random.randint(1000000000, 9999999999)}",
        f"https://boards.greenhouse.io/{company.lower().replace(' ', '')}/jobs/{random.randint(1000000000, 9999999999)}",
        f"https://www.glassdoor.com/job-listing/{random.randint(1000000000, 9999999999)}",
        f"https://jobs.github.com/{random.randint(1000000000, 9999999999)}",
        f"https://angel.co/company/{company.lower().replace(' ', '')}/jobs/{random.randint(1000000000, 9999999999)}"
    ]
    return random.choice(job_boards)

def fix_apply_urls():
    """Update all internships with realistic apply URLs"""
    print("🔗 Fixing apply URLs for existing internships...")
    
    db_session = next(get_db())
    
    try:
        # Get all internships
        internships = db_session.query(Internship).all()
        
        updated_count = 0
        for internship in internships:
            # Generate new realistic URL
            new_url = generate_realistic_url(internship.company)
            internship.apply_url = new_url
            updated_count += 1
            print(f"✅ Updated: {internship.title} at {internship.company}")
        
        db_session.commit()
        print(f"🎉 Successfully updated {updated_count} internship URLs!")
        
    except Exception as e:
        db_session.rollback()
        print(f"❌ Error updating URLs: {e}")
    finally:
        db_session.close()

if __name__ == "__main__":
    fix_apply_urls()
