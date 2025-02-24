import os
import sys
import random
from logs.logger import logger




class FileGenerator:
    def __init__(self, output_dir="generated_files"):
        self.output_dir = output_dir
        self.extensions = ['.txt', '.pdf', '.doc', '.docx', '.csv', '.dat', '.mp4', '.wav']

        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Initialized FileGenerator with output directory: {output_dir}")
        
    def create_file(self, filename=None, min_size_gb=7, max_size_gb=8):
        size_gb = random.uniform(min_size_gb, max_size_gb)
        size_bytes = int(size_gb * 1024 * 1024 * 1024)  
        
        if filename is None:
            timestamp = random.randint(1000000, 9999999)
            extension = random.choice(self.extensions)
            filename = f"file_{timestamp}__{extension}"
            
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

    def create_multiple_files(self, num_files, min_size_gb=4, max_size_gb=8):
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