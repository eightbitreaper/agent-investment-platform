"""
LLM Client for Agent Investment Platform

This module provides a unified interface for interacting with various
Large Language Model providers including OpenAI, Anthropic, Hugging Face,
and local models via Ollama.
"""

import os
import yaml
import json
import logging
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, AsyncGenerator
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

# Import configuration loading
try:
    import aiohttp
    import httpx
except ImportError:
    raise ImportError("aiohttp and httpx are required. Install with: pip install aiohttp httpx")

# Optional imports for different providers
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    from huggingface_hub import hf_hub_download, list_repo_files
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"


class TaskType(Enum):
    """Types of tasks for model selection."""
    STOCK_ANALYSIS = "stock_analysis"
    MARKET_SENTIMENT = "market_sentiment"
    TECHNICAL_ANALYSIS = "technical_analysis"
    INVESTMENT_STRATEGY = "investment_strategy"
    RISK_ASSESSMENT = "risk_assessment"
    REPORT_GENERATION = "report_generation"
    NEWS_SUMMARIZATION = "news_summarization"
    DATA_EXTRACTION = "data_extraction"
    CLASSIFICATION = "classification"
    DOCUMENT_EMBEDDINGS = "document_embeddings"
    SEMANTIC_SEARCH = "semantic_search"
    GENERAL = "general"


