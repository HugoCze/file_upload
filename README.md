# File Upload Service

A high-performance RESTful API service that allows users to upload and manage large files (4GB-8GB) efficiently. The system handles multiple concurrent uploads reliably and organizes files in a structured storage system using FastAPI and asynchronous programming.

## Features

- Upload large files up to 8GB with metadata
- Validate file extensions
- Organize files in a structured storage system
- List all uploaded files with metadata
- Fully type-annotated codebase
- Asynchronous architecture for handling multiple concurrent uploads
- Comprehensive test suite
- API documentation via Swagger UI

## Project Structure

```
.
├── docker-compose.yml     # Docker Compose configuration
├── server/                # Server application
│   ├── Dockerfile         # Server Dockerfile
│   ├── main.py            # FastAPI application entry point
│   ├── app/               # Server application package
│   │   ├── core/          # Core application modules
│   │   ├── models/        # Pydantic models
│   │   ├── routers/       # API route definitions
│   │   ├── services/      # Business logic
│   │   └── utils/         # Utility functions
│   ├── requirements.txt   # Server dependencies
│   └── test_main.py       # API tests
├── client/                # Client application
│   ├── Dockerfile         # Client Dockerfile
│   ├── client.py          # Client script entry point
│   ├── app/               # Client application package
│   │   ├── api/           # API client
│   │   ├── client/        # Client implementation
│   │   └── utils/         # Client utilities
│   └── requirements.txt   # Client dependencies
└── README.md              # This file
```

## API Endpoints

### Health Check
- `GET /health` - Check if the service is running

### Upload File
- `POST /api/v1/upload` - Upload a file with metadata
  - Form parameters:
    - `file`: The file to upload
    - `location`: The target location in the storage system
    - `description`: A description of the file
  - Response: JSON object with file metadata

### List Files
- `GET /api/v1/files` - List all uploaded files
  - Response: JSON array of file metadata

## API Documentation
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)

## Setup Instructions

### Prerequisites

- Docker and Docker Compose
- At least 10GB of free disk space for testing

### Running the Service

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd file-upload-service
   ```

2. Build and start the services:
   ```bash
   docker compose up --build
   ```

3. To test with multiple simultaneous clients:
   ```bash
   docker compose up --build --scale client=6
   ```

4. Access the API documentation:
   ```
   http://localhost:8000/docs
   ```

### Running Tests

```bash
# Navigate to the server directory
cd server

# Run tests
pytest
```

## Configuration

The service can be configured using environment variables:

### Server
- `UPLOAD_FOLDER` - Directory where files will be stored (default: `uploads`)
- `MAX_CONTENT_LENGTH` - Maximum file size in bytes (default: 8GB)

### Client
- `API_URL` - URL of the API service (default: `http://localhost:8000`)
- `FILE_SIZE` - Size of the generated test file in bytes (default: 1GB)
- `TIMEOUT` - Request timeout in seconds (default: 3600)

## Architecture

The project follows a modular architecture with a clear separation of concerns:

1. **API Server**:
   - FastAPI application with router modules for different endpoints
   - Asynchronous request handling for improved performance
   - File handling optimizations for large uploads
   - Type validation using Pydantic models
   - Service layer for business logic
   - Utility functions for common operations

2. **Client**:
   - Asynchronous HTTP client for uploading files
   - File generator for creating test files
   - Configurable client behavior for testing

All data is persisted in a Docker volume to ensure it survives container restarts.

## Performance Considerations

- **Asynchronous Processing**: Uses FastAPI's async capabilities for non-blocking I/O operations
- **Chunked File Handling**: Processes large files in chunks to minimize memory usage
- **Background Tasks**: Performs metadata saving as a background task to improve response time
- **Client Scaling**: Supports multiple concurrent clients for load testing
- **Health Checks**: Includes health check endpoint for service monitoring#   f i l e _ u p l o a d  
 