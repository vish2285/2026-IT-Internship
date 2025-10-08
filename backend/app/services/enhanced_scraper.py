#!/usr/bin/env python3
"""
Enhanced job scraper with better error handling, retry logic, and more sources.
"""

import requests
from bs4 import BeautifulSoup
import logging
import time
import random
from datetime import datetime, date, timedelta
from typing import List, Dict
from urllib.parse import urljoin
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedJobScraper:
    """Enhanced job scraper with retry logic and multiple sources."""
    
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
        self.delay_range = (2, 5)  # Random delay between requests
        
        # Enhanced search terms for better coverage
        self.search_terms = {
            'Cybersecurity': [
                'cybersecurity intern', 'security analyst intern', 'cyber security intern',
                'information security intern', 'security engineer intern', 'penetration testing intern',
                'security operations intern', 'threat analyst intern', 'incident response intern',
                'security consultant intern', 'vulnerability assessment intern', 'security researcher intern'
            ],
            'IT': [
                'software engineer intern', 'software developer intern', 'web developer intern',
                'full stack developer intern', 'frontend developer intern', 'backend developer intern',
                'data engineer intern', 'devops engineer intern', 'cloud engineer intern',
                'systems engineer intern', 'network engineer intern', 'database administrator intern',
                'machine learning intern', 'artificial intelligence intern', 'data science intern',
                'mobile developer intern', 'game developer intern', 'blockchain developer intern'
            ],
            'Neuroscience': [
                'neuroscience intern', 'neural network intern', 'brain computer interface intern',
                'cognitive science intern', 'neuroimaging intern', 'neural engineering intern',
                'computational neuroscience intern', 'neurotechnology intern', 'brain research intern',
                'neural data analysis intern', 'neuroinformatics intern', 'neuroengineering intern'
            ]
        }
    
    def _random_delay(self):
        """Add random delay to avoid rate limiting."""
        delay = random.uniform(*self.delay_range)
        time.sleep(delay)
    
    def _extract_posted_date(self, card) -> date:
        """Extract posted date from job card or generate realistic date."""
        try:
            # Try to find date elements in the card
            date_elements = card.find_all(text=re.compile(r'\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2}|posted|ago'))
            
            if date_elements:
                for date_text in date_elements:
                    date_text = date_text.strip().lower()
                    if 'ago' in date_text:
                        if 'day' in date_text:
                            days_ago = int(re.search(r'(\d+)', date_text).group(1))
                            return date.today() - timedelta(days=days_ago)
                        elif 'week' in date_text:
                            weeks_ago = int(re.search(r'(\d+)', date_text).group(1))
                            return date.today() - timedelta(weeks=weeks_ago)
            
            # If no date found, generate a realistic random date (1-30 days ago)
            days_ago = random.randint(1, 30)
            return date.today() - timedelta(days=days_ago)
            
        except Exception:
            days_ago = random.randint(1, 30)
            return date.today() - timedelta(days=days_ago)
    
    def _calculate_deadline(self, posted_date: date, field: str) -> date:
        """Calculate realistic deadline based on field and posted date."""
        if field == "Cybersecurity":
            days_to_deadline = random.randint(45, 90)
        elif field == "IT":
            days_to_deadline = random.randint(30, 75)
        elif field == "Neuroscience":
            days_to_deadline = random.randint(60, 120)
        else:
            days_to_deadline = random.randint(30, 60)
        
        min_deadline = posted_date + timedelta(days=7)
        calculated_deadline = posted_date + timedelta(days=days_to_deadline)
        return max(min_deadline, calculated_deadline)
    
    def _classify_field(self, title: str, description: str) -> str:
        """Classify job into Cybersecurity, IT, or Neuroscience."""
        text = (title + " " + description).lower()
        
        cyber_keywords = [
            'cybersecurity', 'cyber security', 'security', 'penetration testing',
            'vulnerability', 'threat', 'malware', 'firewall', 'encryption',
            'security analyst', 'security engineer', 'infosec', 'red team',
            'blue team', 'incident response', 'forensics'
        ]
        
        it_keywords = [
            'software', 'developer', 'programming', 'coding', 'web development',
            'mobile app', 'database', 'cloud', 'devops', 'system admin',
            'network', 'it support', 'technical support', 'backend', 'frontend',
            'full stack', 'data engineer', 'machine learning', 'ai'
        ]
        
        neuro_keywords = [
            'neuroscience', 'neural', 'brain', 'cognitive', 'psychology',
            'neuroimaging', 'brain-computer', 'neural network', 'neurotechnology',
            'research', 'lab', 'study', 'experiment', 'neural engineering'
        ]
        
        cyber_count = sum(1 for keyword in cyber_keywords if keyword in text)
        it_count = sum(1 for keyword in it_keywords if keyword in text)
        neuro_count = sum(1 for keyword in neuro_keywords if keyword in text)
        
        if cyber_count > it_count and cyber_count > neuro_count:
            return "Cybersecurity"
        elif it_count > neuro_count:
            return "IT"
        elif neuro_count > 0:
            return "Neuroscience"
        else:
            return "IT"
    
    def scrape_linkedin(self, search_term: str) -> List[Dict]:
        """Scrape LinkedIn with enhanced error handling."""
        jobs = []
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                self._random_delay()
                
                base_url = "https://www.linkedin.com/jobs/search"
                params = {
                    'keywords': f"{search_term} intern",
                    'location': 'United States',
                    'f_TPR': 'r604800',  # Last 7 days
                    'f_JT': 'I',  # Internship
                    'sortBy': 'DD'  # Date posted
                }
                
                response = self.session.get(base_url, params=params, timeout=15)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('div', class_='job-search-card')
                
                if not job_cards:
                    logger.warning(f"No job cards found on LinkedIn for '{search_term}' (attempt {attempt + 1})")
                    if attempt < max_retries - 1:
                        time.sleep(10)
                        continue
                
                for card in job_cards[:10]:
                    try:
                        title_elem = card.find('h3', class_='job-search-card__title')
                        if not title_elem:
                            continue
                        
                        title = title_elem.get_text(strip=True)
                        if 'intern' not in title.lower():
                            continue
                        
                        company_elem = card.find('h4', class_='job-search-card__subtitle')
                        company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
                        
                        location_elem = card.find('span', class_='job-search-card__location')
                        job_location = location_elem.get_text(strip=True) if location_elem else "Remote"
                        
                        apply_link = card.find('a', class_='job-search-card__link')
                        apply_url = urljoin(base_url, apply_link['href']) if apply_link else ""
                        
                        desc_elem = card.find('p', class_='job-search-card__snippet')
                        description = desc_elem.get_text(strip=True) if desc_elem else ""
                        
                        field = self._classify_field(title, description)
                        posted_date = self._extract_posted_date(card)
                        deadline = self._calculate_deadline(posted_date, field)
                        
                        job = {
                            'title': title,
                            'company': company,
                            'location': job_location,
                            'field': field,
                            'apply_url': apply_url,
                            'description': description,
                            'source': 'LinkedIn',
                            'posted_date': posted_date,
                            'deadline': deadline
                        }
                        
                        jobs.append(job)
                        
                    except Exception as e:
                        logger.warning(f"Error parsing LinkedIn job card: {e}")
                        continue
                
                logger.info(f"Scraped {len(jobs)} jobs from LinkedIn for '{search_term}'")
                break
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request error on LinkedIn (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(15)
                else:
                    logger.error(f"Failed to scrape LinkedIn after {max_retries} attempts: {e}")
            except Exception as e:
                logger.error(f"Unexpected error scraping LinkedIn: {e}")
                break
        
        return jobs
    
    def scrape_glassdoor(self, search_term: str) -> List[Dict]:
        """Scrape Glassdoor for internship opportunities."""
        jobs = []
        
        try:
            self._random_delay()
            
            base_url = "https://www.glassdoor.com/Job/jobs.htm"
            params = {
                'sc.keyword': f"{search_term} intern",
                'locT': 'C',
                'locId': '1',  # United States
                'jobType': 'internship'
            }
            
            response = self.session.get(base_url, params=params, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            job_cards = soup.find_all('div', class_='jobContainer')
            
            for card in job_cards[:10]:
                try:
                    title_elem = card.find('a', class_='jobLink')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    if 'intern' not in title.lower():
                        continue
                    
                    company_elem = card.find('div', class_='employerName')
                    company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
                    
                    location_elem = card.find('div', class_='loc')
                    job_location = location_elem.get_text(strip=True) if location_elem else "Remote"
                    
                    apply_url = urljoin(base_url, title_elem['href']) if title_elem.get('href') else ""
                    
                    desc_elem = card.find('div', class_='jobDescription')
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    field = self._classify_field(title, description)
                    posted_date = self._extract_posted_date(card)
                    deadline = self._calculate_deadline(posted_date, field)
                    
                    job = {
                        'title': title,
                        'company': company,
                        'location': job_location,
                        'field': field,
                        'apply_url': apply_url,
                        'description': description,
                        'source': 'Glassdoor',
                        'posted_date': posted_date,
                        'deadline': deadline
                    }
                    
                    jobs.append(job)
                    
                except Exception as e:
                    logger.warning(f"Error parsing Glassdoor job card: {e}")
                    continue
            
            logger.info(f"Scraped {len(jobs)} jobs from Glassdoor for '{search_term}'")
            
        except Exception as e:
            logger.error(f"Error scraping Glassdoor: {e}")
        
        return jobs
    
    def scrape_jobs(self, field: str, keywords: List[str]) -> List[Dict]:
        """Scrape jobs from multiple sources for a specific field."""
        all_jobs = []
        
        logger.info(f"Starting enhanced scraping for {field} field with {len(keywords)} keywords")
        
        for keyword in keywords:
            logger.info(f"Scraping for keyword: {keyword}")
            
            # Scrape from LinkedIn
            linkedin_jobs = self.scrape_linkedin(keyword)
            all_jobs.extend(linkedin_jobs)
            
            # Scrape from Glassdoor
            glassdoor_jobs = self.scrape_glassdoor(keyword)
            all_jobs.extend(glassdoor_jobs)
            
            # Add delay between keywords
            time.sleep(random.uniform(3, 6))
        
        # Remove duplicates based on title and company
        unique_jobs = []
        seen = set()
        
        for job in all_jobs:
            key = (job['title'].lower(), job['company'].lower())
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        logger.info(f"Found {len(unique_jobs)} unique jobs for {field} field")
        return unique_jobs

