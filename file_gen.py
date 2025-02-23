import os
import random
import string
import time

def generate_random_string(length=1000):
    """Generate a random string of specified length."""
    return ''.join(random.choices(string.ascii_letters + string.digits + ' \n', k=length))

def create_file(size_gb, filename=None):
    """
    Create a file of specified size in gigabytes.
    
    Args:
        size_gb (int): Size of the file in gigabytes
        filename (str): Optional custom filename
    """
    if filename is None:
        filename = f"{size_gb}GB_file.txt"
    
    # Convert GB to bytes
    target_size = size_gb * 1024 * 1024 * 1024
    chunk_size = 1024 * 1024  # Write 1MB at a time
    
    print(f"Creating {size_gb}GB file: {filename}")
    start_time = time.time()
    
    written_size = 0
    with open(filename, 'w') as f:
        while written_size < target_size:
            # Generate a 1MB chunk of random text
            chunk = generate_random_string(chunk_size)
            chunk_bytes = chunk.encode('utf-8')
            
            # Make sure we don't exceed the target size
            remaining = target_size - written_size
            if len(chunk_bytes) > remaining:
                chunk_bytes = chunk_bytes[:remaining]
            
            f.write(chunk)
            written_size += len(chunk_bytes)
            
            # Print progress
            progress = (written_size / target_size) * 100
            print(f"\rProgress: {progress:.1f}%", end='')
    
    end_time = time.time()
    duration = end_time - start_time
    print(f"\nFile created in {duration:.1f} seconds")

def main():
    # Create 2GB, 4GB, and 8GB files
    sizes = [2, 4, 8]
    
    for size in sizes:
        create_file(size)
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()
