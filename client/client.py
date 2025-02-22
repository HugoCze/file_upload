import os
import asyncio
import logging
from app.client import upload_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main() -> None:
    """Main entry point for the client application."""
    try:
        # Run the file upload client
        await upload_client.run()
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())