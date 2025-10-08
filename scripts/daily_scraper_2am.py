#!/usr/bin/env python3
"""
🔄 Fresh Internship Scraper (Every 2 Hours)
Runs the enhanced scraper every 2 hours to keep internships fresh
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add the backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_scraper_2am.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main function to run scraper every 2 hours"""
    logger.info("🔄 Starting Fresh Internship Scraper (Every 2 Hours)")
    logger.info("=" * 60)
    
    try:
        # Load environment variables
        load_dotenv()
        
        # Set database URL if not already set
        if not os.getenv('DATABASE_URL'):
            os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_l7zw0VaudiRo@ep-dark-truth-adri72k9-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
        
        # Run the enhanced daily scraper
        logger.info("🤖 Running Enhanced Daily Scraper...")
        from enhanced_daily_scraper import run_enhanced_scraper
        run_enhanced_scraper()
        
        # Update the README
        logger.info("📝 Updating README with latest internships...")
        from update_readme import main as update_readme_main
        update_readme_main()
        
        logger.info("✅ Fresh internship scraper completed successfully!")
        logger.info(f"🕐 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
    except Exception as e:
        logger.error(f"❌ Error in daily scraper: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
