import os
import pytest
import requests
from typing import Generator
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

@pytest.fixture
def api_url() -> str:
    return os.getenv('API_URL', 'http://localhost:8000')

@pytest.fixture
def client_url() -> str:
    return os.getenv('CLIENT_URL', 'http://localhost:5000')

@pytest.fixture
def session() -> Generator[requests.Session, None, None]:

    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    yield session
    session.close()


def test_api_health(session: requests.Session, api_url: str):

    response = session.get(f"{api_url}/api/health/")
    assert response.status_code == 200
    assert response.json()['status'] == 'healthy'


def test_client_health(session: requests.Session, client_url: str):

    response = session.get(f"{client_url}/health")
    assert response.status_code == 200
    assert response.json()['status'] == 'healthy'


def test_file_extensions(session: requests.Session, api_url: str):

    allowed_files = {
        'test.txt': True,
        'document.pdf': True,
        'file.doc': True,
        'data.csv': True,
        'audio.wav': True,
        'video.mp4': True,
        'document.docx': True,
        'data.dat': True
    }

    disallowed_files = {
        'script.py': False,
        'image.jpg': False,
        'file.exe': False,
        'document.zip': False
    }

    for filename, should_allow in {**allowed_files, **disallowed_files}.items():
        response = session.post(
            f"{api_url}/api/health/check-extension/",
            json={"filename": filename}
        )
        
        assert response.status_code == 200
        result = response.json()
        
        if should_allow:
            assert result['allowed'] is True, f"Extension for {filename} should be allowed"
        else:
            assert result['allowed'] is False, f"Extension for {filename} should not be allowed"


def test_api_data_endpoint_structure(session: requests.Session, api_url: str):
    response = session.get(f"{api_url}/api/data/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_api_data_file_schema(session: requests.Session, api_url: str):
    response = session.get(f"{api_url}/api/data/")
    files = response.json()
    if not files:
        pytest.skip("No files to test schema")
    for file in files:
        assert 'filename' in file
        assert 'size' in file
        assert 'storage_location' in file
        assert 'upload_date' in file
        assert 'upload_duration' in file
        assert 'file_creation_time' in file
        assert 'status' in file
        assert 'client_id' in file
        assert isinstance(file['filename'], str)
        assert isinstance(file['size'], int)
        assert isinstance(file['storage_location'], str)
        assert isinstance(file['upload_date'], str)
        assert isinstance(file['upload_duration'], float)
        assert isinstance(file['file_creation_time'], str)
        assert isinstance(file['status'], str)



