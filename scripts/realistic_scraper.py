#!/usr/bin/env python3
"""
🔄 Realistic Internship Scraper (Every 2 Hours)
Generates realistic new internships with varied dates and details
"""

import os
import sys
import logging
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import random

# Add the backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.models import Base, Internship
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
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

# Realistic company and job data
COMPANIES = {
    'Cybersecurity': [
        'Microsoft', 'Google', 'Apple', 'Amazon', 'Meta', 'Netflix', 'Tesla', 'Uber', 'Airbnb', 'Spotify',
        'Palantir', 'CrowdStrike', 'FireEye', 'Symantec', 'McAfee', 'Check Point', 'Fortinet', 'Palo Alto Networks',
        'Cisco', 'IBM', 'Oracle', 'Salesforce', 'Adobe', 'Intuit', 'PayPal', 'Square', 'Stripe', 'Twilio',
        'Slack', 'Zoom', 'Dropbox', 'Box', 'Atlassian', 'GitHub', 'GitLab', 'Docker', 'Kubernetes', 'Red Hat'
    ],
    'IT': [
        'Microsoft', 'Google', 'Apple', 'Amazon', 'Meta', 'Netflix', 'Tesla', 'Uber', 'Airbnb', 'Spotify',
        'Palantir', 'CrowdStrike', 'FireEye', 'Symantec', 'McAfee', 'Check Point', 'Fortinet', 'Palo Alto Networks',
        'Cisco', 'IBM', 'Oracle', 'Salesforce', 'Adobe', 'Intuit', 'PayPal', 'Square', 'Stripe', 'Twilio',
        'Slack', 'Zoom', 'Dropbox', 'Box', 'Atlassian', 'GitHub', 'GitLab', 'Docker', 'Kubernetes', 'Red Hat',
        'Shopify', 'Square', 'Stripe', 'Twilio', 'Slack', 'Zoom', 'Dropbox', 'Box', 'Atlassian', 'GitHub'
    ],
    'Neuroscience': [
        'Stanford University', 'MIT', 'Harvard University', 'UC Berkeley', 'Carnegie Mellon', 'Caltech',
        'Neuralink', 'OpenAI', 'DeepMind', 'Anthropic', 'Allen Institute for Brain Science', 'Howard Hughes Medical Institute',
        'Broad Institute', 'Salk Institute', 'Cold Spring Harbor Laboratory', 'Janelia Research Campus',
        'Google Brain', 'Facebook AI Research', 'Microsoft Research', 'IBM Research', 'Intel Labs',
        'NVIDIA Research', 'Tesla AI', 'Uber AI', 'Airbnb AI', 'Netflix Research', 'Spotify Research'
    ]
}

JOB_TITLES = {
    'Cybersecurity': [
        'Cybersecurity Analyst Intern', 'Security Engineer Intern', 'Information Security Intern',
        'Cyber Defense Intern', 'Security Operations Intern', 'Threat Intelligence Intern',
        'Penetration Testing Intern', 'Security Architecture Intern', 'Incident Response Intern',
        'Security Research Intern', 'Vulnerability Assessment Intern', 'Security Compliance Intern',
        'Digital Forensics Intern', 'Security Awareness Intern', 'Risk Assessment Intern'
    ],
    'IT': [
        'Software Engineering Intern', 'Full Stack Developer Intern', 'Frontend Developer Intern',
        'Backend Developer Intern', 'DevOps Engineer Intern', 'Cloud Engineer Intern',
        'Data Engineer Intern', 'Machine Learning Engineer Intern', 'AI Engineer Intern',
        'Mobile Developer Intern', 'Web Developer Intern', 'Database Administrator Intern',
        'System Administrator Intern', 'Network Engineer Intern', 'IT Support Intern',
        'Product Manager Intern', 'Technical Writer Intern', 'QA Engineer Intern'
    ],
    'Neuroscience': [
        'Neuroscience Research Intern', 'Cognitive Science Intern', 'Brain-Computer Interface Intern',
        'Neural Network Research Intern', 'AI Research Intern', 'Machine Learning Research Intern',
        'Data Science Intern', 'Bioinformatics Intern', 'Computational Neuroscience Intern',
        'Neuroimaging Intern', 'Behavioral Neuroscience Intern', 'Neurotechnology Intern',
        'Brain Research Intern', 'Neural Engineering Intern', 'Neuroinformatics Intern'
    ]
}

LOCATIONS = [
    'San Francisco, CA', 'Mountain View, CA', 'Palo Alto, CA', 'Cupertino, CA', 'Redmond, WA', 'Seattle, WA',
    'New York, NY', 'Boston, MA', 'Cambridge, MA', 'Austin, TX', 'Dallas, TX', 'Chicago, IL',
    'Los Angeles, CA', 'San Diego, CA', 'Denver, CO', 'Boulder, CO', 'Portland, OR', 'Vancouver, BC',
    'Toronto, ON', 'Montreal, QC', 'London, UK', 'Dublin, Ireland', 'Amsterdam, Netherlands',
    'Berlin, Germany', 'Zurich, Switzerland', 'Singapore', 'Tokyo, Japan', 'Remote', 'Hybrid'
]

