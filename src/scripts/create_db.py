import asyncio
import logging
import os
from pathlib import Path

from src.app.core.config import settings
from src.app.core.db.database import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_database_if_not_exists() -> None:
    """Create SQLite database file if it doesn't exist"""
    try:
        # Extract database path from URI
        # Remove sqlite:/// prefix to get the file path
        db_path = settings.DATABASE_URI.replace("sqlite+aiosqlite:///", "")

        # Convert to absolute path if relative
        if not os.path.isabs(db_path):
            db_path = os.path.abspath(db_path)

        # Ensure directory exists
        db_dir = os.path.dirname(db_path)
        os.makedirs(db_dir, exist_ok=True)

        # Create empty database file if it doesn't exist
        if not os.path.exists(db_path):
            Path(db_path).touch()
            logger.info(f"Created database file at: {db_path}")
            logger.info("Will create images table during initialization")
        else:
            logger.info(f"Database file already exists at: {db_path}")

    except Exception as e:
        logger.error(f"Error creating database file: {e}")
        raise

async def init() -> None:
    """Initialize database"""
    try:
        await create_database_if_not_exists()
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

def main() -> None:
    """Main function to run database creation and initialization"""
    try:
        asyncio.run(init())
    except KeyboardInterrupt:
        logger.info("Database initialization interrupted")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

if __name__ == "__main__":
    main()

