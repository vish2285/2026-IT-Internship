#!/usr/bin/env python3
"""
Script to update README.md with current internship listings.
This script is designed to be run by GitHub Actions.
"""

import os
import sys
import requests
from datetime import datetime
from pathlib import Path

# Add the backend app directory to the Python path
backend_path = Path(__file__).parent.parent / "backend" / "app"
sys.path.insert(0, str(backend_path))

from utils.readme_updater import fetch_internships_from_api, generate_readme_content, update_readme_file

def main():
    """Main function to update README with current internships."""
    print("🚀 Starting README update process...")
    
    # Get API URL from environment variable
    api_url = os.getenv("API_URL", "http://localhost:8000")
    print(f"📡 Fetching data from API: {api_url}")
    
    try:
        # Fetch internships from API
        print("📋 Fetching internships from API...")
        internships = fetch_internships_from_api(api_url)
        
        if not internships:
            print("⚠️  No internships found or API error")
            return False
        
        print(f"✅ Found {len(internships)} internships")
        
        # Generate README content
        print("📝 Generating README content...")
        readme_content = generate_readme_content(internships)
        
        # Update README file
        readme_path = Path(__file__).parent.parent / "README.md"
        print(f"💾 Updating README file: {readme_path}")
        
        success = update_readme_file(readme_content, str(readme_path))
        
        if success:
            print("🎉 README update completed successfully!")
            return True
        else:
            print("❌ README update failed!")
            return False
            
    except Exception as e:
        print(f"💥 Error during README update: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

