"""
Arize AX Observability Configuration

This module sets up OpenTelemetry tracing with Arize AX for comprehensive
observability of LangChain, LangGraph, and OpenAI operations.

Environment Variables Required:
- ARIZE_SPACE_ID: Your Arize Space ID
- ARIZE_API_KEY: Your Arize API Key

Optional:
- ARIZE_PROJECT_NAME: Project name in Arize (default: "goalbot-ai-trip-planner")
- ENABLE_TRACING: Set to "1" or "true" to enable tracing (default: auto-detect from credentials)
"""

import os
import logging
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)

# Track if tracing is available and initialized
_TRACING_AVAILABLE = False
_TRACER_PROVIDER = None


def is_tracing_enabled() -> bool:
    """Check if tracing is enabled and available."""
    return _TRACING_AVAILABLE


def get_tracer_provider():
    """Get the initialized tracer provider."""
    return _TRACER_PROVIDER


def init_arize_tracing() -> bool:
    """
    Initialize Arize AX tracing with OpenTelemetry instrumentation.
    
    Returns:
        bool: True if tracing was successfully initialized, False otherwise.
    """
    global _TRACING_AVAILABLE, _TRACER_PROVIDER
    
    # Check if already initialized
    if _TRACING_AVAILABLE:
        logger.info("Arize tracing already initialized")
        return True
    
    # Check for required credentials
    space_id = os.getenv("ARIZE_SPACE_ID")
    api_key = os.getenv("ARIZE_API_KEY")
    
    if not space_id or not api_key:
        logger.warning(
            "Arize tracing disabled: ARIZE_SPACE_ID and ARIZE_API_KEY not set. "
            "Set these environment variables to enable observability."
        )
        return False
    
    try:
        # Import tracing dependencies
        from arize.otel import register
        from openinference.instrumentation.langchain import LangChainInstrumentor
        from openinference.instrumentation.openai import OpenAIInstrumentor
        from openinference.instrumentation.litellm import LiteLLMInstrumentor
        
        # Get project name (default to application name)
        project_name = os.getenv("ARIZE_PROJECT_NAME", "goalbot-ai-trip-planner")
        
        # Register tracer provider with Arize
        logger.info(f"Initializing Arize tracing for project: {project_name}")
        tracer_provider = register(
            space_id=space_id,
            api_key=api_key,
            project_name=project_name,
        )
        
        # Store tracer provider globally
        _TRACER_PROVIDER = tracer_provider
        
        # Instrument LangChain (includes LangGraph)
        LangChainInstrumentor().instrument(
            tracer_provider=tracer_provider,
            include_chains=True,
            include_agents=True,
            include_tools=True,
        )
        logger.info("✓ LangChain/LangGraph instrumented")
        
        # Instrument OpenAI for deeper LLM call traces
        OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)
        logger.info("✓ OpenAI instrumented")
        
        # Instrument LiteLLM (if using LiteLLM for multi-provider support)
        try:
            LiteLLMInstrumentor().instrument(
                tracer_provider=tracer_provider,
                skip_dep_check=True
            )
            logger.info("✓ LiteLLM instrumented")
        except Exception as e:
            logger.warning(f"LiteLLM instrumentation skipped: {e}")
        
        _TRACING_AVAILABLE = True
        logger.info(
            f"🎉 Arize AX tracing initialized successfully!\n"
            f"   Project: {project_name}\n"
            f"   Space ID: {space_id[:8]}...\n"
            f"   View traces at: https://app.arize.com/organizations/{space_id}/spaces"
        )
        
        return True
        
    except ImportError as e:
        logger.error(
            f"Arize tracing dependencies not installed: {e}. "
            f"Run: pip install -r requirements.txt"
        )
        return False
    except Exception as e:
        logger.error(f"Failed to initialize Arize tracing: {e}", exc_info=True)
        return False


# Context manager helpers for manual instrumentation
def using_prompt_template(**kwargs):
    """Context manager for prompt template instrumentation."""
    if _TRACING_AVAILABLE:
        try:
            from openinference.instrumentation import using_prompt_template as _using_prompt_template
            return _using_prompt_template(**kwargs)
        except ImportError:
            pass
    
    # Fallback no-op context manager
    from contextlib import contextmanager
    @contextmanager
    def _noop():
        yield
    return _noop()


def using_metadata(*args, **kwargs):
    """Context manager for metadata instrumentation."""
    if _TRACING_AVAILABLE:
        try:
            from openinference.instrumentation import using_metadata as _using_metadata
            return _using_metadata(*args, **kwargs)
        except ImportError:
            pass
    
    # Fallback no-op context manager
    from contextlib import contextmanager
    @contextmanager
    def _noop():
        yield
    return _noop()


def using_attributes(*args, **kwargs):
    """Context manager for attributes instrumentation."""
    if _TRACING_AVAILABLE:
        try:
            from openinference.instrumentation import using_attributes as _using_attributes
            return _using_attributes(*args, **kwargs)
        except ImportError:
            pass
    
    # Fallback no-op context manager
    from contextlib import contextmanager
    @contextmanager
    def _noop():
        yield
    return _noop()


def get_current_span():
    """Get the current OpenTelemetry span."""
    if _TRACING_AVAILABLE:
        try:
            from opentelemetry import trace
            return trace.get_current_span()
        except ImportError:
            pass
    return None


def set_span_attributes(attributes: dict):
    """Set attributes on the current span."""
    span = get_current_span()
    if span and attributes:
        for key, value in attributes.items():
            span.set_attribute(key, value)


# Initialize tracing on module import (safe - only if credentials present)
if __name__ != "__main__":
    init_arize_tracing()

