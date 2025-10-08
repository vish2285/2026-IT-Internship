#!/usr/bin/env python3
"""
Add application_status column to existing internships table.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.database import SessionLocal, engine
from app.models import Base, Internship
from sqlalchemy import text
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_application_status_column():
    """Add application_status column to internships table."""
    logger.info("🔄 Adding application_status column to internships table...")
    
    try:
        # Check if column already exists
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'internships' 
                AND column_name = 'application_status'
            """))
            
            if result.fetchone():
                logger.info("✅ application_status column already exists")
                return True
        
        # Add the column
        with engine.connect() as conn:
            conn.execute(text("""
                ALTER TABLE internships 
                ADD COLUMN application_status VARCHAR(20) DEFAULT 'not_applied' NOT NULL
            """))
            conn.commit()
        
        logger.info("✅ Successfully added application_status column")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error adding application_status column: {e}")
        return False

def update_existing_records():
    """Update existing records to have default application_status."""
    logger.info("🔄 Updating existing records with default application_status...")
    
    db = SessionLocal()
    try:
        # Update all records that don't have application_status set
        updated_count = db.query(Internship).filter(
            Internship.application_status == None
        ).update({
            Internship.application_status: 'not_applied'
        })
        
        db.commit()
        logger.info(f"✅ Updated {updated_count} existing records")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error updating existing records: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    """Main function to add application_status column."""
    logger.info("=" * 60)
    logger.info("🔧 Adding Application Status Column")
    logger.info("=" * 60)
    
    try:
        # Add the column
        if not add_application_status_column():
            logger.error("Failed to add application_status column")
            return False
        
        # Update existing records
        if not update_existing_records():
            logger.error("Failed to update existing records")
            return False
        
        logger.info("🎉 Application status column added successfully!")
        logger.info("=" * 60)
        return True
        
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"❌ Migration failed: {e}")
        logger.error("=" * 60)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

