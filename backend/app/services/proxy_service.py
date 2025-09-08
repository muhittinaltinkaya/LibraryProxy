import os
import socket
import subprocess
import json
from datetime import datetime
from app import db
from app.models.proxy_config import ProxyConfig
from app.models.journal import Journal

class ProxyService:
    """Service for managing HAProxy configurations dynamically"""
    
    def __init__(self):
        self.haproxy_socket = os.environ.get('HAPROXY_SOCKET', '/run/haproxy/admin.sock')
        self.config_dir = os.environ.get('PROXY_CONFIG_DIR', '/app/proxy_configs')
        self.haproxy_config_path = '/app/haproxy_config/haproxy-simple.cfg'
        self.ensure_config_dir()
    
    def ensure_config_dir(self):
        """Ensure configuration directory exists"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir, exist_ok=True)
    
    def generate_haproxy_rule(self, journal, user):
        """Generate HAProxy configuration rule for journal access"""
        rule_parts = []
        
        # ACL for journal path
        rule_parts.append(f"acl is_{journal.slug} path_beg /{journal.proxy_path}")
        
        # ACL for user (if authentication required)
        if journal.requires_auth:
            rule_parts.append(f"acl user_{user.id} hdr(X-User-ID) {user.id}")
            rule_parts.append(f"use_backend {journal.slug}_backend if is_{journal.slug} user_{user.id}")
        else:
            rule_parts.append(f"use_backend {journal.slug}_backend if is_{journal.slug}")
        
        return "\n".join(rule_parts)
    
    def generate_global_haproxy_rule(self, journal):
        """Generate HAProxy configuration rule for global journal access (no user authentication)"""
        rule_parts = []
        
        # ACL for journal path
        rule_parts.append(f"acl is_{journal.slug} path_beg /{journal.proxy_path}")
        
        # Use backend for this journal (no user authentication required)
        rule_parts.append(f"use_backend {journal.slug}_backend if is_{journal.slug}")
        
        return "\n".join(rule_parts)
    
    def generate_backend_config(self, journal):
        """Generate HAProxy backend configuration for journal"""
        backend_config = f"""
backend {journal.slug}_backend
    mode http
    balance roundrobin
    option httpchk GET /
    http-check expect status 200
    server {journal.slug}_server {self._extract_host_from_url(journal.base_url)} check
"""
        
        # Add custom headers if configured
        if journal.custom_headers:
            for header, value in journal.custom_headers.items():
                backend_config += f"    http-request set-header {header} {value}\n"
        
        # Add timeout settings
        if journal.timeout:
            backend_config += f"    timeout server {journal.timeout}s\n"
        
        return backend_config
    
    def apply_proxy_config(self, proxy_config):
        """Apply proxy configuration to HAProxy"""
        try:
            # Generate backend configuration
            journal = Journal.query.get(proxy_config.journal_id)
            backend_config = self.generate_backend_config(journal)
            
            # Write configuration to file
            config_file = os.path.join(self.config_dir, f"{proxy_config.config_name}.cfg")
            with open(config_file, 'w') as f:
                f.write(backend_config)
            
            # Reload HAProxy configuration
            self.reload_haproxy()
            
            return True
            
        except Exception as e:
            print(f"Failed to apply proxy config: {str(e)}")
            return False
    
    def apply_global_proxy_config(self, proxy_config):
        """Apply global proxy configuration to HAProxy (accessible to all users)"""
        try:
            # Generate backend configuration
            journal = Journal.query.get(proxy_config.journal_id)
            backend_config = self.generate_backend_config(journal)
            
            # Generate frontend rules for global access
            frontend_rules = self.generate_global_haproxy_rule(journal)
            
            # Write backend configuration to file
            backend_file = os.path.join(self.config_dir, f"{proxy_config.config_name}_backend.cfg")
            with open(backend_file, 'w') as f:
                f.write(backend_config)
            
            # Write frontend rules to file
            frontend_file = os.path.join(self.config_dir, f"{proxy_config.config_name}_frontend.cfg")
            with open(frontend_file, 'w') as f:
                f.write(frontend_rules)
            
            # Update main HAProxy configuration with new rules
            self.update_main_haproxy_config()
            
            # Reload HAProxy configuration
            self.reload_haproxy()
            
            return True
            
        except Exception as e:
            print(f"Failed to apply global proxy config: {str(e)}")
            return False
    
    def remove_proxy_config(self, proxy_config):
        """Remove proxy configuration from HAProxy"""
        try:
            # Remove configuration file
            config_file = os.path.join(self.config_dir, f"{proxy_config.config_name}.cfg")
            if os.path.exists(config_file):
                os.remove(config_file)
            
            # Reload HAProxy configuration
            self.reload_haproxy()
            
            return True
            
        except Exception as e:
            print(f"Failed to remove proxy config: {str(e)}")
            return False
    
    def generate_dynamic_haproxy_config(self):
        """Generate complete HAProxy configuration with all active journals"""
        try:
            # Get all active journals directly from database
            active_journals = Journal.query.filter_by(is_active=True).all()
            
            # Generate frontend ACL rules and use_backend rules
            frontend_acls = []
            frontend_backends = []
            backend_configs = []
            
            for journal in active_journals:
                # Add frontend ACL
                frontend_acls.append(f"    acl is_{journal.slug} path_beg /{journal.proxy_path}")
                frontend_backends.append(f"    use_backend {journal.slug}_backend if is_{journal.slug}")
                
                # Generate backend configuration
                backend_config = self.generate_dynamic_backend_config(journal)
                backend_configs.append(backend_config)
            
            # Generate complete HAProxy configuration
            haproxy_config = f"""global
    daemon
    log stdout local0
    stats timeout 30s

