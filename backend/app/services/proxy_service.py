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
        self.haproxy_socket = os.environ.get('HAPROXY_SOCKET', '/var/run/haproxy/admin.sock')
        self.config_dir = os.environ.get('PROXY_CONFIG_DIR', '/app/proxy_configs')
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
