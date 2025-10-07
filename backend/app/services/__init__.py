"""
Services package.

Exports all service classes.
"""
from app.services.fred_service import FREDService, FREDAPIError, get_fred_service
from app.services.email_service import EmailService, EmailServiceError, get_email_service
from app.services.metric_analysis_service import MetricAnalysisService
from app.services.bea_service import BEAService
from app.services.bls_service import BLSService

__all__ = [
    "FREDService",
    "FREDAPIError",
    "get_fred_service",
    "EmailService",
    "EmailServiceError",
    "get_email_service",
    "MetricAnalysisService",
    "BEAService",
    "BLSService",
]
