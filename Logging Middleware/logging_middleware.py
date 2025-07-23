"""
Logging Middleware for URL Shortener - Makes API calls to test server
"""

import requests
import time
import json
from datetime import datetime
from typing import Optional


class LoggingMiddleware:
    """Logging middleware that sends logs to the evaluation service."""
    
    def __init__(self):
        self.log_api_url = "http://20.244.56.144/evaluation-service/logs"
        self.stack = "backend"  # We're working with backend only
        self.bearer_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJnLnN1cnBpeWEyMkBpZmhlaW5kaWEub3JnIiwiZXhwIjoxNzUzMjU1NDMwLCJpYXQiOjE3NTMyNTQ1MzAsImlzcyI6IkFmZm9yZCBNZWRpY2FsIFRlY2hub2xvZ2llcyBQcml2YXRlIExpbWl0ZWQiLCJqdGkiOiJiNjM3NWQ0OS1mMTc1LTRkM2MtYjNmMy1jM2JlOTMzMzcxYjIiLCJsb2NhbGUiOiJlbi1JTiIsIm5hbWUiOiJnYWxpIHN1cHJpeWEiLCJzdWIiOiJjNDk5ZmM5Ny0xMTZlLTQ3YWMtOTFkZS0wZGViYjUzMjc4NTYifSwiZW1haWwiOiJnLnN1cnBpeWEyMkBpZmhlaW5kaWEub3JnIiwibmFtZSI6ImdhbGkgc3Vwcml5YSIsInJvbGxObyI6IjIyc3R1Y2hoMDEwMDc3IiwiYWNjZXNzQ29kZSI6ImJDdUNGVCIsImNsaWVudElEIjoiYzQ5OWZjOTctMTE2ZS00N2FjLTkxZGUtMGRlYmI1MzI3ODU2IiwiY2xpZW50U2VjcmV0IjoiYnZZaGpobXZqcmpVa2pzQSJ9.joYYXj57gCYBcgen0WOPrseYffyuGGXFEUQuDKtzmu4"
    
    def log(self, stack: str, level: str, package: str, message: str) -> bool:
        """
        Send log to the evaluation service.
        
        Args:
            stack: "backend" or "frontend" (we use "backend")
            level: "debug", "info", "warn", "error", "fatal"
            package: Package name like "handler", "controller", etc.
            message: Log message
        """
        try:
            # Validate parameters according to constraints
            if stack.lower() not in ["backend", "frontend"]:
                return False
            
            if level.lower() not in ["debug", "info", "warn", "error", "fatal"]:
                return False
            
            # Backend packages as shown in image
            backend_packages = [
                "cache", "controller", "cron_job", "db", "domain", 
                "handler", "repository", "route", "service"
            ]
            
            if package.lower() not in backend_packages:
                return False
            
            # Prepare request body
            request_body = {
                "stack": stack.lower(),
                "level": level.lower(),
                "package": package.lower(),
                "message": message
            }
            
            # Make API call
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.bearer_token}"
            }
            
            response = requests.post(
                self.log_api_url,
                json=request_body,
                headers=headers,
                timeout=5
            )
            
            return response.status_code == 200
            
        except Exception as e:
            # Fallback to console logging if API call fails
            print(f"Log API call failed: {e}")
            print(f"Log: [{stack}][{level}][{package}] {message}")
            return False
    
    async def __call__(self, request, call_next):
        """Middleware function that logs requests and responses."""
        start_time = time.time()
        
        # Log incoming request
        self.log(
            stack="backend",
            level="info",
            package="handler",
            message=f"Incoming request: {request.method} {request.url}"
        )
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log successful response
            self.log(
                stack="backend",
                level="info",
                package="handler",
                message=f"Request processed successfully: {response.status_code} - {process_time:.3f}s"
            )
            
            return response
            
        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            self.log(
                stack="backend",
                level="error",
                package="handler",
                message=f"Request failed: {str(e)} - {process_time:.3f}s"
            )
            raise
    
    def log_info(self, package: str, message: str):
        """Log info level message."""
        self.log("backend", "info", package, message)
    
    def log_warn(self, package: str, message: str):
        """Log warning level message."""
        self.log("backend", "warn", package, message)
    
    def log_error(self, package: str, message: str):
        """Log error level message."""
        self.log("backend", "error", package, message)
    
    def log_debug(self, package: str, message: str):
        """Log debug level message."""
        self.log("backend", "debug", package, message)


# Global logger instance
app_logger = LoggingMiddleware()
