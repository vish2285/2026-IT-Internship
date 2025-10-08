#!/usr/bin/env python3
"""
Script to seed the database with sample internship data.
"""

import os
import sys
from datetime import datetime, date, timedelta
from pathlib import Path

# Add the backend app directory to the Python path
backend_path = Path(__file__).parent.parent / "backend" / "app"
sys.path.insert(0, str(backend_path))

from database import SessionLocal, engine
from models import Internship, Base

def create_sample_internships():
    """Create sample internship data."""
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Check if internships already exist
        existing_count = db.query(Internship).count()
        if existing_count > 0:
            print(f"Database already contains {existing_count} internships. Skipping seed.")
            return
        
        # Sample internship data
        sample_internships = [
            # Cybersecurity Internships
            {
                "title": "Cybersecurity Analyst Intern",
                "company": "Microsoft",
                "location": "Redmond, WA",
                "field": "Cybersecurity",
                "apply_url": "https://careers.microsoft.com/us/en/job/123456",
                "description": "Join our security team to help protect Microsoft's infrastructure and customers from cyber threats.",
                "deadline": date.today() + timedelta(days=30)
            },
            {
                "title": "Security Engineering Intern",
                "company": "Google",
                "location": "Mountain View, CA",
                "field": "Cybersecurity",
                "apply_url": "https://careers.google.com/jobs/results/123456",
                "description": "Work on cutting-edge security technologies and help build secure systems at scale.",
                "deadline": date.today() + timedelta(days=45)
            },
            {
                "title": "Cybersecurity Research Intern",
                "company": "MITRE",
                "location": "McLean, VA",
                "field": "Cybersecurity",
                "apply_url": "https://mitre.org/careers/123456",
                "description": "Conduct research on emerging cybersecurity threats and develop innovative solutions.",
                "deadline": date.today() + timedelta(days=60)
            },
            
            # IT Internships
            {
                "title": "Software Engineering Intern",
                "company": "Apple",
                "location": "Cupertino, CA",
                "field": "IT",
                "apply_url": "https://jobs.apple.com/en-us/details/123456",
                "description": "Develop innovative software solutions for Apple's ecosystem of products and services.",
                "deadline": date.today() + timedelta(days=25)
            },
            {
                "title": "Cloud Infrastructure Intern",
                "company": "Amazon Web Services",
                "location": "Seattle, WA",
                "field": "IT",
                "apply_url": "https://amazon.jobs/en/jobs/123456",
                "description": "Work on AWS cloud infrastructure and help build scalable, reliable systems.",
                "deadline": date.today() + timedelta(days=40)
            },
            {
                "title": "Data Engineering Intern",
                "company": "Netflix",
                "location": "Los Gatos, CA",
                "field": "IT",
                "apply_url": "https://jobs.netflix.com/jobs/123456",
                "description": "Build data pipelines and analytics systems to support Netflix's global streaming platform.",
                "deadline": date.today() + timedelta(days=35)
            },
            {
                "title": "DevOps Engineering Intern",
                "company": "Docker",
                "location": "San Francisco, CA",
                "field": "IT",
                "apply_url": "https://docker.com/careers/123456",
                "description": "Help build and maintain Docker's containerization platform and developer tools.",
                "deadline": date.today() + timedelta(days=50)
            },
            
            # Neuroscience Internships
            {
                "title": "Neuroscience Research Intern",
                "company": "Stanford University",
                "location": "Stanford, CA",
                "field": "Neuroscience",
                "apply_url": "https://stanford.edu/careers/123456",
                "description": "Conduct cutting-edge neuroscience research in brain-computer interfaces and neural networks.",
                "deadline": date.today() + timedelta(days=55)
            },
            {
                "title": "Cognitive Science Intern",
                "company": "MIT",
                "location": "Cambridge, MA",
                "field": "Neuroscience",
                "apply_url": "https://web.mit.edu/careers/123456",
                "description": "Study human cognition and develop AI systems inspired by neural processes.",
                "deadline": date.today() + timedelta(days=65)
            },
            {
                "title": "Neurotechnology Intern",
                "company": "Neuralink",
                "location": "Austin, TX",
                "field": "Neuroscience",
                "apply_url": "https://neuralink.com/careers/123456",
                "description": "Work on brain-machine interface technology and neural implant development.",
                "deadline": date.today() + timedelta(days=70)
            },
            {
                "title": "Neuroscience Data Analysis Intern",
                "company": "Allen Institute for Brain Science",
                "location": "Seattle, WA",
                "field": "Neuroscience",
                "apply_url": "https://alleninstitute.org/careers/123456",
                "description": "Analyze large-scale neuroscience datasets to understand brain function and connectivity.",
                "deadline": date.today() + timedelta(days=45)
            }
        ]
        
        # Add internships to database
        for internship_data in sample_internships:
            internship = Internship(
                title=internship_data["title"],
                company=internship_data["company"],
                location=internship_data["location"],
                field=internship_data["field"],
                apply_url=internship_data["apply_url"],
                description=internship_data["description"],
                deadline=internship_data["deadline"],
                posted_date=date.today() - timedelta(days=1)  # Posted yesterday
            )
            db.add(internship)
        
        # Commit changes
        db.commit()
        print(f"✅ Successfully added {len(sample_internships)} sample internships to the database!")
        
        # Print summary
        cybersecurity_count = db.query(Internship).filter(Internship.field == "Cybersecurity").count()
        it_count = db.query(Internship).filter(Internship.field == "IT").count()
        neuroscience_count = db.query(Internship).filter(Internship.field == "Neuroscience").count()
        
        print(f"📊 Database Summary:")
        print(f"   - Cybersecurity: {cybersecurity_count} internships")
        print(f"   - IT: {it_count} internships")
        print(f"   - Neuroscience: {neuroscience_count} internships")
        print(f"   - Total: {cybersecurity_count + it_count + neuroscience_count} internships")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Main function to seed the database."""
    print("🌱 Starting database seeding process...")
    
    try:
        create_sample_internships()
        print("🎉 Database seeding completed successfully!")
        return True
    except Exception as e:
        print(f"💥 Database seeding failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

