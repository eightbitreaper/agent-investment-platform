"""
GitHub integration package for Agent Investment Platform

This package provides functionality for uploading and managing investment reports
on GitHub repositories for version control and collaboration.
"""

from .report_uploader import (
    GitHubReportUploader,
    upload_report_to_github,
    batch_upload_reports_to_github
)

__all__ = [
    'GitHubReportUploader',
    'upload_report_to_github',
    'batch_upload_reports_to_github'
]
