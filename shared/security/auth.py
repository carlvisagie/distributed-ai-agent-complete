"""
API Authentication and Security Module
Provides API key authentication, rate limiting, and access control
"""
import hashlib
import secrets
import time
from typing import Optional, Dict, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import os


@dataclass
class APIKey:
    """API key with metadata"""
    key_hash: str
    name: str
    created_at: float
    last_used: float = 0
    usage_count: int = 0
    rate_limit: int = 100  # requests per hour
    is_active: bool = True
    permissions: List[str] = field(default_factory=lambda: ["read", "write"])


@dataclass
class RateLimitInfo:
    """Rate limit tracking"""
    requests: List[float] = field(default_factory=list)
    limit: int = 100
    window: int = 3600  # 1 hour in seconds


class AuthManager:
    """Manages API authentication and authorization"""
    
    def __init__(self, keys_file: str = "api_keys.json"):
        self.keys_file = keys_file
        self.api_keys: Dict[str, APIKey] = {}
        self.rate_limits: Dict[str, RateLimitInfo] = {}
        self.load_keys()
    
    def load_keys(self):
        """Load API keys from file"""
        if os.path.exists(self.keys_file):
            try:
                with open(self.keys_file, 'r') as f:
                    data = json.load(f)
                    for key_hash, key_data in data.items():
                        self.api_keys[key_hash] = APIKey(
                            key_hash=key_data['key_hash'],
                            name=key_data['name'],
                            created_at=key_data['created_at'],
                            last_used=key_data.get('last_used', 0),
                            usage_count=key_data.get('usage_count', 0),
                            rate_limit=key_data.get('rate_limit', 100),
                            is_active=key_data.get('is_active', True),
                            permissions=key_data.get('permissions', ["read", "write"])
                        )
            except Exception as e:
                print(f"Error loading API keys: {e}")
    
    def save_keys(self):
        """Save API keys to file"""
        try:
            data = {}
            for key_hash, api_key in self.api_keys.items():
                data[key_hash] = {
                    'key_hash': api_key.key_hash,
                    'name': api_key.name,
                    'created_at': api_key.created_at,
                    'last_used': api_key.last_used,
                    'usage_count': api_key.usage_count,
                    'rate_limit': api_key.rate_limit,
                    'is_active': api_key.is_active,
                    'permissions': api_key.permissions
                }
            
            with open(self.keys_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving API keys: {e}")
    
    def generate_api_key(
        self,
        name: str,
        rate_limit: int = 100,
        permissions: List[str] = None
    ) -> str:
        """
        Generate a new API key
        
        Args:
            name: Name/description for the key
            rate_limit: Requests per hour
            permissions: List of permissions (read, write, admin)
        
        Returns:
            The generated API key (only shown once)
        """
        if permissions is None:
            permissions = ["read", "write"]
        
        # Generate secure random key
        raw_key = secrets.token_urlsafe(32)
        key_hash = self._hash_key(raw_key)
        
        # Create API key object
        api_key = APIKey(
            key_hash=key_hash,
            name=name,
            created_at=time.time(),
            rate_limit=rate_limit,
            permissions=permissions
        )
        
        # Store
        self.api_keys[key_hash] = api_key
        self.save_keys()
        
        return raw_key
    
    def _hash_key(self, key: str) -> str:
        """Hash an API key for storage"""
        return hashlib.sha256(key.encode()).hexdigest()
    
    def verify_key(self, key: str) -> Optional[APIKey]:
        """
        Verify an API key
        
        Args:
            key: The API key to verify
        
        Returns:
            APIKey object if valid, None otherwise
        """
        key_hash = self._hash_key(key)
        api_key = self.api_keys.get(key_hash)
        
        if not api_key:
            return None
        
        if not api_key.is_active:
            return None
        
        # Update usage
        api_key.last_used = time.time()
        api_key.usage_count += 1
        self.save_keys()
        
        return api_key
    
    def check_rate_limit(self, key: str) -> bool:
        """
        Check if request is within rate limit
        
        Args:
            key: The API key
        
        Returns:
            True if within limit, False otherwise
        """
        key_hash = self._hash_key(key)
        api_key = self.api_keys.get(key_hash)
        
        if not api_key:
            return False
        
        # Get or create rate limit info
        if key_hash not in self.rate_limits:
            self.rate_limits[key_hash] = RateLimitInfo(
                limit=api_key.rate_limit
            )
        
        rate_info = self.rate_limits[key_hash]
        current_time = time.time()
        
        # Remove old requests outside the window
        rate_info.requests = [
            req_time for req_time in rate_info.requests
            if current_time - req_time < rate_info.window
        ]
        
        # Check if within limit
        if len(rate_info.requests) >= rate_info.limit:
            return False
        
        # Add current request
        rate_info.requests.append(current_time)
        return True
    
    def check_permission(self, key: str, permission: str) -> bool:
        """
        Check if API key has specific permission
        
        Args:
            key: The API key
            permission: Permission to check (read, write, admin)
        
        Returns:
            True if has permission, False otherwise
        """
        key_hash = self._hash_key(key)
        api_key = self.api_keys.get(key_hash)
        
        if not api_key:
            return False
        
        return permission in api_key.permissions
    
    def revoke_key(self, key: str):
        """Revoke an API key"""
        key_hash = self._hash_key(key)
        if key_hash in self.api_keys:
            self.api_keys[key_hash].is_active = False
            self.save_keys()
    
    def list_keys(self) -> List[Dict]:
        """List all API keys (without revealing actual keys)"""
        return [
            {
                'name': api_key.name,
                'created_at': datetime.fromtimestamp(api_key.created_at).isoformat(),
                'last_used': datetime.fromtimestamp(api_key.last_used).isoformat() if api_key.last_used else 'Never',
                'usage_count': api_key.usage_count,
                'rate_limit': api_key.rate_limit,
                'is_active': api_key.is_active,
                'permissions': api_key.permissions
            }
            for api_key in self.api_keys.values()
        ]
    
    def get_rate_limit_status(self, key: str) -> Dict:
        """Get current rate limit status"""
        key_hash = self._hash_key(key)
        api_key = self.api_keys.get(key_hash)
        
        if not api_key:
            return {'error': 'Invalid API key'}
        
        if key_hash not in self.rate_limits:
            return {
                'limit': api_key.rate_limit,
                'remaining': api_key.rate_limit,
                'reset_at': datetime.fromtimestamp(time.time() + 3600).isoformat()
            }
        
        rate_info = self.rate_limits[key_hash]
        current_time = time.time()
        
        # Clean old requests
        rate_info.requests = [
            req_time for req_time in rate_info.requests
            if current_time - req_time < rate_info.window
        ]
        
        remaining = max(0, rate_info.limit - len(rate_info.requests))
        
        # Calculate reset time (oldest request + window)
        if rate_info.requests:
            reset_time = rate_info.requests[0] + rate_info.window
        else:
            reset_time = current_time + rate_info.window
        
        return {
            'limit': rate_info.limit,
            'remaining': remaining,
            'reset_at': datetime.fromtimestamp(reset_time).isoformat()
        }


# Global auth manager instance
auth_manager = AuthManager()


def require_auth(permission: str = "read"):
    """
    Decorator for FastAPI endpoints requiring authentication
    
    Usage:
        @app.get("/api/data")
        @require_auth("read")
        async def get_data(api_key: str = Header(...)):
            return {"data": "..."}
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract API key from kwargs
            api_key = kwargs.get('api_key') or kwargs.get('x_api_key')
            
            if not api_key:
                return {'error': 'API key required'}, 401
            
            # Verify key
            key_obj = auth_manager.verify_key(api_key)
            if not key_obj:
                return {'error': 'Invalid API key'}, 401
            
            # Check rate limit
            if not auth_manager.check_rate_limit(api_key):
                return {'error': 'Rate limit exceeded'}, 429
            
            # Check permission
            if not auth_manager.check_permission(api_key, permission):
                return {'error': f'Permission denied: {permission} required'}, 403
            
            # Call original function
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


if __name__ == "__main__":
    # Example usage
    manager = AuthManager()
    
    # Generate a new API key
    key = manager.generate_api_key(
        name="Development Key",
        rate_limit=1000,
        permissions=["read", "write", "admin"]
    )
    
    print(f"Generated API key: {key}")
    print("\nSave this key securely - it won't be shown again!")
    
    # Verify the key
    key_obj = manager.verify_key(key)
    if key_obj:
        print(f"\nKey verified: {key_obj.name}")
        print(f"Permissions: {key_obj.permissions}")
    
    # Check rate limit
    for i in range(5):
        if manager.check_rate_limit(key):
            print(f"Request {i+1}: OK")
        else:
            print(f"Request {i+1}: Rate limit exceeded")
    
    # Get rate limit status
    status = manager.get_rate_limit_status(key)
    print(f"\nRate limit status: {status}")
    
    # List all keys
    print("\nAll API keys:")
    for key_info in manager.list_keys():
        print(f"  - {key_info['name']}: {key_info['usage_count']} requests")
