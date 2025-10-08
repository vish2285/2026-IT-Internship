#!/usr/bin/env python3
"""
🧹 Clean Fake Data Script
Removes all fake "Sample Internship" entries and duplicates
"""

import os
import sys
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.models import Internship
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler("clean_data.log"),
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

def clean_fake_data():
    """Remove all fake data and duplicates"""
    logger.info("🧹 Cleaning fake data and duplicates...")
    
    db_session = next(get_db())
    
    try:
        # Remove all "Sample Internship" entries
        sample_count = db_session.query(Internship).filter(
            Internship.title.like('%Sample Internship%')
        ).count()
        
        if sample_count > 0:
            db_session.query(Internship).filter(
                Internship.title.like('%Sample Internship%')
            ).delete(synchronize_session=False)
            logger.info(f"🗑️  Removed {sample_count} fake 'Sample Internship' entries")
        
        # Remove entries with "Company X" pattern
        fake_company_count = db_session.query(Internship).filter(
            Internship.company.like('%Company %')
        ).count()
        
        if fake_company_count > 0:
            db_session.query(Internship).filter(
                Internship.company.like('%Company %')
            ).delete(synchronize_session=False)
            logger.info(f"🗑️  Removed {fake_company_count} fake 'Company X' entries")
        
        # Remove duplicate entries (keep the first one)
        from sqlalchemy import func
        
        # Find duplicates by title, company, and location
        duplicates = db_session.query(
            Internship.title,
            Internship.company,
            Internship.location,
            func.count(Internship.id).label('count')
        ).group_by(
            Internship.title,
            Internship.company,
            Internship.location
        ).having(func.count(Internship.id) > 1).all()
        
        duplicate_count = 0
        for dup in duplicates:
            # Get all entries with this combination
            entries = db_session.query(Internship).filter(
                Internship.title == dup.title,
                Internship.company == dup.company,
                Internship.location == dup.location
            ).order_by(Internship.id).all()
            
            # Keep the first one, delete the rest
            for entry in entries[1:]:
                db_session.delete(entry)
                duplicate_count += 1
        
        if duplicate_count > 0:
            logger.info(f"🗑️  Removed {duplicate_count} duplicate entries")
        
        db_session.commit()
        
        # Final statistics
        total_active = db_session.query(Internship).filter(Internship.is_active == True).count()
        cybersecurity_count = db_session.query(Internship).filter(Internship.field == "Cybersecurity", Internship.is_active == True).count()
        it_count = db_session.query(Internship).filter(Internship.field == "IT", Internship.is_active == True).count()
        neuroscience_count = db_session.query(Internship).filter(Internship.field == "Neuroscience", Internship.is_active == True).count()
        
        logger.info("📊 Database after cleaning:")
        logger.info(f"   - Total active jobs: {total_active}")
        logger.info(f"   - Cybersecurity: {cybersecurity_count}")
        logger.info(f"   - IT: {it_count}")
        logger.info(f"   - Neuroscience: {neuroscience_count}")
        
        logger.info("✅ Database cleaned successfully!")
        
    except Exception as e:
        db_session.rollback()
        logger.error(f"❌ Error cleaning database: {e}", exc_info=True)
    finally:
        db_session.close()

if __name__ == "__main__":
    clean_fake_data()
