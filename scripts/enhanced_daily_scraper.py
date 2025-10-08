#!/usr/bin/env python3
"""
Enhanced daily scraper with better error handling and more job sources.
"""

import os
import sys
from datetime import datetime, timedelta
import logging
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.database import SessionLocal, engine
from app.models import Base, Internship
from app.services.enhanced_scraper import EnhancedJobScraper
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def clean_old_jobs(db):
    """Remove jobs older than 60 days."""
    cutoff_date = datetime.now() - timedelta(days=60)
    
    try:
        old_jobs = db.query(Internship).filter(
            Internship.posted_date < cutoff_date.date()
        ).all()
        
        if old_jobs:
            for job in old_jobs:
                db.delete(job)
            
            db.commit()
            logger.info(f"Cleaned {len(old_jobs)} old jobs")
        else:
            logger.info("No old jobs to clean")
            
    except Exception as e:
        logger.error(f"Error cleaning old jobs: {e}")
        db.rollback()

def add_jobs_to_database(db, jobs):
    """Add new jobs to database, avoiding duplicates."""
    added_count = 0
    duplicate_count = 0
    
    for job_data in jobs:
        try:
            # Check if job already exists
            existing_job = db.query(Internship).filter(
                Internship.title == job_data['title'],
                Internship.company == job_data['company'],
                Internship.source == job_data['source']
            ).first()
            
            if existing_job:
                duplicate_count += 1
                continue
            
            # Create new internship
            internship = Internship(
                title=job_data['title'],
                company=job_data['company'],
                location=job_data['location'],
                field=job_data['field'],
                apply_url=job_data['apply_url'],
                description=job_data['description'],
                source=job_data['source'],
                posted_date=job_data['posted_date'],
                deadline=job_data['deadline'],
                is_active=True
            )
            
            db.add(internship)
            added_count += 1
            
        except Exception as e:
            logger.error(f"Error adding job {job_data.get('title', 'Unknown')}: {e}")
            continue
    
    try:
        db.commit()
        logger.info(f"Added {added_count} new jobs, skipped {duplicate_count} duplicates")
        return added_count
    except Exception as e:
        logger.error(f"Error committing jobs to database: {e}")
        db.rollback()
        return 0

def run_enhanced_daily_scraper():
    """Run the enhanced daily scraper."""
    logger.info("🚀 Starting enhanced daily scraper...")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Clean old jobs
        logger.info("🧹 Cleaning old jobs...")
        clean_old_jobs(db)
        
        # Initialize enhanced scraper
        scraper = EnhancedJobScraper()
        
        total_new_jobs = 0
        
        # Scrape for each field
        fields = ['Cybersecurity', 'IT', 'Neuroscience']
        
        for field in fields:
            logger.info(f"🔍 Scraping {field} internships...")
            
            try:
                # Get search terms for this field
                search_terms = scraper.search_terms.get(field, [])
                
                if not search_terms:
                    logger.warning(f"No search terms found for {field}")
                    continue
                
                # Scrape jobs
                jobs = scraper.scrape_jobs(field, search_terms[:5])  # Limit to 5 keywords per field
                
                if jobs:
                    # Add to database
                    added_count = add_jobs_to_database(db, jobs)
                    total_new_jobs += added_count
                    logger.info(f"✅ Added {added_count} new {field} jobs")
                else:
                    logger.warning(f"No {field} jobs found")
                
            except Exception as e:
                logger.error(f"Error scraping {field} jobs: {e}")
                continue
        
        # Get final statistics
        total_jobs = db.query(Internship).filter(Internship.is_active == True).count()
        cybersecurity_count = db.query(Internship).filter(
            Internship.field == "Cybersecurity", 
            Internship.is_active == True
        ).count()
        it_count = db.query(Internship).filter(
            Internship.field == "IT", 
            Internship.is_active == True
        ).count()
        neuroscience_count = db.query(Internship).filter(
            Internship.field == "Neuroscience", 
            Internship.is_active == True
        ).count()
        
        logger.info("📊 Final database statistics:")
        logger.info(f"   - Total active jobs: {total_jobs}")
        logger.info(f"   - Cybersecurity: {cybersecurity_count}")
        logger.info(f"   - IT: {it_count}")
        logger.info(f"   - Neuroscience: {neuroscience_count}")
        logger.info(f"   - New jobs added today: {total_new_jobs}")
        
        return total_new_jobs
        
    except Exception as e:
        logger.error(f"💥 Error in enhanced daily scraper: {e}")
        db.rollback()
        return 0
    finally:
        db.close()

def main():
    """Main function to run enhanced daily scraper."""
    logger.info("=" * 60)
    logger.info("🤖 Enhanced Daily Job Scraper")
    logger.info("=" * 60)
    
    try:
        new_jobs_count = run_enhanced_daily_scraper()
        
        if new_jobs_count > 0:
            logger.info("🎉 Enhanced daily scraper completed successfully!")
            logger.info(f"📈 Added {new_jobs_count} new internship opportunities")
        else:
            logger.info("ℹ️  No new jobs found today")
        
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"❌ Enhanced daily scraper failed: {e}")
        logger.error("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()

