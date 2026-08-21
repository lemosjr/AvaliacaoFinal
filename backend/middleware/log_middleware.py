# backend/middleware/log_middleware.py
"""
Logging middleware for tracking requests, responses, and operations.
"""

import logging
import time
import json
from functools import wraps
from typing import Callable, Any, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class LogMiddleware:
    """
    Middleware for logging requests, responses, and operations.
    Captures timing, payloads, and results for debugging/auditing.
    """

    def __init__(self, log_requests: bool = True, log_responses: bool = True):
        """
        Initialize logging middleware.

        Args:
            log_requests: Log request details
            log_responses: Log response details
        """
        self.log_requests = log_requests
        self.log_responses = log_responses

    def log_operation(self, func: Callable) -> Callable:
        """
        Decorator to log function calls with timing.

        Usage:
            @log_middleware.log_operation
            def my_service_method(...):
                pass
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            function_name = f"{func.__module__}.{func.__name__}"

            # Log start
            logger.info(f"▶️  Starting: {function_name}")

            try:
                result = func(*args, **kwargs)
                elapsed = (time.time() - start_time) * 1000

                # Log success
                logger.info(f"✅ Completed: {function_name} in {elapsed:.2f}ms")
                return result

            except Exception as e:
                elapsed = (time.time() - start_time) * 1000
                logger.error(f"❌ Failed: {function_name} in {elapsed:.2f}ms - Error: {str(e)}")
                raise

        return wrapper

    def log_request(self, request_id: str, operation: str, data: Optional[Dict] = None) -> None:
        """
        Log an incoming request.

        Args:
            request_id: Unique request identifier
            operation: Operation name
            data: Request payload (sanitized)
        """
        if not self.log_requests:
            return

        log_data = {
            'request_id': request_id,
            'operation': operation,
            'timestamp': datetime.now().isoformat()
        }

        if data:
            # Sanitize sensitive data
            sanitized = self._sanitize_data(data)
            log_data['data'] = sanitized

        logger.info(f"📨 Request: {json.dumps(log_data, default=str)}")

    def log_response(self, request_id: str, operation: str, result: Any, duration_ms: float) -> None:
        """
        Log a response.

        Args:
            request_id: Unique request identifier
            operation: Operation name
            result: Response result
            duration_ms: Operation duration in milliseconds
        """
        if not self.log_responses:
            return

        log_data = {
            'request_id': request_id,
            'operation': operation,
            'timestamp': datetime.now().isoformat(),
            'duration_ms': round(duration_ms, 2)
        }

        # Don't log large results
        if isinstance(result, (dict, list)):
            # Limit size
            result_str = json.dumps(result, default=str)
            if len(result_str) > 1000:
                log_data['result'] = f"<truncated, size={len(result_str)}>"
            else:
                log_data['result'] = result

        logger.info(f"📤 Response: {json.dumps(log_data, default=str)}")

    def log_error(self, request_id: str, operation: str, error: Exception, duration_ms: float) -> None:
        """
        Log an error response.

        Args:
            request_id: Unique request identifier
            operation: Operation name
            error: Exception
            duration_ms: Operation duration in milliseconds
        """
        log_data = {
            'request_id': request_id,
            'operation': operation,
            'timestamp': datetime.now().isoformat(),
            'duration_ms': round(duration_ms, 2),
            'error': str(error),
            'error_type': type(error).__name__
        }

        logger.error(f"💥 Error: {json.dumps(log_data, default=str)}")

    def _sanitize_data(self, data: Dict) -> Dict:
        """
        Remove sensitive data from logs.

        Args:
            data: Dictionary to sanitize

        Returns:
            Sanitized dictionary
        """
        sensitive_keys = {'password', 'password_confirm', 'token', 'authorization', 'secret', 'key'}
        sanitized = {}

        for key, value in data.items():
            if key.lower() in sensitive_keys:
                sanitized[key] = '********'
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_data(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self._sanitize_data(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                sanitized[key] = value

        return sanitized

    def with_logging(self, operation_name: Optional[str] = None) -> Callable:
        """
        Decorator for logging entire operations with request/response.

        Usage:
            @log_middleware.with_logging(operation_name='create_product')
            def create_product(request, data):
                # ... logic
                return result

        Args:
            operation_name: Name of the operation (defaults to function name)
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                op_name = operation_name or func.__name__
                request_id = f"{op_name}-{int(time.time() * 1000)}"

                # Extract request data (adapt to your framework)
                request_data = None
                if args:
                    # Assume first arg is request with data
                    first_arg = args[0]
                    if hasattr(first_arg, 'get_json'):
                        request_data = first_arg.get_json()
                    elif hasattr(first_arg, 'json'):
                        request_data = first_arg.json
                    elif isinstance(first_arg, dict):
                        request_data = first_arg

                # Log request
                self.log_request(request_id, op_name, request_data)

                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = (time.time() - start_time) * 1000
                    self.log_response(request_id, op_name, result, duration)
                    return result
                except Exception as e:
                    duration = (time.time() - start_time) * 1000
                    self.log_error(request_id, op_name, e, duration)
                    raise

            return wrapper
        return decorator


# ============ SINGLETON INSTANCE ============
log_middleware = LogMiddleware()