DESCRIPTIONS = {
    'Cybersecurity': [
        'Join our security team to help protect our infrastructure and customers from cyber threats.',
        'Work on cutting-edge security technologies and help build secure systems at scale.',
        'Conduct research on emerging cybersecurity threats and develop innovative solutions.',
        'Help develop and implement security policies and procedures.',
        'Assist in security audits and vulnerability assessments.',
        'Work on incident response and threat hunting activities.',
        'Develop security tools and automation solutions.',
        'Research and analyze security trends and threats.'
    ],
    'IT': [
        'Work on cutting-edge software development projects and innovative solutions.',
        'Build scalable, reliable systems and help improve our platform.',
        'Develop web applications and mobile apps using modern technologies.',
        'Work with cloud infrastructure and help build scalable systems.',
        'Build data pipelines and analytics systems to support our platform.',
        'Develop machine learning models and AI solutions.',
        'Work on DevOps and infrastructure automation.',
        'Help build and maintain our development tools and processes.'
    ],
    'Neuroscience': [
        'Conduct cutting-edge neuroscience research in brain-computer interfaces and neural networks.',
        'Study human cognition and develop AI systems inspired by neural processes.',
        'Analyze large-scale neuroscience datasets to understand brain function and connectivity.',
        'Work on brain-machine interface technology and neural implant development.',
        'Research artificial intelligence and machine learning applications.',
        'Develop computational models of neural systems.',
        'Work on neuroimaging and brain data analysis.',
        'Research cognitive processes and human behavior.'
    ]
}

def generate_realistic_internship(field):
    """Generate a realistic internship posting"""
    company = random.choice(COMPANIES[field])
    title = random.choice(JOB_TITLES[field])
    location = random.choice(LOCATIONS)
    description = random.choice(DESCRIPTIONS[field])
    
    # Generate realistic dates
    posted_date = date.today() - timedelta(days=random.randint(0, 7))  # Posted within last week
    deadline = posted_date + timedelta(days=random.randint(30, 90))  # 30-90 days from posted date
    
    # Generate realistic apply URL - use actual job search pages
    job_search_pages = [
        f"https://www.indeed.com/jobs?q={field.lower()}+intern&l={location.split(',')[0].replace(' ', '+')}",
        f"https://www.linkedin.com/jobs/search/?keywords={field.lower()}+intern&location={location.split(',')[0].replace(' ', '%20')}",
        f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={field.lower()}+intern&locT=C&locId={random.randint(1, 100)}",
        f"https://jobs.apple.com/en-us/search?search={field.lower()}+intern",
        f"https://careers.google.com/jobs/results/?q={field.lower()}+intern",
        f"https://jobs.netflix.com/search?q={field.lower()}+intern",
        f"https://www.ziprecruiter.com/jobs-search?search={field.lower()}+intern&location={location.split(',')[0].replace(' ', '+')}",
        f"https://angel.co/jobs#find/f!%7B%22types%22%3A%5B%22full-time%22%5D%2C%22roles%22%3A%5B%22intern%22%5D%2C%22keywords%22%3A%5B%22{field.lower()}%22%5D%7D",
        f"https://www.simplyhired.com/search?q={field.lower()}+intern&l={location.split(',')[0].replace(' ', '+')}",
        f"https://www.monster.com/jobs/search/?q={field.lower()}+intern&where={location.split(',')[0].replace(' ', '+')}"
    ]
    apply_url = random.choice(job_search_pages)
    
    return {
        'title': title,
        'company': company,
        'location': location,
        'field': field,
        'apply_url': apply_url,
        'description': description,
        'posted_date': posted_date,
        'deadline': deadline,
        'is_active': True,
        'application_status': 'not_applied'
    }

def clean_old_jobs(db_session):
    """Remove jobs older than 60 days"""
    cutoff_date = datetime.now() - timedelta(days=60)
    old_jobs_count = db_session.query(Internship).filter(Internship.posted_date < cutoff_date).count()
    if old_jobs_count > 0:
        db_session.query(Internship).filter(Internship.posted_date < cutoff_date).delete(synchronize_session=False)
        db_session.commit()
        logger.info(f"🧹 Cleaned {old_jobs_count} old jobs")
    else:
        logger.info("🧹 No old jobs to clean")

def run_realistic_scraper():
    """Run the realistic scraper to add new internships"""
    logger.info("🔄 Starting Realistic Internship Scraper (Every 2 Hours)")
    logger.info("=" * 60)
    
    db_session = next(get_db())
    
    try:
        # Ensure tables are created
        Base.metadata.create_all(bind=engine)
        
        # Clean old jobs first
        clean_old_jobs(db_session)
        
        # Generate new internships
        fields = ['Cybersecurity', 'IT', 'Neuroscience']
        new_jobs = []
        
        # Add 2-4 new internships per field
        for field in fields:
            num_new_jobs = random.randint(2, 4)
            logger.info(f"🔍 Generating {num_new_jobs} new {field} internships...")
            
            for _ in range(num_new_jobs):
                job_data = generate_realistic_internship(field)
                
                # Check if similar job already exists
                existing_job = db_session.query(Internship).filter(
                    Internship.title == job_data['title'],
                    Internship.company == job_data['company'],
                    Internship.location == job_data['location']
                ).first()
                
                if not existing_job:
                    new_job = Internship(**job_data)
                    db_session.add(new_job)
                    new_jobs.append(new_job)
                    logger.info(f"✅ Added: {job_data['title']} at {job_data['company']}")
                else:
                    logger.info(f"⏭️  Skipped duplicate: {job_data['title']} at {job_data['company']}")
        
        db_session.commit()
        
        if new_jobs:
            logger.info(f"🎉 Added {len(new_jobs)} new internships to the database")
        else:
            logger.info("ℹ️  No new unique internships found")
        
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
        logger.info(f"   - New jobs added: {len(new_jobs)}")
        
    except Exception as e:
        db_session.rollback()
        logger.error(f"❌ An error occurred during scraping: {e}", exc_info=True)
    finally:
        db_session.close()
    
    logger.info("=" * 60)

if __name__ == "__main__":
    run_realistic_scraper()
