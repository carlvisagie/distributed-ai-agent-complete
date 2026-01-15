"""
Retry Decorator for Autonomous Agent
Provides easy-to-use decorators for adding retry logic to functions
"""

from functools import wraps
from typing import Callable, Optional, Type
import logging

from .error_handler import error_handler, RetryConfig, AgentError

logger = logging.getLogger(__name__)


def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    operation_name: Optional[str] = None,
    catch_exceptions: tuple[Type[Exception], ...] = (Exception,)
):
    """
    Decorator to add retry logic to a function
    
    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        jitter: Whether to add random jitter to delays
        operation_name: Name of operation for logging
        catch_exceptions: Tuple of exception types to catch
    
    Example:
        @retry(max_attempts=5, base_delay=2.0)
        def fetch_data():
            return requests.get("https://api.example.com/data")
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use function name if operation name not provided
            op_name = operation_name or func.__name__
            
            # Create retry config
            retry_config = RetryConfig(
                max_attempts=max_attempts,
                base_delay=base_delay,
                max_delay=max_delay,
                exponential_base=exponential_base,
                jitter=jitter
            )
            
            # Create temporary error handler with custom config
            handler = error_handler.__class__(retry_config)
            
            # Execute with retry
            try:
                return handler.execute_with_retry(
                    func,
                    *args,
                    operation_name=op_name,
                    **kwargs
                )
            except AgentError:
                raise
            except Exception as e:
                if isinstance(e, catch_exceptions):
                    agent_error = handler.handle_error(e, operation_name=op_name)
                    raise agent_error
                raise
        
        return wrapper
    return decorator


def retry_on_network_error(max_attempts: int = 5, base_delay: float = 2.0):
    """
    Decorator specifically for network operations
    
    Example:
        @retry_on_network_error(max_attempts=5)
        def call_api():
            return requests.get("https://api.example.com")
    """
    return retry(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=30.0,
        exponential_base=2.0,
        jitter=True
    )


def retry_on_git_error(max_attempts: int = 3, base_delay: float = 1.0):
    """
    Decorator specifically for Git operations
    
    Example:
        @retry_on_git_error()
        def push_to_github():
            subprocess.run(["git", "push", "origin", "main"])
    """
    return retry(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=10.0,
        exponential_base=2.0,
        jitter=False
    )


def retry_on_file_error(max_attempts: int = 3, base_delay: float = 0.5):
    """
    Decorator specifically for file operations
    
    Example:
        @retry_on_file_error()
        def read_file(path):
            with open(path) as f:
                return f.read()
    """
    return retry(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=5.0,
        exponential_base=1.5,
        jitter=False
    )


# Example usage and testing
if __name__ == "__main__":
    import time
    
    # Test basic retry
    @retry(max_attempts=3, base_delay=1.0)
    def flaky_function(fail_count: int = 2):
        """Function that fails first N times"""
        if not hasattr(flaky_function, "attempts"):
            flaky_function.attempts = 0
        
        flaky_function.attempts += 1
        
        if flaky_function.attempts <= fail_count:
            raise Exception(f"Attempt {flaky_function.attempts} failed")
        
        return f"Success on attempt {flaky_function.attempts}"
    
    # Test network retry
    @retry_on_network_error(max_attempts=3)
    def network_call():
        """Simulated network call"""
        if not hasattr(network_call, "attempts"):
            network_call.attempts = 0
        
        network_call.attempts += 1
        
        if network_call.attempts < 2:
            raise ConnectionError("Network timeout")
        
        return "Network call successful"
    
    # Run tests
    print("Testing basic retry...")
    try:
        result = flaky_function(fail_count=2)
        print(f"✅ {result}")
    except Exception as e:
        print(f"❌ {e}")
    
    print("\nTesting network retry...")
    try:
        result = network_call()
        print(f"✅ {result}")
    except Exception as e:
        print(f"❌ {e}")
    
    print("\nRetry decorator tests complete!")
