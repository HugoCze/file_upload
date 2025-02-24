import os
import time
import socket
import requests
from flask import Flask, jsonify
import random
from file_gen import FileGenerator
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    force=True
)
logger = logging.getLogger('ClientApp')

app = Flask(__name__)
file_generator = FileGenerator()

# Configure retry strategy
retry_strategy = Retry(
    total=int(os.getenv('MAX_RETRIES', 3)),
    backoff_factor=float(os.getenv('RETRY_BACKOFF', 5)),
    status_forcelist=[429, 500, 502, 503, 504],
)

session = requests.Session()
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

# Use the session for requests with timeout
timeout = int(os.getenv('REQUESTS_TIMEOUT', 30))

CHUNK_SIZE = 8 * 1024 * 1024  # 8MB chunks

def get_container_id():
    return socket.gethostname()

def create_and_upload_file():
    container_id = get_container_id()
    api_url = os.getenv('API_URL', 'http://api:8000')
    
    try:
        # Create file
        logger.info(f"[Container {container_id}] Starting file generation...")
        creation_start = time.time()
        filepath = file_generator.create_file()
        creation_duration = round(time.time() - creation_start, 2)
        creation_time = time.strftime("%Y-%m-%d %H:%M:%S")
        file_size = os.path.getsize(filepath)
        logger.info(f"[Container {container_id}] File generated: {filepath} (Size: {file_size} bytes) in {creation_duration} seconds")
        
        # Upload file in chunks
        logger.info(f"[Container {container_id}] Initializing upload for {filepath}")
        
        # Initialize upload
        init_data = {
            'client_id': container_id,
            'timestamp': str(time.time()),
            'file_creation_time': creation_time,
            'creation_duration': creation_duration,
            'filename': os.path.basename(filepath),
            'total_size': file_size
        }
        
        response = session.post(f"{api_url}/api/uploads/init", json=init_data)
        upload_id = response.json()['upload_id']
        logger.info(f"[Container {container_id}] Upload initialized with ID: {upload_id}")
        
        # Upload chunks
        with open(filepath, 'rb') as f:
            chunk_number = 0
            while chunk := f.read(CHUNK_SIZE):
                files = {'chunk': chunk}
                data = {
                    'chunk_number': chunk_number,
                    'upload_id': upload_id
                }
                session.post(f"{api_url}/api/uploads/chunk", files=files, data=data)
                logger.info(f"[Container {container_id}] Uploaded chunk {chunk_number} for upload {upload_id}")
                chunk_number += 1
        
        # Finalize upload
        logger.info(f"[Container {container_id}] Finalizing upload {upload_id}")
        response = session.post(
            f"{api_url}/api/uploads/finalize",
            json={'upload_id': upload_id}
        )
        
        # Clean up
        os.remove(filepath)
        logger.info(f"[Container {container_id}] Upload completed and file {filepath} removed")
        
        return {
            'status': 'success',
            'container_id': container_id,
            'upload_id': upload_id
        }
        
    except Exception as e:
        logger.error(f"[Container {container_id}] Error during file creation/upload: {str(e)}", exc_info=True)
        return {
            'status': 'error',
            'container_id': container_id,
            'error': str(e)
        }

@app.route('/trigger-all')
def trigger_all_containers():
    """
    Trigger file upload on all containers by making requests to each container
    """
    try:
        container_id = get_container_id()
        logger.info(f"[Container {container_id}] Initiating uploads across all containers")
        
        # Get list of all client containers
        all_results = []
        project_name = os.getenv('COMPOSE_PROJECT_NAME', 'file_upload')
        for i in range(1, 7):  # Assuming 6 containers
            container_url = f"http://{project_name}-client-{i}:5000/upload"
            try:
                response = session.post(container_url, timeout=timeout)
                all_results.append(response.json())
                logger.info(f"[Container {container_id}] Triggered upload on {project_name}-client-{i}")
            except Exception as e:
                logger.error(f"[Container {container_id}] Failed to trigger {project_name}-client-{i}: {str(e)}")
                all_results.append({
                    "status": "error", 
                    "container": f"{project_name}-client-{i}", 
                    "error": str(e)
                })

        return jsonify({
            'status': 'success',
            'message': 'All containers triggered',
            'container_id': container_id,
            'results': all_results
        })
        
    except Exception as e:
        logger.error(f"[Container {container_id}] Error in trigger_all: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e),
            'container_id': get_container_id()
        }), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handle single file upload request
    """
    try:
        result = create_and_upload_file()
        return jsonify(result)
    except Exception as e:
        logger.error(f"[Container {get_container_id()}] Error in upload: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e),
            'container_id': get_container_id()
        }), 500

if __name__ == '__main__':
    container_id = get_container_id()
    logger.info(f"Client container {container_id} starting...")
    
    # Log container network info
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        logger.info(f"Container network info - Hostname: {hostname}, IP: {ip_address}")
    except Exception as e:
        logger.error(f"Failed to get network info: {str(e)}")
    
    # Verify port is available
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(('0.0.0.0', 5000))
        sock.close()
        logger.info("Port 5000 is available")
    except socket.error as e:
        logger.error(f"Port 5000 is not available: {str(e)}")
        sys.exit(1)
    
    startup_delay = random.uniform(1, 5)
    logger.info(f"Waiting {startup_delay:.2f} seconds before starting...")
    time.sleep(startup_delay)
    
    try:
        app.run(host='0.0.0.0', port=5000)
    except Exception as e:
        logger.error(f"Failed to start Flask app: {str(e)}", exc_info=True)
        sys.exit(1)