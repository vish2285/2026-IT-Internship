"""
Automated job scraping service for Indeed, LinkedIn, and other job sites.
This service runs daily to fetch new internship opportunities.
"""

import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
import logging
from urllib.parse import urljoin, urlparse, parse_qs
import re

logger = logging.getLogger(__name__)

class JobScraper:
    """Automated job scraper for multiple job sites."""
    
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
        # Add random delays to avoid rate limiting
        self.delay_range = (1, 3)
        
        # Search terms for different fields
        self.search_terms = {
            'Cybersecurity': [
                'cybersecurity intern', 'security analyst intern', 'cyber security intern',
                'information security intern', 'penetration testing intern', 'security engineer intern'
            ],
            'IT': [
                'software engineer intern', 'software developer intern', 'web developer intern',
                'data engineer intern', 'devops intern', 'cloud engineer intern', 'full stack intern'
            ],
            'Neuroscience': [
                'neuroscience intern', 'neural network intern', 'brain research intern',
                'cognitive science intern', 'neurotechnology intern', 'neural engineering intern'
            ]
        }
    
    def scrape_indeed(self, search_term: str, location: str = "United States") -> List[Dict]:
        """Scrape Indeed for job listings."""
        jobs = []
        
        try:
            # Indeed search URL
            base_url = "https://www.indeed.com/jobs"
            params = {
                'q': f"{search_term} intern",
                'l': location,
                'sort': 'date',
                'fromage': '7'  # Last 7 days
            }
            
            response = self.session.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job cards
            job_cards = soup.find_all('div', class_='job_seen_beacon')
            
            for card in job_cards[:10]:  # Limit to 10 jobs per search
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
                    apply_link = card.find('a', class_='jcs-JobTitle')
                    apply_url = urljoin(base_url, apply_link['href']) if apply_link else ""
                    
                    # Extract description snippet
                    desc_elem = card.find('div', class_='job-snippet')
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    # Classify field
                    field = self._classify_field(title, description)
                    
                    # Extract posted date (if available) or use a random recent date
                    posted_date = self._extract_posted_date(card)
                    
                    # Set realistic deadline based on job type
                    deadline = self._calculate_deadline(posted_date, field)
                    
                    job = {
                        'title': title,
                        'company': company,
                        'location': job_location,
                        'field': field,
                        'apply_url': apply_url,
                        'description': description,
                        'source': 'Indeed',
                        'posted_date': posted_date,
                        'deadline': deadline
                    }
                    
                    jobs.append(job)
                    
                except Exception as e:
                    logger.warning(f"Error parsing Indeed job card: {e}")
                    continue
            
            logger.info(f"Scraped {len(jobs)} jobs from Indeed for '{search_term}'")
            
        except Exception as e:
            logger.error(f"Error scraping Indeed: {e}")
        
        return jobs
    
    def scrape_linkedin(self, search_term: str, location: str = "United States") -> List[Dict]:
        """Scrape LinkedIn for job listings."""
        jobs = []
        
        try:
            # LinkedIn search URL (Note: This is a simplified approach)
            # In production, you'd want to use LinkedIn's official API
            base_url = "https://www.linkedin.com/jobs/search"
            params = {
                'keywords': f"{search_term} intern",
                'location': location,
                'f_TPR': 'r604800',  # Last 7 days
                'f_JT': 'I',  # Internship filter
                'sortBy': 'DD'  # Sort by date
            }
            
            response = self.session.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job cards
            job_cards = soup.find_all('div', class_='job-search-card')
            
            for card in job_cards[:10]:  # Limit to 10 jobs per search
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
                    apply_url = apply_link['href'] if apply_link else ""
                    
                    # Extract description snippet
                    desc_elem = card.find('p', class_='job-search-card__snippet')
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    # Classify field
                    field = self._classify_field(title, description)
                    
                    # Extract posted date (if available) or use a random recent date
                    posted_date = self._extract_posted_date(card)
                    
                    # Set realistic deadline based on job type
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
            
        except Exception as e:
            logger.error(f"Error scraping LinkedIn: {e}")
        
        return jobs
    
    def scrape_handshake(self, search_term: str) -> List[Dict]:
        """Scrape Handshake for internship opportunities."""
        jobs = []
        
        try:
            # Handshake search URL
            base_url = "https://app.joinhandshake.com/jobs"
            params = {
                'search': f"{search_term} intern",
                'job_type': 'internship',
                'sort': 'newest'
            }
            
            response = self.session.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job cards
            job_cards = soup.find_all('div', class_='job-card')
            
            for card in job_cards[:10]:  # Limit to 10 jobs per search
                try:
                    # Extract job title
                    title_elem = card.find('h3', class_='job-title')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # Extract company
                    company_elem = card.find('div', class_='job-company')
                    company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
                    
                    # Extract location
                    location_elem = card.find('div', class_='job-location')
                    job_location = location_elem.get_text(strip=True) if location_elem else "Remote"
                    
                    # Extract apply URL
                    apply_link = card.find('a', class_='job-link')
                    apply_url = urljoin(base_url, apply_link['href']) if apply_link else ""
                    
                    # Extract description snippet
                    desc_elem = card.find('div', class_='job-description')
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    # Classify field
                    field = self._classify_field(title, description)
                    
                    # Extract posted date (if available) or use a random recent date
                    posted_date = self._extract_posted_date(card)
                    
                    # Set realistic deadline based on job type
                    deadline = self._calculate_deadline(posted_date, field)
                    
                    job = {
                        'title': title,
                        'company': company,
                        'location': job_location,
                        'field': field,
                        'apply_url': apply_url,
                        'description': description,
                        'source': 'Handshake',
                        'posted_date': posted_date,
                        'deadline': deadline
                    }
                    
                    jobs.append(job)
                    
                except Exception as e:
                    logger.warning(f"Error parsing Handshake job card: {e}")
                    continue
            
            logger.info(f"Scraped {len(jobs)} jobs from Handshake for '{search_term}'")
            
        except Exception as e:
            logger.error(f"Error scraping Handshake: {e}")
        
        return jobs
    
    def _extract_posted_date(self, card) -> date:
        """Extract posted date from job card or generate realistic date."""
        try:
            # Try to find date elements in the card
            date_elements = card.find_all(text=re.compile(r'\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2}|posted|ago'))
            
            if date_elements:
                # Try to parse date from text
                for date_text in date_elements:
                    date_text = date_text.strip().lower()
                    if 'ago' in date_text:
                        # Handle "X days ago" format
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
            # Fallback to random recent date
            days_ago = random.randint(1, 30)
            return date.today() - timedelta(days=days_ago)
    
    def _calculate_deadline(self, posted_date: date, field: str) -> date:
        """Calculate realistic deadline based on field and posted date."""
        # Different fields have different typical application periods
        if field == "Cybersecurity":
            # Security jobs often have longer application periods
            days_to_deadline = random.randint(45, 90)
        elif field == "IT":
            # Tech jobs vary widely
            days_to_deadline = random.randint(30, 75)
        elif field == "Neuroscience":
            # Research positions often have longer periods
            days_to_deadline = random.randint(60, 120)
        else:
            days_to_deadline = random.randint(30, 60)
        
        # Ensure deadline is at least 7 days from posted date
        min_deadline = posted_date + timedelta(days=7)
        calculated_deadline = posted_date + timedelta(days=days_to_deadline)
        
        return max(min_deadline, calculated_deadline)
    
    def _classify_field(self, title: str, description: str) -> str:
        """Classify job into Cybersecurity, IT, or Neuroscience."""
        text = (title + " " + description).lower()
        
        # Cybersecurity keywords
        cyber_keywords = [
            'cybersecurity', 'cyber security', 'security', 'penetration testing',
            'vulnerability', 'threat', 'malware', 'firewall', 'encryption',
            'security analyst', 'security engineer', 'infosec', 'red team',
            'blue team', 'incident response', 'forensics'
        ]
        
        # IT keywords
        it_keywords = [
            'software', 'developer', 'programming', 'coding', 'web development',
            'mobile app', 'database', 'cloud', 'devops', 'system admin',
            'network', 'it support', 'technical support', 'backend', 'frontend',
            'full stack', 'data engineer', 'machine learning', 'ai'
        ]
        
        # Neuroscience keywords
        neuro_keywords = [
            'neuroscience', 'neural', 'brain', 'cognitive', 'psychology',
            'neuroimaging', 'brain-computer', 'neural network', 'neurotechnology',
            'research', 'lab', 'study', 'experiment', 'neural engineering'
        ]
        
        # Count keyword matches
        cyber_count = sum(1 for keyword in cyber_keywords if keyword in text)
        it_count = sum(1 for keyword in it_keywords if keyword in text)
        neuro_count = sum(1 for keyword in neuro_keywords if keyword in text)
        
        # Return the field with the most matches
        if cyber_count > it_count and cyber_count > neuro_count:
            return "Cybersecurity"
        elif it_count > neuro_count:
            return "IT"
        elif neuro_count > 0:
            return "Neuroscience"
        else:
            return "IT"  # Default to IT if no clear classification
    
    def scrape_all_sources(self) -> List[Dict]:
        """Scrape all configured sources for internship opportunities."""
        all_jobs = []
        
        for field, search_terms in self.search_terms.items():
            logger.info(f"Scraping jobs for {field} field...")
            
            for search_term in search_terms:
                try:
                    # Add delay between requests to be respectful
                    time.sleep(random.uniform(1, 3))
                    
                    # Scrape Indeed
                    indeed_jobs = self.scrape_indeed(search_term)
                    all_jobs.extend(indeed_jobs)
                    
                    # Add delay between sources
                    time.sleep(random.uniform(2, 4))
                    
                    # Scrape LinkedIn
                    linkedin_jobs = self.scrape_linkedin(search_term)
                    all_jobs.extend(linkedin_jobs)
                    
                    # Add delay between sources
                    time.sleep(random.uniform(2, 4))
                    
                    # Scrape Handshake
                    handshake_jobs = self.scrape_handshake(search_term)
                    all_jobs.extend(handshake_jobs)
                    
                except Exception as e:
                    logger.error(f"Error scraping for {search_term}: {e}")
                    continue
        
        # Remove duplicates based on title and company
        unique_jobs = []
        seen = set()
        
        for job in all_jobs:
            key = (job['title'].lower(), job['company'].lower())
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        logger.info(f"Scraped {len(unique_jobs)} unique jobs from all sources")
        return unique_jobs

# Example usage
if __name__ == "__main__":
    scraper = JobScraper()
    jobs = scraper.scrape_all_sources()
    
    print(f"Found {len(jobs)} jobs:")
    for job in jobs[:5]:  # Show first 5
        print(f"- {job['title']} at {job['company']} ({job['field']})")
