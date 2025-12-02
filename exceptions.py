"""
Custom exception classes for FHIR Medical Data Transformer.
Provides specific error types for better error handling and debugging.
"""


class FHIRTransformerError(Exception):
    """Base exception class for all FHIR Transformer errors."""
    
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self):
        """Convert exception to a dictionary for API responses."""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "details": self.details
        }


class InvalidInputError(FHIRTransformerError):
    """Raised when input data validation fails."""
    pass


class FHIRValidationError(FHIRTransformerError):
    """Raised when FHIR resource validation fails."""
    pass


class ResourceCreationError(FHIRTransformerError):
    """Raised when FHIR resource creation fails."""
    pass


class DatabaseError(FHIRTransformerError):
    """Raised when database operations fail."""
    pass
