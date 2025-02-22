import os
import json
import pytest
import tempfile
import shutil
from fastapi.testclient import TestClient
from main import app
from app.core.config import settings

client = TestClient(app)

@pytest.fixture(scope="module")
def test_app():
    """Create a test client with temporary upload folder."""
    # Create a temporary directory for uploads
    test_upload_dir = tempfile.mkdtemp()
    
    # Override settings
    original_upload_folder = settings.UPLOAD_FOLDER
    settings.UPLOAD_FOLDER = test_upload_dir
    
    # Create metadata.json
    os.makedirs(test_upload_dir, exist_ok=True)
    with open(os.path.join(test_upload_dir, 'metadata.json'), 'w') as f:
        json.dump([], f)
    
    yield client
    
    # Clean up after tests
    shutil.rmtree(test_upload_dir)
    # Restore original settings
    settings.UPLOAD_FOLDER = original_upload_folder

def test_health_check(test_app):
    """Test the health check endpoint."""
    response = test_app.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_upload_no_file(test_app):
    """Test upload endpoint with no file."""
    response = test_app.post("/api/v1/upload")
    assert response.status_code in [400, 422]  # FastAPI validation error

def test_upload_empty_file(test_app):
    """Test upload endpoint with empty file."""
    response = test_app.post(
        "/api/v1/upload",
        files={"file": ("", "")}
    )
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "No file selected"

def test_upload_invalid_extension(test_app):
    """Test upload endpoint with invalid file extension."""
    response = test_app.post(
        "/api/v1/upload",
        files={"file": ("test.invalid", b"test content")}
    )
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "File type not allowed"

def test_upload_valid_file(test_app):
    """Test upload endpoint with valid file."""
    # Create test file content
    file_content = b"Test file content"
    
    # Add metadata
    location = "test/location"
    description = "Test file description"
    
    # Upload the file
    response = test_app.post(
        "/api/v1/upload",
        files={"file": ("test.txt", file_content)},
        data={"location": location, "description": description}
    )
    
    # Check the response
    assert response.status_code == 201
    data = response.json()
    assert "message" in data
    assert data["message"] == "File uploaded successfully"
    assert "metadata" in data
    
    # Check metadata
    metadata = data["metadata"]
    assert "id" in metadata
    assert "original_filename" in metadata
    assert metadata["original_filename"] == "test.txt"
    assert "storage_location" in metadata
    assert location in metadata["storage_location"]
    assert "description" in metadata
    assert metadata["description"] == description
    
    # Check if the file was actually saved
    file_path = os.path.join(settings.UPLOAD_FOLDER, metadata["storage_location"])
    assert os.path.exists(file_path)
    with open(file_path, "rb") as saved_file:
        assert saved_file.read() == file_content

def test_list_files_empty(test_app):
    """Test list files endpoint with empty directory."""
    # Clear metadata file
    with open(os.path.join(settings.UPLOAD_FOLDER, 'metadata.json'), 'w') as f:
        json.dump([], f)
    
    response = test_app.get("/api/v1/files")
    assert response.status_code == 200
    data = response.json()
    assert "files" in data
    assert isinstance(data["files"], list)
    assert len(data["files"]) == 0

def test_list_files_with_content(test_app):
    """Test list files endpoint with files."""
    # Upload a file first
    file_content = b"Test file content"
    response = test_app.post(
        "/api/v1/upload",
        files={"file": ("test.txt", file_content)},
        data={"location": "test/location", "description": "Test file description"}
    )
    
    # Now check the files list
    response = test_app.get("/api/v1/files")
    assert response.status_code == 200
    data = response.json()
    assert "files" in data
    assert isinstance(data["files"], list)
    assert len(data["files"]) == 1
    
    # Check file metadata
    file_metadata = data["files"][0]
    assert "original_filename" in file_metadata
    assert file_metadata["original_filename"] == "test.txt"
    assert "size" in file_metadata
    assert file_metadata["size"] == len(file_content)