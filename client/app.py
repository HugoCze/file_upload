import os
import time
import socket
import requests
from flask import Flask

app = Flask(__name__)

def get_container_id():
    return socket.gethostname()  

@app.route('/trigger-upload')
def trigger_upload():
    container_id = get_container_id()
    api_url = os.getenv('API_URL', 'http://api:5000')
    
    try:
        data = {
            'client_id': container_id,
            'timestamp': time.time()
        }
        
        response = requests.post(f"{api_url}/upload", json=data)
        
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

if __name__ == '__main__':
    print(f"Client container {get_container_id()} starting...")
    app.run(host='0.0.0.0', port=80)