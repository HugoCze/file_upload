Usage Instructions:

1. Start the services with multiple client instances:
   docker compose up --scale client=6

This will start:
- The main API service
- 6 instances of the client service that will generate and prepare files for upload

2. Test concurrent file uploads by making a request to:
   curl http://localhost:5000/trigger-all

This will trigger all client instances to simultaneously upload their files to the API service, demonstrating concurrent upload handling.

The system will:
- Generate random files from each client instance
- Upload files concurrently to the API
- Process and validate the uploads
- Return results for each upload operation

You can monitor the progress in the docker compose logs to see the concurrent upload operations in action.

3. Upload a single file manually:
   After the services are running, you can upload individual files using:
   
   curl -X 'POST' \
     'http://localhost:8000/api/uploads/' \
     -H 'accept: application/json' \
     -H 'Content-Type: multipart/form-data' \
     -F 'file=@test.txt;type=text/plain' \
     -F 'client_id=' \
     -F 'timestamp=' \
     -F 'file_creation_time=' \
     -F 'creation_duration='

   Replace test.txt with your file path. The other fields (client_id, timestamp, etc.) are optional metadata.

4. View uploaded files:
   To see the list of all uploaded files, visit:
   http://localhost:8000/api/data/

5. Run tests:
   To run the health check tests, execute:
   pytest tests/test_health.py

   This will verify:
   - API and client service health endpoints
   - File extension validation (allowed: txt, pdf, doc, csv, wav, mp4, docx, dat)
   - File extension validation (blocked: py, jpg, exe, zip)
   - Data endpoint structure and schema validation
   

   Make sure both services are running before executing the tests.
