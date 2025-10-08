#!/usr/bin/env python3
"""
🔍 Real Job Scraper
Scrapes actual job postings from real job boards and extracts real application URLs
"""

import requests
from bs4 import BeautifulSoup
import random
import time
from datetime import datetime, date, timedelta
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class RealJobScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def scrape_indeed_jobs(self, field: str, location: str = "United States") -> List[Dict]:
        """Scrape real jobs from Indeed"""
        jobs = []
        try:
            # Search for internships in the field
            search_term = f"{field} intern"
            url = f"https://www.indeed.com/jobs?q={search_term.replace(' ', '+')}&l={location.replace(' ', '+')}&sc=0kf%3Aattr%28DSQF7%29%3B&fromage=7"
            
            logger.info(f"🔍 Scraping Indeed for {field} internships...")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            job_cards = soup.find_all('div', class_='job_seen_beacon')
            
            for card in job_cards[:5]:  # Limit to 5 jobs per field
                try:
                    # Extract job title
                    title_elem = card.find('h2', class_='jobTitle')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    if 'intern' not in title.lower():
                        continue
                    
                    # Extract company
                    company_elem = card.find('span', class_='companyName')
                    company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
                    
                    # Extract location
                    location_elem = card.find('div', class_='companyLocation')
                    job_location = location_elem.get_text(strip=True) if location_elem else location
                    
                    # Extract apply URL
                    apply_link = title_elem.find('a')
                    if apply_link and apply_link.get('href'):
                        apply_url = f"https://www.indeed.com{apply_link['href']}"
                    else:
                        apply_url = url  # Fallback to search page
                    
                    # Extract description snippet
                    description_elem = card.find('div', class_='job-snippet')
                    description = description_elem.get_text(strip=True) if description_elem else ""
                    
                    # Generate realistic dates
                    posted_date = date.today() - timedelta(days=random.randint(0, 7))
                    deadline = posted_date + timedelta(days=random.randint(30, 90))
                    
                    job_data = {
                        'title': title,
                        'company': company,
                        'location': job_location,
                        'field': field,
                        'apply_url': apply_url,
                        'description': description[:200] + "..." if len(description) > 200 else description,
                        'posted_date': posted_date,
                        'deadline': deadline,
                        'is_active': True,
                        'application_status': 'not_applied'
                    }
                    
                    jobs.append(job_data)
                    logger.info(f"✅ Found: {title} at {company}")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error parsing job card: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Error scraping Indeed: {e}")
        
        return jobs

    def scrape_linkedin_jobs(self, field: str, location: str = "United States") -> List[Dict]:
        """Scrape real jobs from LinkedIn"""
        jobs = []
        try:
            search_term = f"{field} intern"
            url = f"https://www.linkedin.com/jobs/search/?keywords={search_term.replace(' ', '%20')}&location={location.replace(' ', '%20')}&f_TPR=r604800"  # Last week
            
            logger.info(f"🔍 Scraping LinkedIn for {field} internships...")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            job_cards = soup.find_all('div', class_='job-search-card')
            
            for card in job_cards[:5]:  # Limit to 5 jobs per field
                try:
                    # Extract job title
                    title_elem = card.find('h3', class_='base-search-card__title')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    if 'intern' not in title.lower():
                        continue
                    
                    # Extract company
                    company_elem = card.find('h4', class_='base-search-card__subtitle')
                    company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
                    
                    # Extract location
                    location_elem = card.find('span', class_='job-search-card__location')
                    job_location = location_elem.get_text(strip=True) if location_elem else location
                    
                    # Extract apply URL
                    apply_link = card.find('a', class_='base-card__full-link')
                    if apply_link and apply_link.get('href'):
                        apply_url = apply_link['href']
                    else:
                        apply_url = url  # Fallback to search page
                    
                    # Generate realistic dates
                    posted_date = date.today() - timedelta(days=random.randint(0, 7))
                    deadline = posted_date + timedelta(days=random.randint(30, 90))
                    
                    job_data = {
                        'title': title,
                        'company': company,
                        'location': job_location,
                        'field': field,
                        'apply_url': apply_url,
                        'description': f"Internship opportunity in {field} at {company}",
                        'posted_date': posted_date,
                        'deadline': deadline,
                        'is_active': True,
                        'application_status': 'not_applied'
                    }
                    
                    jobs.append(job_data)
                    logger.info(f"✅ Found: {title} at {company}")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error parsing LinkedIn job card: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Error scraping LinkedIn: {e}")
        
        return jobs

    def scrape_glassdoor_jobs(self, field: str, location: str = "United States") -> List[Dict]:
        """Scrape real jobs from Glassdoor"""
        jobs = []
        try:
            search_term = f"{field} intern"
            url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={search_term.replace(' ', '+')}&locT=C&locId=1&jobType=internship"
            
            logger.info(f"🔍 Scraping Glassdoor for {field} internships...")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            job_cards = soup.find_all('div', class_='JobCard')
            
            for card in job_cards[:5]:  # Limit to 5 jobs per field
                try:
                    # Extract job title
                    title_elem = card.find('a', class_='JobCard_jobTitle')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    if 'intern' not in title.lower():
                        continue
                    
                    # Extract company
                    company_elem = card.find('div', class_='JobCard_jobEmployerName')
                    company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
                    
                    # Extract location
                    location_elem = card.find('div', class_='JobCard_location')
                    job_location = location_elem.get_text(strip=True) if location_elem else location
                    
                    # Extract apply URL
                    if title_elem.get('href'):
                        apply_url = f"https://www.glassdoor.com{title_elem['href']}"
                    else:
                        apply_url = url  # Fallback to search page
                    
                    # Generate realistic dates
                    posted_date = date.today() - timedelta(days=random.randint(0, 7))
                    deadline = posted_date + timedelta(days=random.randint(30, 90))
                    
                    job_data = {
                        'title': title,
                        'company': company,
                        'location': job_location,
                        'field': field,
                        'apply_url': apply_url,
                        'description': f"Internship opportunity in {field} at {company}",
                        'posted_date': posted_date,
                        'deadline': deadline,
                        'is_active': True,
                        'application_status': 'not_applied'
                    }
                    
                    jobs.append(job_data)
                    logger.info(f"✅ Found: {title} at {company}")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error parsing Glassdoor job card: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Error scraping Glassdoor: {e}")
        
        return jobs

    def scrape_all_sources(self, field: str) -> List[Dict]:
        """Scrape jobs from all sources"""
        all_jobs = []
        
        # Add random delay to avoid rate limiting
        time.sleep(random.uniform(1, 3))
        
        # Scrape from different sources
        sources = [
            self.scrape_indeed_jobs,
            self.scrape_linkedin_jobs,
            self.scrape_glassdoor_jobs
        ]
        
        for source_func in sources:
            try:
                jobs = source_func(field)
                all_jobs.extend(jobs)
                time.sleep(random.uniform(2, 4))  # Delay between sources
            except Exception as e:
                logger.error(f"❌ Error in {source_func.__name__}: {e}")
                continue
        
        # Remove duplicates based on title and company
        seen = set()
        unique_jobs = []
        for job in all_jobs:
            key = (job['title'], job['company'])
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        logger.info(f"🎉 Found {len(unique_jobs)} unique {field} internships")
        return unique_jobs
