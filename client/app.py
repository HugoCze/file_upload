import os
import time
import socket
import requests
from flask import Flask, jsonify
import threading
import random
from file_gen import FileGenerator

app = Flask(__name__)
file_generator = FileGenerator()


def get_container_id():
    return socket.gethostname()


def perform_upload():
    container_id = get_container_id()
    api_url = os.getenv('API_URL', 'http://api:8000')
    
    try:
        creation_start = time.time()
        filepath = file_generator.create_file(size_mb=1)
        creation_duration = round(time.time() - creation_start, 2)
        creation_time = time.strftime("%Y-%m-%d %H:%M:%S")
        
        files = {
            'file': open(filepath, 'rb')
        }
        data = {
            'client_id': container_id,
            'timestamp': str(time.time()),
            'file_creation_time': creation_time,
            'creation_duration': creation_duration
        }
        
        response = requests.post(
            f"{api_url}/api/uploads/", 
            files=files,
            data=data
        )
        
        # Close and clean up the file
        files['file'].close()
        os.remove(filepath)
        
        print(f"Container {container_id} sent request. Response: {response.status_code}")
        return {
            'status': 'success',
            'container_id': container_id,
            'response': response.json()
        }
    except Exception as e:
        print(f"Container {container_id} error: {str(e)}")
        return {
            'status': 'error',
            'container_id': container_id,
            'error': str(e)
        }


@app.route('/trigger-upload')
def trigger_upload():
    return perform_upload()


@app.route('/trigger-all')
def trigger_all_containers():
    try:
        ips = socket.getaddrinfo('client', 5000, socket.AF_INET, socket.SOCK_STREAM)
        
        def trigger_container(ip):
            try:
                time.sleep(0.1 * random.random()) 
                container_url = f"http://{ip[4][0]}:5000/trigger-upload"
                response = requests.get(container_url, params={'client_id': get_container_id()})
                print(f"Triggered upload on {ip[4][0]}: {response.status_code}")
            except Exception as e:
                print(f"Error triggering container at {ip[4][0]}: {str(e)}")

        threads = []
        for ip in ips:
            thread = threading.Thread(target=trigger_container, args=(ip,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        return jsonify({
            'status': 'success',
            'message': f'Triggered upload on {len(ips)} containers',
            'container_id': get_container_id(),
            'triggered_count': len(ips)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error triggering containers: {str(e)}',
            'container_id': get_container_id()
        }), 500

if __name__ == '__main__':
    print(f"Client container {get_container_id()} starting...")
    app.run(host='0.0.0.0', port=5000)