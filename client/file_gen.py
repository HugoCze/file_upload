import os
import random
import string
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [FileGenerator] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout,
    force=True
)
logger = logging.getLogger(__name__)

class FileGenerator:
    def __init__(self, output_dir="generated_files"):
        """Initialize FileGenerator with an output directory."""
        self.output_dir = output_dir
        self.extensions = ['.txt', '.pdf', '.doc', '.docx', '.csv', '.dat', '.mp4', '.wav']

        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Initialized FileGenerator with output directory: {output_dir}")
        
    def create_file(self, filename=None, min_size_gb=2, max_size_gb=4):
        """Create a file with random content of specified size range in GB."""
        size_gb = random.uniform(min_size_gb, max_size_gb)
        size_bytes = int(size_gb * 1024 * 1024 * 1024)  
        
        if filename is None:
            timestamp = random.randint(1000000, 9999999)
            extension = random.choice(self.extensions)
            filename = f"file_{timestamp}{extension}"
            
        filepath = os.path.join(self.output_dir, filename)
        
        logger.info(f"Starting creation of {filename} ({size_gb:.2f} GB)")
        sys.stdout.flush()
        
        try:
            with open(filepath, 'wb') as f:
                f.seek(size_bytes - 1)
                f.write(b'\0')
            logger.info(f"Successfully created {filename} ({size_gb:.2f} GB)")
            sys.stdout.flush()
        except Exception as e:
            logger.error(f"Failed to create {filename}: {str(e)}")
            sys.stdout.flush()
            raise
            
        return filepath

    def create_multiple_files(self, num_files, min_size_gb=2, max_size_gb=4):
        """Create multiple files of specified size range."""
        logger.info(f"Starting batch creation of {num_files} files")
        sys.stdout.flush()
        
        created_files = []
        for i in range(num_files):
            logger.info(f"Creating file {i+1}/{num_files}")
            sys.stdout.flush()
            filepath = self.create_file(min_size_gb=min_size_gb, max_size_gb=max_size_gb)
            created_files.append(filepath)
            
        logger.info(f"Completed batch creation of {num_files} files")
        sys.stdout.flush()
        return created_files