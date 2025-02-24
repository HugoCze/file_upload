import os
import random
import string

class FileGenerator:
    def __init__(self, output_dir="generated_files"):
        """Initialize FileGenerator with an output directory."""
        self.output_dir = output_dir
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
    def generate_random_content(self, size_mb=1):
        """Generate random content of specified size in MB."""
        # Convert MB to bytes (1 MB = 1024 * 1024 bytes)
        size_bytes = size_mb * 1024 * 1024
        # Generate random string content
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(size_bytes))

    def create_file(self, filename=None, size_mb=1):
        """Create a file with random content of specified size."""
        if filename is None:
            # Generate a random filename if none provided
            timestamp = random.randint(1000000, 9999999)
            filename = f"file_{timestamp}.txt"
            
        filepath = os.path.join(self.output_dir, filename)
        
        # Generate and write content
        content = self.generate_random_content(size_mb)
        with open(filepath, 'w') as f:
            f.write(content)
            
        return filepath

    def create_multiple_files(self, num_files, size_mb=1):
        """Create multiple files of specified size."""
        created_files = []
        for _ in range(num_files):
            filepath = self.create_file(size_mb=size_mb)
            created_files.append(filepath)
        return created_files