defaults
    mode http
    log global
    option httplog
    option dontlognull
    option forwardfor
    timeout connect 5000
    timeout client 50000
    timeout server 50000

# Stats page
listen stats
    bind *:8404
    stats enable
    stats uri /stats
    stats refresh 30s
    stats admin if TRUE

# Frontend for LibProxy
frontend libproxy_frontend
    bind *:80
    
    # CORS headers for all responses
    http-after-response set-header Access-Control-Allow-Origin "http://localhost:3000"
    http-after-response set-header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS"
    http-after-response set-header Access-Control-Allow-Headers "Content-Type, Authorization"
    http-after-response set-header Access-Control-Allow-Credentials "true"
    
    # Handle preflight OPTIONS requests
    acl is_options method OPTIONS
    http-request return status 200 if is_options
    
    # Handle favicon.ico requests
    acl is_favicon path /favicon.ico
    http-request return status 204 if is_favicon
    
    # Dynamic journal proxy rules
{chr(10).join(frontend_acls)}
{chr(10).join(frontend_backends)}
    
    default_backend libproxy_backend

# Backend for LibProxy API
backend libproxy_backend
    balance roundrobin
    option httpchk GET /api/health
    http-check expect status 200
    
    # Backend servers
    server libproxy_api backend:5000 check

# Dynamic backend configurations for journals
{chr(10).join(backend_configs)}
"""
            
            return haproxy_config
            
        except Exception as e:
            print(f"Failed to generate dynamic HAProxy config: {str(e)}")
            return None
    
    def generate_dynamic_backend_config(self, journal):
        """Generate HAProxy backend configuration for a journal with CORS and path rewriting"""
        # Extract host and port from URL
        from urllib.parse import urlparse
        parsed = urlparse(journal.base_url)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        ssl_config = "ssl verify none" if parsed.scheme == 'https' else ""
        
        # Path rewriting logic
        path_rewrite_rules = []
        if journal.proxy_path:
            # Handle root path: /proxy_path -> /
            path_rewrite_rules.append(f'    http-request set-path "/" if {{ path -m str "/{journal.proxy_path}" }}')
            # Handle sub paths: /proxy_path/xyz -> /xyz
            path_rewrite_rules.append(f'    http-request set-path %[path,regsub(^/{journal.proxy_path}/,/)] if {{ path -m beg "/{journal.proxy_path}/" }}')
        
        backend_config = f"""
