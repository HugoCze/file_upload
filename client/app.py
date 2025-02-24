import os
import sys
import time
import socket
import random
import requests
from flask import Flask, jsonify
from logs.logger import logger
from file_gen import FileGenerator
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor


app = Flask(__name__)
file_generator = FileGenerator()

retry_strategy = Retry(
    total=int(os.getenv('MAX_RETRIES', 3)),
    backoff_factor=float(os.getenv('RETRY_BACKOFF', 5)),
    status_forcelist=[429, 500, 502, 503, 504],
)

session = requests.Session()
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

timeout = int(os.getenv('REQUESTS_TIMEOUT', 30))

CHUNK_SIZE = 8 * 1024 * 1024

def get_container_id():
    return socket.gethostname()

def create_and_upload_file():
    container_id = get_container_id()
    api_url = os.getenv('API_URL', 'http://api:8000')
    
    try:
        logger.info(f"[Container {container_id}] Starting file generation...")
        start_time = time.time()
        filepath = file_generator.create_file()
        creation_duration = round(time.time() - start_time, 2)
        file_size = os.path.getsize(filepath)
        creation_time = time.strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"[Container {container_id}] File generated: {filepath} (Size: {file_size} bytes)")
        
        upload_start = time.time()
        logger.info(f"[Container {container_id}] Initializing upload for {filepath}")
        
        init_data = {
            'client_id': container_id,
            'timestamp': str(time.time()),
            'file_creation_time': creation_time,
            'filename': os.path.basename(filepath),
            'total_size': file_size,
            'creation_duration': creation_duration
        }
        
        response = session.post(f"{api_url}/api/uploads/init", json=init_data)
        upload_id = response.json()['upload_id']
        logger.info(f"[Container {container_id}] Upload initialized with ID: {upload_id}")
        
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
        
        logger.info(f"[Container {container_id}] Finalizing upload {upload_id}")
        upload_duration = round(time.time() - upload_start, 2)
        
        response = session.post(
            f"{api_url}/api/uploads/finalize",
            json={
                'upload_id': upload_id,
                'upload_duration': upload_duration,
                'creation_duration': creation_duration
            }
        )
        
        os.remove(filepath)
        logger.info(f"[Container {container_id}] Upload completed in {upload_duration} seconds and file {filepath} removed")
        
        return {
            'status': 'success',
            'container_id': container_id,
            'upload_id': upload_id,
            'upload_duration': upload_duration
        }
        
    except Exception as e:
        logger.error(f"[Container {container_id}] Error during file creation/upload: {str(e)}", exc_info=True)
        return {
            'status': 'error',
            'container_id': container_id,
            'error': str(e)
        }

def trigger_single_container(container_url, container_name, timeout):
    """
    Helper function to trigger upload for a single container
    """
    container_id = get_container_id()
    try:
        response = session.post(container_url, timeout=timeout)
        logger.info(f"[Container {container_id}] Triggered upload on {container_name}")
        return {"status": "success", "container": container_name}
    except Exception as e:
        logger.error(f"[Container {container_id}] Failed to trigger {container_name}")
        return {"status": "failed", "container": container_name}

@app.route('/trigger-all')
def trigger_all_containers():
    """
    Trigger file upload on all containers concurrently using ThreadPoolExecutor
    """
    start_time = time.time()
    try:
        container_id = get_container_id()
        logger.info(f"[Container {container_id}] Initiating uploads across all containers")
        
        project_name = os.getenv('COMPOSE_PROJECT_NAME', 'file_upload')
        container_urls = [
            (f"http://{project_name}-client-{i}:5000/upload", f"client-{i}")
            for i in range(1, 7)  # Assuming 6 containers
        ]
        
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = [
                executor.submit(trigger_single_container, url, name, timeout)
                for url, name in container_urls
            ]
            results = [future.result() for future in futures]

        return jsonify({
            'message': 'All client containers triggered successfully'
        })
        
    except Exception as e:
        total_time = round(time.time() - start_time, 2)
        logger.error(f"[Container {container_id}] Error in trigger_all: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
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

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'container_id': get_container_id()
    })

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