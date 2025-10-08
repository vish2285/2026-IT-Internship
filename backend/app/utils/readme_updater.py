import requests
import os
from datetime import datetime
from typing import List, Dict

def fetch_internships_from_api(api_url: str) -> List[Dict]:
    """Fetch internships from the API"""
    try:
        response = requests.get(f"{api_url}/api/v1/internships")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching internships: {e}")
        return []

def generate_readme_content(internships: List[Dict]) -> str:
    """Generate README content with internship listings"""
    
    # Group internships by field
    cybersecurity = [i for i in internships if i['field'] == 'Cybersecurity']
    it = [i for i in internships if i['field'] == 'IT']
    neuroscience = [i for i in internships if i['field'] == 'Neuroscience']
    
    readme_content = f"""# 🧠 Internship Hub - Cybersecurity, IT & Neuroscience

> **Auto-updated on {datetime.now().strftime('%Y-%m-%d at %H:%M UTC')}**

This repository automatically curates and displays internship opportunities in **Cybersecurity**, **IT**, and **Neuroscience** fields. The listings are updated in real-time and sourced from various trusted platforms.

## 📊 Current Statistics

- **Total Active Internships**: {len(internships)}
- **Cybersecurity**: {len(cybersecurity)} opportunities
- **IT**: {len(it)} opportunities  
- **Neuroscience**: {len(neuroscience)} opportunities

## 🔍 How to Use

1. **Browse** the listings below by field
2. **Click "Apply"** to visit the original posting
3. **Filter** by location or field using the web interface
4. **Bookmark** this page for regular updates

## 🌐 Live Web Application

Visit our interactive web application: [Internship Hub](https://your-frontend-url.com)

---

## 🔒 Cybersecurity Internships

| Title | Company | Location | Posted | Deadline | Apply |
|-------|---------|----------|---------|----------|-------|
"""
    
    for internship in cybersecurity:
        posted_date = internship['posted_date']
        deadline = internship['deadline']
        readme_content += f"| {internship['title']} | {internship['company']} | {internship['location']} | {posted_date} | {deadline} | [Apply]({internship['apply_url']}) |\n"
    
    readme_content += f"""
## 💻 IT Internships

| Title | Company | Location | Posted | Deadline | Apply |
|-------|---------|----------|---------|----------|-------|
"""
    
    for internship in it:
        posted_date = internship['posted_date']
        deadline = internship['deadline']
        readme_content += f"| {internship['title']} | {internship['company']} | {internship['location']} | {posted_date} | {deadline} | [Apply]({internship['apply_url']}) |\n"
    
    readme_content += f"""
## 🧠 Neuroscience Internships

| Title | Company | Location | Posted | Deadline | Apply |
|-------|---------|----------|---------|----------|-------|
"""
    
    for internship in neuroscience:
        posted_date = internship['posted_date']
        deadline = internship['deadline']
        readme_content += f"| {internship['title']} | {internship['company']} | {internship['location']} | {posted_date} | {deadline} | [Apply]({internship['apply_url']}) |\n"
    
    readme_content += f"""
---

## 🔄 Auto-Update Information

This README is automatically updated every 6 hours via GitHub Actions. The system:

- ✅ Fetches new internships from our database
- ✅ Removes expired or inactive listings  
- ✅ Updates statistics and counts
- ✅ Maintains consistent formatting

## 🤝 Contributing

To add new internship opportunities:

1. **Web Interface**: Use our [admin panel](https://your-frontend-url.com/admin)
2. **API**: Submit via our REST API endpoints
3. **Email**: Send listings to internships@yourdomain.com

## 📱 Features

- 🔍 **Smart Filtering**: Filter by field, location, or company
- 📅 **Deadline Tracking**: See application deadlines
- 🔔 **Notifications**: Get alerts for new opportunities
- 📊 **Analytics**: Track application success rates
- 🌍 **Global Coverage**: Opportunities from around the world

## 🛠️ Technical Stack

- **Frontend**: React with Vite
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **Deployment**: Vercel + Railway
- **Automation**: GitHub Actions

---

*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}*
"""
    
    return readme_content

def update_readme_file(readme_content: str, file_path: str = "README.md"):
    """Update the README file with new content"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"README updated successfully at {file_path}")
        return True
    except Exception as e:
        print(f"Error updating README: {e}")
        return False

def main():
    """Main function to update README"""
    api_url = os.getenv("API_URL", "http://localhost:8000")
    
    print("Fetching internships from API...")
    internships = fetch_internships_from_api(api_url)
    
    if not internships:
        print("No internships found or API error")
        return False
    
    print(f"Found {len(internships)} internships")
    
    print("Generating README content...")
    readme_content = generate_readme_content(internships)
    
    print("Updating README file...")
    success = update_readme_file(readme_content)
    
    if success:
        print("README update completed successfully!")
    else:
        print("README update failed!")
    
    return success

if __name__ == "__main__":
    main()
