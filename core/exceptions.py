"""Domain-level exceptions for Velora."""


class VeloraError(Exception):
    """Base exception for Velora application errors."""


class IntegrationError(VeloraError):
    """Raised when an external service integration fails."""


class BrevoError(IntegrationError):
    """Raised when Brevo email API calls fail."""


class CloudinaryError(IntegrationError):
    """Raised when Cloudinary upload or delete operations fail."""
