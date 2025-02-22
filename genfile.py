import os
import random
import string

def generate_large_file(filename, size_gb=2):
    """
    Generate a text file of specified size in GB.
    
    Args:
        filename (str): The name of the file to create
        size_gb (float): Size of the file in gigabytes
    """
    # Convert GB to bytes
    target_size_bytes = size_gb * 1024 * 1024 * 1024
    
    # Create a chunk of random text (100KB per chunk for efficiency)
    chunk_size = 100 * 1024  # 100KB
    
    # Calculate how many chunks we need
    num_chunks = target_size_bytes // chunk_size
    remaining_bytes = target_size_bytes % chunk_size
    
    print(f"Generating a {size_gb}GB text file: {filename}")
    print(f"This will require {num_chunks} chunks of {chunk_size/1024:.0f}KB each")
    
    # Use a set of characters that will generate a text file
    chars = string.ascii_letters + string.digits + ' ' * 10 + '\n' * 2  # More spaces and newlines for readability
    
    # Create a reusable chunk of random text for efficiency
    random_chunk = ''.join(random.choice(chars) for _ in range(chunk_size))
    
    # Write the file
    bytes_written = 0
    with open(filename, 'w', encoding='utf-8') as f:
        for i in range(num_chunks):
            f.write(random_chunk)
            bytes_written += chunk_size
            
            # Print progress every 5% or so
            if i % (num_chunks // 20 or 1) == 0:
                percent = bytes_written / target_size_bytes * 100
                print(f"Progress: {percent:.1f}% ({bytes_written / (1024*1024*1024):.2f}GB written)")
        
        # Write any remaining bytes
        if remaining_bytes > 0:
            f.write(random_chunk[:remaining_bytes])
            bytes_written += remaining_bytes
    
    # Verify the file size
    actual_size = os.path.getsize(filename)
    print(f"File generation complete.")
    print(f"Target size: {target_size_bytes:,} bytes ({size_gb}GB)")
    print(f"Actual size: {actual_size:,} bytes ({actual_size / (1024*1024*1024):.2f}GB)")

if __name__ == "__main__":
    filename = "large_2gb_file.txt"
    generate_large_file(filename, 2)
    print(f"File created: {os.path.abspath(filename)}")