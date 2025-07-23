from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import sqlite3
import string
import random
from datetime import datetime, timedelta
import sys
import os

# Try to import logging middleware, fallback to basic logging if it fails
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Logging Middleware'))
    from logging_middleware import LoggingMiddleware, app_logger
    LOGGING_MIDDLEWARE_AVAILABLE = True
except Exception as e:
    print(f"Warning: Could not import logging middleware: {e}")
    LOGGING_MIDDLEWARE_AVAILABLE = False
    
    # Fallback logging setup
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('urlshortener_logs.log'),
            logging.StreamHandler()
        ]
    )
    
    class FallbackLogger:
        def __init__(self):
            self.logger = logging.getLogger("URLShortener")
        
        def log_info(self, package, message):
            self.logger.info(f"[{package}] {message}")
        
        def log_warn(self, package, message):
            self.logger.warning(f"[{package}] {message}")
        
        def log_error(self, package, message):
            self.logger.error(f"[{package}] {message}")
        
        def log_debug(self, package, message):
            self.logger.debug(f"[{package}] {message}")
    
    app_logger = FallbackLogger()

# Database file
DB_FILE = "url_shortener.db"

def init_db():
    """Initialize the database and create tables if they don't exist."""
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            shortcode TEXT PRIMARY KEY,
            url TEXT NOT NULL,
            expiry TEXT NOT NULL,
            access_count INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()
    app_logger.log_info("db", "Database initialized successfully")

# Models
class URLRequest(BaseModel):
    url: str
    validity: int = 30
    shortcode: str = None

class URLResponse(BaseModel):
    shortLink: str
    expiry: str

def generate_shortcode():
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=6))

def save_url(shortcode, url, expiry):
    """Save URL to database with logging."""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.execute("INSERT INTO urls (shortcode, url, expiry) VALUES (?, ?, ?)", 
                    (shortcode, url, expiry))
        conn.commit()
        conn.close()
        app_logger.log_info("db", f"URL saved successfully: {shortcode}")
    except Exception as e:
        app_logger.log_error("db", f"Failed to save URL: {str(e)}")
        raise

def get_url(shortcode):
    """Retrieve URL from database with logging."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.execute("SELECT url, expiry, access_count FROM urls WHERE shortcode = ?", 
                             (shortcode,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            app_logger.log_info("db", f"URL retrieved successfully: {shortcode}")
        else:
            app_logger.log_warn("db", f"URL not found: {shortcode}")
        
        return result
    except Exception as e:
        app_logger.log_error("db", f"Failed to retrieve URL: {str(e)}")
        raise

def increment_count(shortcode):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("UPDATE urls SET access_count = access_count + 1 WHERE shortcode = ?", 
                (shortcode,))
    conn.commit()
    conn.close()

def shortcode_exists(shortcode):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.execute("SELECT 1 FROM urls WHERE shortcode = ?", (shortcode,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

init_db()
app = FastAPI(title="URL Shortener")

# Add logging middleware if available
if LOGGING_MIDDLEWARE_AVAILABLE:
    logging_middleware = LoggingMiddleware()
    app.middleware("http")(logging_middleware)

app_logger.log_info("service", "URL Shortener Microservice started")

@app.get("/")
def health():
    """Health check endpoint."""
    app_logger.log_info("handler", "Health check requested")
    return {"status": "healthy", "service": "URL Shortener"}

@app.post("/shorturls", response_model=URLResponse)
def create_short_url(request: URLRequest, http_request: Request):
    """Create a short URL with comprehensive logging."""
    try:
        app_logger.log_info("handler", f"Creating short URL for: {request.url}")
        
        # Validate URL format
        if not request.url.startswith(('http://', 'https://')):
            app_logger.log_warn("handler", f"Invalid URL format: {request.url}")
            raise HTTPException(status_code=400, detail="Invalid URL format")
        
        # Validate validity period
        if request.validity < 1 or request.validity > 525600:
            app_logger.log_warn("handler", f"Invalid validity period: {request.validity}")
            raise HTTPException(status_code=400, detail="Invalid validity period")
        
        # Handle shortcode
        if request.shortcode:
            app_logger.log_info("handler", f"Using custom shortcode: {request.shortcode}")
            if len(request.shortcode) < 3 or len(request.shortcode) > 20:
                app_logger.log_warn("handler", f"Invalid shortcode length: {request.shortcode}")
                raise HTTPException(status_code=400, detail="Shortcode must be 3-20 characters")
            if not request.shortcode.isalnum():
                app_logger.log_warn("handler", f"Invalid shortcode format: {request.shortcode}")
                raise HTTPException(status_code=400, detail="Shortcode must be alphanumeric")
            if shortcode_exists(request.shortcode):
                app_logger.log_warn("handler", f"Shortcode already exists: {request.shortcode}")
                raise HTTPException(status_code=400, detail="Shortcode already taken")
            shortcode = request.shortcode
        else:
            app_logger.log_info("handler", "Generating random shortcode")
            attempts = 0
            while attempts < 10:
                shortcode = generate_shortcode()
                if not shortcode_exists(shortcode):
                    break
                attempts += 1
            else:
                app_logger.log_error("handler", "Failed to generate unique shortcode after 10 attempts")
                raise HTTPException(status_code=500, detail="Could not generate shortcode")
        
        # Calculate expiry
        expiry_time = datetime.now() + timedelta(minutes=request.validity)
        expiry_str = expiry_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Save URL
        save_url(shortcode, request.url, expiry_str)
        
        # Generate response
        base_url = f"{http_request.url.scheme}://{http_request.url.netloc}"
        short_link = f"{base_url}/{shortcode}"
        
        app_logger.log_info("handler", f"Short URL created successfully: {short_link}")
        return URLResponse(shortLink=short_link, expiry=expiry_str)
        
    except HTTPException as e:
        app_logger.log_error("handler", f"HTTP Exception in create_short_url: {e.detail}")
        raise
    except Exception as e:
        app_logger.log_error("handler", f"Unexpected error in create_short_url: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/{shortcode}")
def redirect_to_url(shortcode: str):
    """Redirect to original URL with comprehensive logging."""
    try:
        app_logger.log_info("handler", f"Redirect request for shortcode: {shortcode}")
        
        result = get_url(shortcode)
        
        if not result:
            app_logger.log_warn("handler", f"Short URL not found: {shortcode}")
            raise HTTPException(status_code=404, detail="Short URL not found")
        
        url, expiry_str, access_count = result
        
        # Check expiry
        expiry_time = datetime.strptime(expiry_str, "%Y-%m-%dT%H:%M:%SZ")
        if datetime.now() > expiry_time:
            app_logger.log_warn("handler", f"Short URL expired: {shortcode}")
            raise HTTPException(status_code=410, detail="Short URL has expired")
        
        # Increment access count
        increment_count(shortcode)
        app_logger.log_info("handler", f"Redirecting to: {url} (access count: {access_count + 1})")
        
        return RedirectResponse(url=url, status_code=302)
        
    except HTTPException as e:
        app_logger.log_error("handler", f"HTTP Exception in redirect_to_url: {e.detail}")
        raise
    except Exception as e:
        app_logger.log_error("handler", f"Unexpected error in redirect_to_url: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
