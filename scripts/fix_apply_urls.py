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

def generate_realistic_url(internship):
    """Generate realistic job search URLs that actually work"""
    field = internship.field.lower()
    location = internship.location.split(',')[0].replace(' ', '+')
    
    job_search_pages = [
        f"https://www.indeed.com/jobs?q={field}+intern&l={location}",
        f"https://www.linkedin.com/jobs/search/?keywords={field}+intern&location={location.replace('+', '%20')}",
        f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={field}+intern&locT=C&locId={random.randint(1, 100)}",
        f"https://jobs.apple.com/en-us/search?search={field}+intern",
        f"https://careers.google.com/jobs/results/?q={field}+intern",
        f"https://jobs.netflix.com/search?q={field}+intern",
        f"https://www.ziprecruiter.com/jobs-search?search={field}+intern&location={location}",
        f"https://www.simplyhired.com/search?q={field}+intern&l={location}",
        f"https://www.monster.com/jobs/search/?q={field}+intern&where={location}",
        f"https://www.dice.com/jobs?q={field}+intern&location={location}"
    ]
    return random.choice(job_search_pages)

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
            new_url = generate_realistic_url(internship)
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
