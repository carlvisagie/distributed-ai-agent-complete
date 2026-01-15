"""
Error Handler for Autonomous Agent
Provides comprehensive error handling, retry logic, and recovery procedures
"""

import traceback
import time
from typing import Optional, Callable, Any, Dict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ErrorSeverity(str, Enum):
    """Error severity levels"""
    LOW = "low"  # Retry automatically
    MEDIUM = "medium"  # Retry with backoff
    HIGH = "high"  # Requires manual intervention
    CRITICAL = "critical"  # Stop all operations


class ErrorCategory(str, Enum):
    """Error categories for classification"""
    NETWORK = "network"  # Network/API failures
    FILE_SYSTEM = "file_system"  # File operations
    GIT = "git"  # Git/GitHub operations
    EXECUTION = "execution"  # Code execution errors
    VALIDATION = "validation"  # Data validation errors
    TIMEOUT = "timeout"  # Operation timeouts
    AUTHENTICATION = "authentication"  # Auth failures
    UNKNOWN = "unknown"  # Unclassified errors


class AgentError(Exception):
    """Base exception for agent errors"""
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        recoverable: bool = True,
        context: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.category = category
        self.severity = severity
        self.recoverable = recoverable
        self.context = context or {}
        self.timestamp = time.time()
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary"""
        return {
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "recoverable": self.recoverable,
            "context": self.context,
            "timestamp": self.timestamp,
            "traceback": traceback.format_exc()
        }


class RetryConfig:
    """Configuration for retry logic"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt"""
        import random
        
        # Exponential backoff
        delay = min(
            self.base_delay * (self.exponential_base ** attempt),
            self.max_delay
        )
        
        # Add jitter to prevent thundering herd
        if self.jitter:
            delay = delay * (0.5 + random.random() * 0.5)
        
        return delay


class ErrorHandler:
    """Handles errors with retry logic and recovery"""
    
    def __init__(self, retry_config: Optional[RetryConfig] = None):
        self.retry_config = retry_config or RetryConfig()
        self.error_history: list[AgentError] = []
    
    def classify_error(self, error: Exception) -> tuple[ErrorCategory, ErrorSeverity]:
        """Classify error by type and determine severity"""
        error_str = str(error).lower()
        
        # Network errors
        if any(keyword in error_str for keyword in ["connection", "timeout", "network", "unreachable"]):
            return ErrorCategory.NETWORK, ErrorSeverity.MEDIUM
        
        # Git errors
        if any(keyword in error_str for keyword in ["git", "github", "repository", "branch"]):
            return ErrorCategory.GIT, ErrorSeverity.MEDIUM
        
        # File system errors
        if any(keyword in error_str for keyword in ["file", "directory", "permission", "not found"]):
            return ErrorCategory.FILE_SYSTEM, ErrorSeverity.LOW
        
        # Authentication errors
        if any(keyword in error_str for keyword in ["auth", "unauthorized", "forbidden", "token"]):
            return ErrorCategory.AUTHENTICATION, ErrorSeverity.HIGH
        
        # Timeout errors
        if "timeout" in error_str:
            return ErrorCategory.TIMEOUT, ErrorSeverity.MEDIUM
        
        # Validation errors
        if any(keyword in error_str for keyword in ["invalid", "validation", "schema"]):
            return ErrorCategory.VALIDATION, ErrorSeverity.LOW
        
        return ErrorCategory.UNKNOWN, ErrorSeverity.MEDIUM
    
    def should_retry(self, error: AgentError, attempt: int) -> bool:
        """Determine if operation should be retried"""
        # Don't retry if max attempts reached
        if attempt >= self.retry_config.max_attempts:
            return False
        
        # Don't retry critical errors
        if error.severity == ErrorSeverity.CRITICAL:
            return False
        
        # Don't retry high severity errors
        if error.severity == ErrorSeverity.HIGH:
            return False
        
        # Don't retry non-recoverable errors
        if not error.recoverable:
            return False
        
        return True
    
    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        operation_name: str = "unknown"
    ) -> AgentError:
        """Handle an error and create AgentError"""
        category, severity = self.classify_error(error)
        
        agent_error = AgentError(
            message=str(error),
            category=category,
            severity=severity,
            recoverable=severity in [ErrorSeverity.LOW, ErrorSeverity.MEDIUM],
            context={
                **(context or {}),
                "operation": operation_name,
                "original_error_type": type(error).__name__
            }
        )
        
        self.error_history.append(agent_error)
        logger.error(f"Error in {operation_name}: {agent_error.to_dict()}")
        
        return agent_error
    
    def execute_with_retry(
        self,
        func: Callable,
        *args,
        operation_name: str = "unknown",
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Any:
        """Execute function with retry logic"""
        attempt = 0
        last_error = None
        
        while attempt < self.retry_config.max_attempts:
            try:
                result = func(*args, **kwargs)
                
                # Log successful retry
                if attempt > 0:
                    logger.info(f"{operation_name} succeeded on attempt {attempt + 1}")
                
                return result
            
            except Exception as e:
                agent_error = self.handle_error(e, context, operation_name)
                last_error = agent_error
                
                if not self.should_retry(agent_error, attempt):
                    logger.error(f"{operation_name} failed permanently: {agent_error.message}")
                    raise agent_error
                
                # Calculate delay and wait
                delay = self.retry_config.get_delay(attempt)
                logger.warning(
                    f"{operation_name} failed (attempt {attempt + 1}/{self.retry_config.max_attempts}). "
                    f"Retrying in {delay:.2f}s..."
                )
                time.sleep(delay)
                
                attempt += 1
        
        # All retries exhausted
        logger.error(f"{operation_name} failed after {self.retry_config.max_attempts} attempts")
        raise last_error
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of all errors"""
        if not self.error_history:
            return {"total_errors": 0, "by_category": {}, "by_severity": {}}
        
        by_category = {}
        by_severity = {}
        
        for error in self.error_history:
            # Count by category
            cat = error.category.value
            by_category[cat] = by_category.get(cat, 0) + 1
            
            # Count by severity
            sev = error.severity.value
            by_severity[sev] = by_severity.get(sev, 0) + 1
        
        return {
            "total_errors": len(self.error_history),
            "by_category": by_category,
            "by_severity": by_severity,
            "recent_errors": [e.to_dict() for e in self.error_history[-5:]]
        }


# Global error handler instance
error_handler = ErrorHandler()