@dataclass
class LLMResponse:
    """Response from LLM API."""
    content: str
    model: str
    provider: str
    tokens_used: int = 0
    cost_usd: float = 0.0
    response_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMRequest:
    """Request to LLM API."""
    prompt: str
    task_type: TaskType = TaskType.GENERAL
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    model: Optional[str] = None
    provider: Optional[LLMProvider] = None
    system_message: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class LLMClient:
    """
    Unified client for multiple LLM providers.

    Features:
    - Automatic model selection based on task type
    - Fallback handling for failed requests
    - Cost tracking and limits
    - Caching for repeated requests
    - Health monitoring and metrics
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the LLM client.

        Args:
            config_path: Path to LLM configuration file
        """
        self.logger = logging.getLogger(__name__)

        # Load configuration
        if config_path:
            self.config_path = Path(config_path)
        else:
            # Default to project config
            project_root = Path(__file__).parents[2]
            self.config_path = project_root / "config" / "llm-config.yaml"

        self.config = self._load_config()

        # Initialize providers
        self.providers = {}
        self._initialize_providers()

        # Request cache
        self.cache = {}
        self.cache_ttl = self.config.get('optimization', {}).get('cache_ttl_seconds', 3600)

        # Cost tracking
        self.cost_tracker = {
            'daily_cost': 0.0,
            'monthly_cost': 0.0,
            'last_reset': datetime.now(),
            'request_count': 0
        }

        # Performance metrics
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0,
            'provider_usage': {}
        }

    def _load_config(self) -> Dict[str, Any]:
        """Load LLM configuration from YAML file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            # Expand environment variables
            config = self._expand_env_vars(config)

            self.logger.info(f"Loaded LLM configuration from {self.config_path}")
            return config

        except Exception as e:
            self.logger.error(f"Failed to load LLM config: {e}")
            # Return minimal default config
            return {
                'default': {
                    'provider': 'huggingface',
                    'model': 'microsoft/Phi-3-mini-4k-instruct',
                    'max_tokens': 4096,
                    'temperature': 0.1
                },
                'providers': {},
                'task_assignments': {}
            }

    def _expand_env_vars(self, obj: Any) -> Any:
        """Recursively expand environment variables in configuration."""
        if isinstance(obj, dict):
            return {key: self._expand_env_vars(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._expand_env_vars(item) for item in obj]
        elif isinstance(obj, str) and obj.startswith('${') and obj.endswith('}'):
            # Handle ${VAR:-default} syntax
            env_expr = obj[2:-1]  # Remove ${ and }
            if ':-' in env_expr:
                var_name, default_value = env_expr.split(':-', 1)
                return os.getenv(var_name, default_value)
            else:
                return os.getenv(env_expr, obj)
        else:
            return obj

    def _initialize_providers(self):
        """Initialize available LLM providers."""
        providers_config = self.config.get('providers', {})

        # Initialize OpenAI
        if OPENAI_AVAILABLE and 'openai' in providers_config:
            openai_config = providers_config['openai']
            api_key = openai_config.get('api_key')
            if api_key and api_key != 'your_openai_api_key_here':
                try:
                    self.providers[LLMProvider.OPENAI] = openai.OpenAI(api_key=api_key)
                    self.logger.info("OpenAI provider initialized")
                except Exception as e:
                    self.logger.warning(f"Failed to initialize OpenAI: {e}")

        # Initialize Anthropic
        if ANTHROPIC_AVAILABLE and 'anthropic' in providers_config:
            anthropic_config = providers_config['anthropic']
            api_key = anthropic_config.get('api_key')
            if api_key and api_key != 'your_anthropic_api_key_here':
                try:
                    self.providers[LLMProvider.ANTHROPIC] = anthropic.Anthropic(api_key=api_key)
                    self.logger.info("Anthropic provider initialized")
                except Exception as e:
                    self.logger.warning(f"Failed to initialize Anthropic: {e}")

        # Initialize Hugging Face
        if HUGGINGFACE_AVAILABLE and 'huggingface' in providers_config:
            self.providers[LLMProvider.HUGGINGFACE] = {}
            self.logger.info("Hugging Face provider initialized")

        # Initialize Ollama
        if 'ollama' in providers_config:
            self.providers[LLMProvider.OLLAMA] = {}
            self.logger.info("Ollama provider initialized")

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generate text using the most appropriate LLM.

        Args:
            request: LLM request with prompt and parameters

        Returns:
            LLM response with generated text and metadata
        """
        start_time = time.time()
        self.metrics['total_requests'] += 1

        try:
            # Check cost limits
            if not self._check_cost_limits():
                raise Exception("Daily or monthly cost limit exceeded")

            # Select model and provider
            model, provider = self._select_model(request)

            # Check cache first
            cache_key = self._generate_cache_key(request, model)
            if self._is_cache_valid(cache_key):
                cached_response = self.cache[cache_key]
                cached_response.metadata['from_cache'] = True
                return cached_response

            # Generate response
            response = await self._generate_with_provider(request, model, provider)
            response.response_time = time.time() - start_time

            # Cache response
            if self.config.get('optimization', {}).get('cache_enabled', True):
                self.cache[cache_key] = response

            # Update metrics and cost tracking
            self._update_metrics(response, provider)
            self._update_cost_tracking(response)

            self.metrics['successful_requests'] += 1
            return response

        except Exception as e:
            self.logger.error(f"Failed to generate response: {e}")
            self.metrics['failed_requests'] += 1

            # Try fallback if available
            fallback_model, fallback_provider = self._get_fallback_model(request.task_type)
            if fallback_model and fallback_provider and fallback_provider != provider:
                try:
                    self.logger.info(f"Trying fallback model: {fallback_model}")
                    response = await self._generate_with_provider(request, fallback_model, fallback_provider)
                    response.response_time = time.time() - start_time
                    response.metadata['used_fallback'] = True

                    self._update_metrics(response, fallback_provider)
                    self._update_cost_tracking(response)
                    self.metrics['successful_requests'] += 1
                    return response

                except Exception as fallback_error:
                    self.logger.error(f"Fallback also failed: {fallback_error}")

            # Return error response
            return LLMResponse(
                content=f"Error generating response: {str(e)}",
                model="error",
                provider="error",
                response_time=time.time() - start_time,
                metadata={'error': str(e)}
            )

    async def _generate_with_provider(
        self,
        request: LLMRequest,
        model: str,
        provider: LLMProvider
    ) -> LLMResponse:
        """Generate response using specific provider."""
        if provider == LLMProvider.OPENAI:
            return await self._generate_openai(request, model)
        elif provider == LLMProvider.ANTHROPIC:
            return await self._generate_anthropic(request, model)
        elif provider == LLMProvider.HUGGINGFACE:
            return await self._generate_huggingface(request, model)
        elif provider == LLMProvider.OLLAMA:
            return await self._generate_ollama(request, model)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    async def _generate_openai(self, request: LLMRequest, model: str) -> LLMResponse:
        """Generate response using OpenAI API."""
        if LLMProvider.OPENAI not in self.providers:
            raise Exception("OpenAI provider not available")

        client = self.providers[LLMProvider.OPENAI]

        messages = []
        if request.system_message:
            messages.append({"role": "system", "content": request.system_message})
        messages.append({"role": "user", "content": request.prompt})

        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=model,
            messages=messages,
            max_tokens=request.max_tokens or 4096,
            temperature=request.temperature or 0.1
        )

        return LLMResponse(
            content=response.choices[0].message.content,
            model=model,
            provider="openai",
            tokens_used=response.usage.total_tokens,
            cost_usd=self._calculate_openai_cost(model, response.usage.total_tokens)
        )

    async def _generate_anthropic(self, request: LLMRequest, model: str) -> LLMResponse:
        """Generate response using Anthropic API."""
        if LLMProvider.ANTHROPIC not in self.providers:
            raise Exception("Anthropic provider not available")

        client = self.providers[LLMProvider.ANTHROPIC]

        response = await asyncio.to_thread(
            client.messages.create,
            model=model,
            max_tokens=request.max_tokens or 4096,
            temperature=request.temperature or 0.1,
            system=request.system_message or "",
            messages=[{"role": "user", "content": request.prompt}]
        )

        return LLMResponse(
            content=response.content[0].text,
            model=model,
            provider="anthropic",
            tokens_used=response.usage.input_tokens + response.usage.output_tokens,
            cost_usd=self._calculate_anthropic_cost(model, response.usage.input_tokens, response.usage.output_tokens)
        )

    async def _generate_huggingface(self, request: LLMRequest, model: str) -> LLMResponse:
        """Generate response using Hugging Face model."""
        if not HUGGINGFACE_AVAILABLE:
            raise Exception("Hugging Face not available")

        try:
            # Load model and tokenizer (cached after first use)
            cache_key = f"hf_model_{model}"
            if cache_key not in self.providers[LLMProvider.HUGGINGFACE]:
                tokenizer = AutoTokenizer.from_pretrained(model)
                model_obj = AutoModelForCausalLM.from_pretrained(model)
                pipe = pipeline("text-generation", model=model_obj, tokenizer=tokenizer)
                self.providers[LLMProvider.HUGGINGFACE][cache_key] = pipe

            pipe = self.providers[LLMProvider.HUGGINGFACE][cache_key]

            # Generate response
            result = await asyncio.to_thread(
                pipe,
                request.prompt,
                max_length=request.max_tokens or 1024,
                temperature=request.temperature or 0.1,
                do_sample=True,
                return_full_text=False
            )

            generated_text = result[0]['generated_text']

            return LLMResponse(
                content=generated_text,
                model=model,
                provider="huggingface",
                tokens_used=len(generated_text.split()),  # Approximate
                cost_usd=0.0  # Free
            )

        except Exception as e:
            self.logger.error(f"Hugging Face generation failed: {e}")
            raise

    async def _generate_ollama(self, request: LLMRequest, model: str) -> LLMResponse:
        """Generate response using Ollama API."""
        ollama_config = self.config.get('providers', {}).get('ollama', {})
        host = ollama_config.get('host', 'http://localhost:11434')

        async with aiohttp.ClientSession() as session:
            payload = {
                'model': model,
                'prompt': request.prompt,
                'options': {
                    'temperature': request.temperature or 0.1,
                    'num_predict': request.max_tokens or 4096
                }
            }

            async with session.post(f"{host}/api/generate", json=payload) as response:
                if response.status != 200:
                    raise Exception(f"Ollama API error: {response.status}")

                result = await response.json()

                return LLMResponse(
                    content=result.get('response', ''),
                    model=model,
                    provider="ollama",
                    tokens_used=len(result.get('response', '').split()),  # Approximate
                    cost_usd=0.0  # Free for local models
                )

    def _select_model(self, request: LLMRequest) -> tuple[str, LLMProvider]:
        """Select the best model for the request."""
        # If specific model/provider requested, use that
        if request.model and request.provider:
            return request.model, request.provider

        # Get task-specific assignment
        task_assignments = self.config.get('task_assignments', {})
        task_config = task_assignments.get(request.task_type.value, {})

        # Get primary model
        primary_model = task_config.get('primary')
        if primary_model:
            provider = self._get_provider_for_model(primary_model)
            if provider and provider in self.providers:
                return primary_model, provider

        # Fall back to default
        default_config = self.config.get('default', {})
        default_model = default_config.get('model', 'microsoft/Phi-3-mini-4k-instruct')
        default_provider = LLMProvider(default_config.get('provider', 'huggingface'))

        return default_model, default_provider

    def _get_fallback_model(self, task_type: TaskType) -> tuple[Optional[str], Optional[LLMProvider]]:
        """Get fallback model for task type."""
        task_assignments = self.config.get('task_assignments', {})
        task_config = task_assignments.get(task_type.value, {})

        fallback_model = task_config.get('fallback')
        if fallback_model:
            provider = self._get_provider_for_model(fallback_model)
            if provider and provider in self.providers:
                return fallback_model, provider

        return None, None

    def _get_provider_for_model(self, model: str) -> Optional[LLMProvider]:
        """Determine provider for a given model name."""
        providers_config = self.config.get('providers', {})

        for provider_name, provider_config in providers_config.items():
            models = provider_config.get('models', [])
            for model_config in models:
                if model_config.get('name') == model or model_config.get('repo_id') == model:
                    return LLMProvider(provider_name)

        # Default heuristics
        if model.startswith('gpt-'):
            return LLMProvider.OPENAI
        elif model.startswith('claude-'):
            return LLMProvider.ANTHROPIC
        elif '/' in model:  # Hugging Face format
            return LLMProvider.HUGGINGFACE
        else:
            return LLMProvider.OLLAMA

    def _generate_cache_key(self, request: LLMRequest, model: str) -> str:
        """Generate cache key for request."""
        key_data = {
            'prompt': request.prompt[:100],  # First 100 chars
            'model': model,
            'max_tokens': request.max_tokens,
            'temperature': request.temperature,
            'system_message': request.system_message
        }
        return str(hash(str(key_data)))

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached response is still valid."""
        if cache_key not in self.cache:
            return False

        # Check TTL
        cached_response = self.cache[cache_key]
        if 'cached_at' in cached_response.metadata:
            cached_at = datetime.fromisoformat(cached_response.metadata['cached_at'])
            if datetime.now() - cached_at > timedelta(seconds=self.cache_ttl):
                del self.cache[cache_key]
                return False

        return True

    def _check_cost_limits(self) -> bool:
        """Check if cost limits allow new requests."""
        cost_config = self.config.get('cost_management', {})
        daily_limit = cost_config.get('daily_limit_usd', float('inf'))
        monthly_limit = cost_config.get('monthly_limit_usd', float('inf'))

        # Reset daily cost if needed
        now = datetime.now()
        if now.date() > self.cost_tracker['last_reset'].date():
            self.cost_tracker['daily_cost'] = 0.0
            self.cost_tracker['last_reset'] = now

        # Check limits
        if self.cost_tracker['daily_cost'] >= daily_limit:
            self.logger.warning("Daily cost limit exceeded")
            return False

        if self.cost_tracker['monthly_cost'] >= monthly_limit:
            self.logger.warning("Monthly cost limit exceeded")
            return False

        return True

    def _update_metrics(self, response: LLMResponse, provider: LLMProvider):
        """Update performance metrics."""
        # Update provider usage
        provider_name = provider.value
        if provider_name not in self.metrics['provider_usage']:
            self.metrics['provider_usage'][provider_name] = 0
        self.metrics['provider_usage'][provider_name] += 1

        # Update average response time
        current_avg = self.metrics['average_response_time']
        total_requests = self.metrics['total_requests']
        self.metrics['average_response_time'] = (
            (current_avg * (total_requests - 1) + response.response_time) / total_requests
        )

    def _update_cost_tracking(self, response: LLMResponse):
        """Update cost tracking."""
        self.cost_tracker['daily_cost'] += response.cost_usd
        self.cost_tracker['monthly_cost'] += response.cost_usd
        self.cost_tracker['request_count'] += 1

    def _calculate_openai_cost(self, model: str, tokens: int) -> float:
        """Calculate cost for OpenAI API usage."""
        # Simplified cost calculation - would need actual pricing
        cost_per_1k_tokens = {
            'gpt-4-turbo-preview': 0.01,
            'gpt-4': 0.03,
            'gpt-3.5-turbo': 0.002
        }

        rate = cost_per_1k_tokens.get(model, 0.01)
        return (tokens / 1000) * rate

    def _calculate_anthropic_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for Anthropic API usage."""
        # Simplified cost calculation - would need actual pricing
        input_cost_per_1k = {
            'claude-3-sonnet-20240229': 0.003,
            'claude-3-haiku-20240307': 0.00025
        }

        output_cost_per_1k = {
            'claude-3-sonnet-20240229': 0.015,
            'claude-3-haiku-20240307': 0.00125
        }

        input_rate = input_cost_per_1k.get(model, 0.003)
        output_rate = output_cost_per_1k.get(model, 0.015)

        return (input_tokens / 1000) * input_rate + (output_tokens / 1000) * output_rate

    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return {
            **self.metrics,
            'cost_tracking': self.cost_tracker,
            'cache_size': len(self.cache),
            'available_providers': list(self.providers.keys())
        }

    def get_available_models(self) -> Dict[str, List[str]]:
        """Get list of available models by provider."""
        available_models = {}
        providers_config = self.config.get('providers', {})

        for provider_name, provider_config in providers_config.items():
            if LLMProvider(provider_name) in self.providers:
                models = provider_config.get('models', [])
                available_models[provider_name] = [
                    model.get('name', '') for model in models
                ]

        return available_models

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all providers."""
        health_status = {}

        for provider in self.providers:
            try:
                # Simple test request
                test_request = LLMRequest(
                    prompt="Hello, this is a test.",
                    task_type=TaskType.GENERAL,
                    max_tokens=10
                )

                response = await self._generate_with_provider(
                    test_request,
                    "gpt-3.5-turbo" if provider == LLMProvider.OPENAI else "test-model",
                    provider
                )

                health_status[provider.value] = {
                    'status': 'healthy',
                    'response_time': response.response_time,
                    'last_check': datetime.now().isoformat()
                }

            except Exception as e:
                health_status[provider.value] = {
                    'status': 'unhealthy',
                    'error': str(e),
                    'last_check': datetime.now().isoformat()
                }

        return health_status


# Convenience functions
async def generate_text(
    prompt: str,
    task_type: TaskType = TaskType.GENERAL,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    config_path: Optional[str] = None
) -> str:
    """
    Convenience function to generate text with default settings.

    Args:
        prompt: Text prompt for generation
        task_type: Type of task for model selection
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
        config_path: Path to LLM configuration

    Returns:
        Generated text content
    """
    client = LLMClient(config_path)
    request = LLMRequest(
        prompt=prompt,
        task_type=task_type,
        max_tokens=max_tokens,
        temperature=temperature
    )

    response = await client.generate(request)
    return response.content


if __name__ == "__main__":
    # Example usage
    async def main():
        logging.basicConfig(level=logging.INFO)

        client = LLMClient()

        # Test request
        request = LLMRequest(
            prompt="What are the key factors to consider when analyzing a stock?",
            task_type=TaskType.STOCK_ANALYSIS,
            max_tokens=500
        )

        response = await client.generate(request)
        print(f"Response: {response.content[:200]}...")
        print(f"Model: {response.model}")
        print(f"Provider: {response.provider}")
        print(f"Tokens: {response.tokens_used}")

        # Get metrics
        metrics = client.get_metrics()
        print(f"Metrics: {metrics}")

    asyncio.run(main())