backend {journal.slug}_backend
    mode http
    balance roundrobin
{chr(10).join(path_rewrite_rules)}
    # CORS headers for journal responses
    http-after-response set-header Access-Control-Allow-Origin "http://localhost:3000"
    http-after-response set-header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS"
    http-after-response set-header Access-Control-Allow-Headers "Content-Type, Authorization"
    http-after-response set-header Access-Control-Allow-Credentials "true"
    server {journal.slug}_server {host}:{port} {ssl_config}
    timeout server {journal.timeout}s"""
        
        # Add custom headers if configured
        if journal.custom_headers:
            for header, value in journal.custom_headers.items():
                backend_config += f"\n    http-request set-header {header} {value}"
        
        return backend_config
    
    def update_main_haproxy_config(self):
        """Update main HAProxy configuration with all active journals"""
        try:
            # Generate complete dynamic configuration
            haproxy_config = self.generate_dynamic_haproxy_config()
            
            if not haproxy_config:
                return False
            
            # Write the updated configuration
            with open(self.haproxy_config_path, 'w') as f:
                f.write(haproxy_config)
            
            print(f"HAProxy configuration updated with {Journal.query.filter_by(is_active=True).count()} active journals")
            return True
            
        except Exception as e:
            print(f"Failed to update main HAProxy config: {str(e)}")
            return False
    
    def reload_haproxy(self):
        """Reload HAProxy configuration"""
        try:
            # Use HAProxy socket to reload configuration
            if os.path.exists(self.haproxy_socket):
                # Send reload command via socket
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                    s.connect(self.haproxy_socket)
                    s.send(b"reload\n")
                    response = s.recv(1024)
                    return b"reload" in response.lower()
            else:
                # Fallback to system command
                result = subprocess.run(['haproxy', '-f', '/etc/haproxy/haproxy.cfg', '-c'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    subprocess.run(['systemctl', 'reload', 'haproxy'], check=True)
                    return True
                else:
                    print(f"HAProxy config validation failed: {result.stderr}")
                    return False
                    
        except Exception as e:
            print(f"Failed to reload HAProxy: {str(e)}")
            return False
    
    def get_haproxy_stats(self):
        """Get HAProxy statistics"""
        try:
            if os.path.exists(self.haproxy_socket):
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                    s.connect(self.haproxy_socket)
                    s.send(b"show stat\n")
                    response = s.recv(4096).decode('utf-8')
                    return self._parse_haproxy_stats(response)
            else:
                return {"error": "HAProxy socket not available"}
                
        except Exception as e:
            return {"error": f"Failed to get HAProxy stats: {str(e)}"}
    
    def _parse_haproxy_stats(self, stats_data):
        """Parse HAProxy statistics data"""
        lines = stats_data.strip().split('\n')
        if not lines:
            return {"error": "No stats data"}
        
        # Parse CSV format
        headers = lines[0].split(',')
        stats = []
        
        for line in lines[1:]:
            if line.strip():
                values = line.split(',')
                stat = dict(zip(headers, values))
                stats.append(stat)
        
        return {"stats": stats}
    
    def _extract_host_from_url(self, url):
        """Extract host and port from URL"""
        from urllib.parse import urlparse
        
        parsed = urlparse(url)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == 'https' else 80)
        
        return f"{host}:{port}"
    
    def cleanup_expired_configs(self):
        """Clean up expired proxy configurations"""
        try:
            expired_configs = ProxyConfig.query.filter(
                ProxyConfig.expires_at < datetime.utcnow()
            ).all()
            
            for config in expired_configs:
                self.remove_proxy_config(config)
                db.session.delete(config)
            
            db.session.commit()
            return len(expired_configs)
            
        except Exception as e:
            print(f"Failed to cleanup expired configs: {str(e)}")
            return 0
    
    def get_active_configs(self):
        """Get all active proxy configurations"""
        return ProxyConfig.query.filter(
            ProxyConfig.is_active == True,
            ProxyConfig.expires_at > datetime.utcnow()
        ).all()
    
    def get_config_status(self):
        """Get status of all proxy configurations"""
        active_configs = self.get_active_configs()
        haproxy_stats = self.get_haproxy_stats()
        
        return {
            "active_configs": len(active_configs),
            "haproxy_stats": haproxy_stats,
            "config_directory": self.config_dir,
            "socket_available": os.path.exists(self.haproxy_socket)
        }
