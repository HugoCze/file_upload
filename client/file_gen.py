import os
import random
import string
from tqdm import tqdm
import time

class FileGenerator:
    def __init__(self, output_dir="generated_files"):
        """Initialize FileGenerator with an output directory."""
        self.output_dir = output_dir
        self.extensions = ['.txt', '.pdf', '.doc', '.docx', '.csv', '.dat', '.mp4', '.wav']
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
    def generate_random_content_with_progress(self, size_gb):
        """Generate random content of specified size in GB with progress bar."""
        # Convert GB to bytes (1 GB = 1024 * 1024 * 1024 bytes)
        size_bytes = int(size_gb * 1024 * 1024 * 1024)
        chunk_size = 1024 * 1024  # 1MB chunks for progress bar
        num_chunks = size_bytes // chunk_size
        
        # Create a temporary file to avoid memory issues
        temp_file_path = os.path.join(self.output_dir, "temp_file")
        
        with open(temp_file_path, 'wb') as f:
            with tqdm(total=num_chunks, desc=f"Generating {size_gb}GB file", unit='MB') as pbar:
                for _ in range(num_chunks):
                    # Generate 1MB of random data
                    chunk = ''.join(random.choices(string.ascii_letters + string.digits, k=chunk_size)).encode()
                    f.write(chunk)
                    pbar.update(1)
                    
                # Handle remaining bytes
                remaining_bytes = size_bytes % chunk_size
                if remaining_bytes:
                    chunk = ''.join(random.choices(string.ascii_letters + string.digits, k=remaining_bytes)).encode()
                    f.write(chunk)
        
        return temp_file_path

    def create_file(self, filename=None, min_size_gb=4, max_size_gb=8):
        """Create a file with random content of specified size range in GB."""
        # Generate random size between min_size_gb and max_size_gb
        size_gb = random.uniform(min_size_gb, max_size_gb)
        
        if filename is None:
            # Generate a random filename with random extension
            timestamp = random.randint(1000000, 9999999)
            extension = random.choice(self.extensions)
            filename = f"file_{timestamp}{extension}"
            
        filepath = os.path.join(self.output_dir, filename)
        
        # Generate content with progress bar
        temp_file_path = self.generate_random_content_with_progress(size_gb)
        
        # Rename temp file to final filename
        os.rename(temp_file_path, filepath)
        print(f"\nFile created: {filename} ({size_gb:.2f} GB)")
            
        return filepath

    def create_multiple_files(self, num_files, min_size_gb=4, max_size_gb=8):
        """Create multiple files of specified size range."""
        created_files = []
        for i in range(num_files):
            print(f"\nGenerating file {i+1}/{num_files}")
            filepath = self.create_file(min_size_gb=min_size_gb, max_size_gb=max_size_gb)
            created_files.append(filepath)
        return created_files