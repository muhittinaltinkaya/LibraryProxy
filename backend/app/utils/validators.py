import re
from typing import Dict, Any

def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password: str) -> Dict[str, Any]:
    """Validate password strength"""
    if not password:
        return {'valid': False, 'message': 'Password is required'}
    
    if len(password) < 8:
        return {'valid': False, 'message': 'Password must be at least 8 characters long'}
    
    if len(password) > 128:
        return {'valid': False, 'message': 'Password must be less than 128 characters'}
    
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return {'valid': False, 'message': 'Password must contain at least one uppercase letter'}
    
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return {'valid': False, 'message': 'Password must contain at least one lowercase letter'}
    
    # Check for at least one digit
    if not re.search(r'\d', password):
        return {'valid': False, 'message': 'Password must contain at least one digit'}
    
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return {'valid': False, 'message': 'Password must contain at least one special character'}
    
    return {'valid': True, 'message': 'Password is valid'}

def validate_username(username: str) -> Dict[str, Any]:
    """Validate username format"""
    if not username:
        return {'valid': False, 'message': 'Username is required'}
    
    if len(username) < 3:
        return {'valid': False, 'message': 'Username must be at least 3 characters long'}
    
    if len(username) > 30:
        return {'valid': False, 'message': 'Username must be less than 30 characters'}
    
    # Check for valid characters (alphanumeric and underscore only)
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return {'valid': False, 'message': 'Username can only contain letters, numbers, and underscores'}
    
    # Check if starts with letter
    if not re.match(r'^[a-zA-Z]', username):
        return {'valid': False, 'message': 'Username must start with a letter'}
    
    return {'valid': True, 'message': 'Username is valid'}

def validate_url(url: str) -> bool:
    """Validate URL format"""
    if not url:
        return False
    
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))

def validate_ip_address(ip: str) -> bool:
    """Validate IP address format (IPv4 or IPv6)"""
    if not ip:
        return False
    
    # IPv4 pattern
    ipv4_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    
    # IPv6 pattern (simplified)
    ipv6_pattern = r'^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
    
    return bool(re.match(ipv4_pattern, ip) or re.match(ipv6_pattern, ip))

def sanitize_string(text: str, max_length: int = 255) -> str:
    """Sanitize string input"""
    if not text:
        return ''
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length]
    
    # Remove potentially dangerous characters
    text = re.sub(r'[<>"\']', '', text)
    
    return text

def validate_journal_slug(slug: str) -> Dict[str, Any]:
    """Validate journal slug format"""
    if not slug:
        return {'valid': False, 'message': 'Slug is required'}
    
    if len(slug) < 2:
        return {'valid': False, 'message': 'Slug must be at least 2 characters long'}
    
    if len(slug) > 50:
        return {'valid': False, 'message': 'Slug must be less than 50 characters'}
    
    # Check for valid characters (lowercase letters, numbers, and hyphens only)
    if not re.match(r'^[a-z0-9-]+$', slug):
        return {'valid': False, 'message': 'Slug can only contain lowercase letters, numbers, and hyphens'}
    
    # Check if starts and ends with letter or number
    if not re.match(r'^[a-z0-9]', slug) or not re.search(r'[a-z0-9]$', slug):
        return {'valid': False, 'message': 'Slug must start and end with a letter or number'}
    
    # Check for consecutive hyphens
    if '--' in slug:
        return {'valid': False, 'message': 'Slug cannot contain consecutive hyphens'}
    
    return {'valid': True, 'message': 'Slug is valid'}
