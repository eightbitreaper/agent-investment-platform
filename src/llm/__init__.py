"""
LLM package for Agent Investment Platform

This package provides a unified interface for interacting with various
Large Language Model providers and managing AI-powered investment analysis.
"""

from .client import (
    LLMClient,
    LLMProvider,
    TaskType,
    LLMRequest,
    LLMResponse,
    generate_text
)

__all__ = [
    'LLMClient',
    'LLMProvider',
    'TaskType',
    'LLMRequest',
    'LLMResponse',
    'generate_text'
]
