import logging
from typing import Dict, Any, Optional
from fastapi import HTTPException
from pydantic import ValidationError

class JarvisError(Exception):
    """Base exception class for JARVIS AI Assistant"""
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class VoiceProcessingError(JarvisError):
    """Raised when voice processing operations fail"""
    pass

class AIProcessingError(JarvisError):
    """Raised when AI-related operations fail"""
    pass

class SystemControlError(JarvisError):
    """Raised when system control operations fail"""
    pass

class ErrorHandler:
    """Centralized error handling for JARVIS AI Assistant"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_logging()
    
    def setup_logging(self):
        """Configure logging settings"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('jarvis.log'),
                logging.StreamHandler()
            ]
        )
    
    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """Process and format error responses"""
        if isinstance(error, JarvisError):
            self.logger.error(
                f"JARVIS Error: {error.message}",
                extra={"error_code": error.error_code, "details": error.details}
            )
            return {
                "error": error.message,
                "error_code": error.error_code,
                "details": error.details
            }
        
        elif isinstance(error, ValidationError):
            self.logger.error(f"Validation Error: {str(error)}")
            return {
                "error": "Invalid request data",
                "error_code": "VALIDATION_ERROR",
                "details": error.errors()
            }
        
        elif isinstance(error, HTTPException):
            self.logger.error(f"HTTP Error: {error.detail}")
            return {
                "error": error.detail,
                "error_code": f"HTTP_{error.status_code}",
                "details": {}
            }
        
        # Handle unexpected errors
        self.logger.critical(f"Unexpected Error: {str(error)}")
        return {
            "error": "An unexpected error occurred",
            "error_code": "INTERNAL_ERROR",
            "details": {"type": type(error).__name__}
        }
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Log error with additional context"""
        error_data = self.handle_error(error)
        if context:
            error_data["context"] = context
        self.logger.error(
            f"Error occurred: {error_data['error']}",
            extra=error_data
        )
        return error_data

# Global error handler instance
error_handler = ErrorHandler()