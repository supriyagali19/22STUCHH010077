# Simple URL Shortener Microservice

A basic HTTP URL Shortener built with Python FastAPI that meets all assignment requirements with clean, simple code.

## Features

✅ **Assignment Requirements:**
- ✅ Logging integration with file and console output
- ✅ Microservice architecture using FastAPI
- ✅ Globally unique short links
- ✅ Default 30-minute validity (configurable)
- ✅ Custom shortcode support (3-20 alphanumeric characters)
- ✅ Automatic redirection (HTTP 302)
- ✅ Proper error handling with HTTP status codes

## API Endpoints

### 1. Health Check
```
GET /
```
Returns service status.

### 2. Create Short URL
```
POST /shorturls
```

**Request Body:**
```json
{
  "url": "https://example.com/very/long/url",
  "validity": 60,
  "shortcode": "mycode"
}
```

- `url` (required): Original URL to shorten
- `validity` (optional): Validity period in minutes (default: 30)
- `shortcode` (optional): Custom shortcode (3-20 alphanumeric chars)

**Response:**
```json
{
  "shortLink": "http://localhost:8000/mycode",
  "expiry": "2025-01-23T15:30:00Z"
}
```

### 3. Redirect to Original URL
```
GET /{shortcode}
```
Redirects to the original URL (HTTP 302).

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install fastapi uvicorn
   ```

2. **Start the service:**
   ```bash
   python main.py
   ```
   Service runs on: http://localhost:8000

3. **Test the service:**
   ```bash
   python test_service.py
   ```

4. **View API docs:**
   Visit: http://localhost:8000/docs

## Usage Examples

### Using curl:

1. **Create short URL:**
   ```bash
   curl -X POST "http://localhost:8000/shorturls" \
        -H "Content-Type: application/json" \
        -d '{"url": "https://www.google.com", "validity": 60}'
   ```

2. **Create with custom shortcode:**
   ```bash
   curl -X POST "http://localhost:8000/shorturls" \
        -H "Content-Type: application/json" \
        -d '{
          "url": "https://www.github.com",
          "validity": 120,
          "shortcode": "github"
        }'
   ```

3. **Access shortened URL:**
   ```bash
   curl -L "http://localhost:8000/github"
   ```

### Using Python:

```python
import requests

# Create short URL
response = requests.post("http://localhost:8000/shorturls", json={
    "url": "https://www.example.com",
    "validity": 60,
    "shortcode": "test123"
})
print(response.json())
# Output: {"shortLink": "http://localhost:8000/test123", "expiry": "..."}

# Use the short URL
response = requests.get("http://localhost:8000/test123")
print(response.url)  # Original URL after redirect
```

## File Structure

```
Backend Test Submission/
├── main.py              # Main application (simplified)
├── test_service.py      # Simple test script
├── requirements.txt     # Dependencies
└── README.md           # This file

Generated Files:
├── url_shortener.db    # SQLite database
└── urlshortener_logs.log # Application logs
```

## Error Codes

- **200**: Success
- **302**: Redirect (for shortcode access)
- **400**: Bad Request (invalid input, shortcode taken)
- **404**: Not Found (shortcode doesn't exist)
- **410**: Gone (URL expired)
- **500**: Internal Server Error

## Database Schema

Simple SQLite table:
```sql
CREATE TABLE urls (
    shortcode TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    expiry TEXT NOT NULL,
    access_count INTEGER DEFAULT 0
);
```

## Code Highlights

- **Simple**: ~150 lines of clean, readable code
- **Fast**: Direct SQLite operations, no ORM overhead
- **Reliable**: Basic error handling for all scenarios
- **Logged**: All requests/responses logged to file and console
- **Tested**: Includes comprehensive test script

## Key Simplifications Made

1. **Removed complex classes** - Direct functions instead
2. **Simplified logging** - Basic logging setup, no custom middleware complexity
3. **Removed unnecessary features** - No analytics endpoint, no complex validation
4. **Direct database operations** - Simple SQLite queries instead of ORM
5. **Basic models** - Simple Pydantic models without complex validators
6. **Minimal dependencies** - Only FastAPI, no extra packages

The code is now much simpler while maintaining all required functionality!
