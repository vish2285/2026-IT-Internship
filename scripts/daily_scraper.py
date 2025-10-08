#!/usr/bin/env python3
"""
Daily job scraping automation script.
This script runs daily to fetch new internships and update the database.
"""

import os
import sys
import logging
from datetime import datetime, date, timedelta
from pathlib import Path

# Add the backend app directory to the Python path
backend_path = Path(__file__).parent.parent / "backend" / "app"
sys.path.insert(0, str(backend_path))

from database import SessionLocal, engine
from models import Internship, Base
from services.job_scraper import JobScraper

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def scrape_and_update_database():
    """Scrape jobs and update database."""
    logger.info("🚀 Starting daily job scraping...")
    
    try:
        # Create database tables if they don't exist
        Base.metadata.create_all(bind=engine)
        
        # Initialize scraper
        scraper = JobScraper()
        
        # Scrape all sources
        logger.info("📡 Scraping job sites...")
        new_jobs = scraper.scrape_all_sources()
        
        if not new_jobs:
            logger.warning("⚠️ No new jobs found")
            return
        
        logger.info(f"✅ Found {len(new_jobs)} new job opportunities")
        
        # Create database session
        db = SessionLocal()
        
        try:
            added_count = 0
            updated_count = 0
            
            for job_data in new_jobs:
                try:
                    # Check if job already exists
                    existing_job = db.query(Internship).filter(
                        Internship.title == job_data['title'],
                        Internship.company == job_data['company']
                    ).first()
                    
                    if existing_job:
                        # Update existing job if it's inactive
                        if not existing_job.is_active:
                            existing_job.is_active = True
                            existing_job.updated_at = datetime.now()
                            updated_count += 1
                            logger.info(f"🔄 Reactivated: {job_data['title']} at {job_data['company']}")
                    else:
                        # Create new job
                        internship = Internship(
                            title=job_data['title'],
                            company=job_data['company'],
                            location=job_data['location'],
                            field=job_data['field'],
                            apply_url=job_data['apply_url'],
                            description=job_data['description'],
                            posted_date=job_data['posted_date'],
                            deadline=job_data['deadline'],
                            is_active=True
                        )
                        
                        db.add(internship)
                        added_count += 1
                        logger.info(f"➕ Added: {job_data['title']} at {job_data['company']} ({job_data['field']})")
                
                except Exception as e:
                    logger.error(f"❌ Error processing job {job_data.get('title', 'Unknown')}: {e}")
                    continue
            
            # Commit all changes
            db.commit()
            
            logger.info(f"🎉 Scraping completed successfully!")
            logger.info(f"   - Added: {added_count} new jobs")
            logger.info(f"   - Updated: {updated_count} existing jobs")
            logger.info(f"   - Total processed: {len(new_jobs)} jobs")
            
            # Get current statistics
            total_active = db.query(Internship).filter(Internship.is_active == True).count()
            cybersecurity = db.query(Internship).filter(
                Internship.field == "Cybersecurity", 
                Internship.is_active == True
            ).count()
            it = db.query(Internship).filter(
                Internship.field == "IT", 
                Internship.is_active == True
            ).count()
            neuroscience = db.query(Internship).filter(
                Internship.field == "Neuroscience", 
                Internship.is_active == True
            ).count()
            
            logger.info(f"📊 Current database statistics:")
            logger.info(f"   - Total active internships: {total_active}")
            logger.info(f"   - Cybersecurity: {cybersecurity}")
            logger.info(f"   - IT: {it}")
            logger.info(f"   - Neuroscience: {neuroscience}")
            
        except Exception as e:
            logger.error(f"❌ Database error: {e}")
            db.rollback()
            raise
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"💥 Scraping failed: {e}")
        raise

def cleanup_old_jobs():
    """Remove jobs older than 60 days."""
    logger.info("🧹 Cleaning up old jobs...")
    
    try:
        db = SessionLocal()
        
        # Calculate cutoff date (60 days ago)
        cutoff_date = date.today() - timedelta(days=60)
        
        # Find old jobs
        old_jobs = db.query(Internship).filter(
            Internship.posted_date < cutoff_date,
            Internship.is_active == True
        ).all()
        
        if old_jobs:
            # Deactivate old jobs
            for job in old_jobs:
                job.is_active = False
                job.updated_at = datetime.now()
            
            db.commit()
            logger.info(f"🗑️ Deactivated {len(old_jobs)} old jobs (older than 60 days)")
        else:
            logger.info("✅ No old jobs to clean up")
        
        db.close()
        
    except Exception as e:
        logger.error(f"❌ Cleanup error: {e}")

def main():
    """Main function to run daily scraping."""
    logger.info("=" * 50)
    logger.info("🤖 Daily Job Scraping Started")
    logger.info(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 50)
    
    try:
        # Scrape and update database
        scrape_and_update_database()
        
        # Clean up old jobs
        cleanup_old_jobs()
        
        logger.info("=" * 50)
        logger.info("✅ Daily scraping completed successfully!")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error("=" * 50)
        logger.error(f"❌ Daily scraping failed: {e}")
        logger.error("=" * 50)
        sys.exit(1)

if __name__ == "__main__":
    main()

