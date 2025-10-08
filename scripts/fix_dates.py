#!/usr/bin/env python3
"""
Script to fix the dates for existing internships in the database.
This will update posted dates and deadlines to be more realistic.
"""

import os
import sys
import random
from datetime import datetime, date, timedelta
from pathlib import Path

# Add the backend app directory to the Python path
backend_path = Path(__file__).parent.parent / "backend" / "app"
sys.path.insert(0, str(backend_path))

from database import SessionLocal, engine
from models import Internship, Base

def fix_internship_dates():
    """Update existing internships with more realistic dates."""
    print("🔧 Fixing internship dates...")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Get all active internships
        internships = db.query(Internship).filter(Internship.is_active == True).all()
        
        print(f"📊 Found {len(internships)} internships to update")
        
        updated_count = 0
        
        for internship in internships:
            try:
                # Generate realistic posted date (1-60 days ago)
                days_ago = random.randint(1, 60)
                new_posted_date = date.today() - timedelta(days=days_ago)
                
                # Calculate realistic deadline based on field
                if internship.field == "Cybersecurity":
                    # Security jobs often have longer application periods
                    days_to_deadline = random.randint(45, 90)
                elif internship.field == "IT":
                    # Tech jobs vary widely
                    days_to_deadline = random.randint(30, 75)
                elif internship.field == "Neuroscience":
                    # Research positions often have longer periods
                    days_to_deadline = random.randint(60, 120)
                else:
                    days_to_deadline = random.randint(30, 60)
                
                # Ensure deadline is at least 7 days from posted date
                min_deadline = new_posted_date + timedelta(days=7)
                calculated_deadline = new_posted_date + timedelta(days=days_to_deadline)
                new_deadline = max(min_deadline, calculated_deadline)
                
                # Update the internship
                internship.posted_date = new_posted_date
                internship.deadline = new_deadline
                internship.updated_at = datetime.now()
                
                updated_count += 1
                
                print(f"✅ Updated: {internship.title} at {internship.company}")
                print(f"   Posted: {new_posted_date.strftime('%b %d, %Y')}")
                print(f"   Deadline: {new_deadline.strftime('%b %d, %Y')}")
                print()
                
            except Exception as e:
                print(f"❌ Error updating {internship.title}: {e}")
                continue
        
        # Commit all changes
        db.commit()
        
        print(f"🎉 Successfully updated {updated_count} internships!")
        
        # Show statistics
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
        
        print(f"📊 Updated database statistics:")
        print(f"   - Cybersecurity: {cybersecurity} internships")
        print(f"   - IT: {it} internships")
        print(f"   - Neuroscience: {neuroscience} internships")
        print(f"   - Total: {cybersecurity + it + neuroscience} internships")
        
    except Exception as e:
        print(f"❌ Error fixing dates: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Main function to fix internship dates."""
    print("=" * 50)
    print("🔧 Fixing Internship Dates")
    print("=" * 50)
    
    try:
        fix_internship_dates()
        print("=" * 50)
        print("✅ Date fixing completed successfully!")
        print("=" * 50)
        
    except Exception as e:
        print("=" * 50)
        print(f"❌ Date fixing failed: {e}")
        print("=" * 50)
        sys.exit(1)

if __name__ == "__main__":
    main()

