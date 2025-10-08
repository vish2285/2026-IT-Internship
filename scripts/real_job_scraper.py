#!/usr/bin/env python3
"""
🔍 Real Job Scraper Script
Scrapes actual job postings with real application URLs
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.models import Base, Internship
from app.services.real_job_scraper import RealJobScraper
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler("real_scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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

def clean_old_jobs(db_session):
    """Removes jobs older than 30 days."""
    cutoff_date = datetime.now().date() - timedelta(days=30)
    old_jobs_count = db_session.query(Internship).filter(Internship.posted_date < cutoff_date).count()
    if old_jobs_count > 0:
        db_session.query(Internship).filter(Internship.posted_date < cutoff_date).delete(synchronize_session=False)
        db_session.commit()
        logger.info(f"🧹 Cleaned {old_jobs_count} old jobs.")
    else:
        logger.info("🧹 No old jobs to clean.")

def run_real_job_scraper():
    """Run the real job scraper to get actual job postings"""
    logger.info("🔍 Starting Real Job Scraper - Finding Actual Job Postings")
    logger.info("=" * 60)
    
    db_session = next(get_db())
    
    try:
        # Ensure tables are created
        Base.metadata.create_all(bind=engine)
        
        # Clean old jobs
        clean_old_jobs(db_session)
        
        scraper = RealJobScraper()
        all_new_jobs = []
        
        fields = ['Cybersecurity', 'IT', 'Neuroscience']
        for field in fields:
            logger.info(f"🔍 Scraping real {field} internships...")
            
            try:
                scraped_jobs = scraper.scrape_all_sources(field)
                
                new_jobs_for_field = 0
                for job_data in scraped_jobs:
                    # Check if job already exists
                    existing_job = db_session.query(Internship).filter(
                        Internship.title == job_data['title'],
                        Internship.company == job_data['company'],
                        Internship.location == job_data['location']
                    ).first()
                    
                    if not existing_job:
                        new_job = Internship(**job_data)
                        db_session.add(new_job)
                        all_new_jobs.append(new_job)
                        new_jobs_for_field += 1
                        logger.info(f"✅ Added: {job_data['title']} at {job_data['company']}")
                        logger.info(f"🔗 Apply URL: {job_data['apply_url']}")
                    else:
                        logger.info(f"ℹ️  Skipped existing: {job_data['title']} at {job_data['company']}")
                
                logger.info(f"📊 Found {new_jobs_for_field} new {field} internships")
                
            except Exception as e:
                logger.error(f"❌ Error scraping {field}: {e}")
                continue
        
        db_session.commit()
        
        if all_new_jobs:
            logger.info(f"🎉 Added {len(all_new_jobs)} new real internships!")
            logger.info("🔗 All apply URLs are real job postings you can actually apply to!")
        else:
            logger.info("ℹ️  No new real internships found this run")
        
        # Final statistics
        total_active = db_session.query(Internship).filter(Internship.is_active == True).count()
        cybersecurity_count = db_session.query(Internship).filter(Internship.field == "Cybersecurity", Internship.is_active == True).count()
        it_count = db_session.query(Internship).filter(Internship.field == "IT", Internship.is_active == True).count()
        neuroscience_count = db_session.query(Internship).filter(Internship.field == "Neuroscience", Internship.is_active == True).count()
        
        logger.info("📊 Final database statistics:")
        logger.info(f"   - Total active jobs: {total_active}")
        logger.info(f"   - Cybersecurity: {cybersecurity_count}")
        logger.info(f"   - IT: {it_count}")
        logger.info(f"   - Neuroscience: {neuroscience_count}")
        logger.info(f"   - New real jobs added: {len(all_new_jobs)}")
        
    except Exception as e:
        db_session.rollback()
        logger.error(f"❌ Error in real job scraper: {e}", exc_info=True)
    finally:
        db_session.close()
    
    logger.info("=" * 60)

if __name__ == "__main__":
    run_real_job_scraper()
