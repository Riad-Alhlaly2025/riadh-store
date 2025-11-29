#!/usr/bin/env python
"""
Scaling configuration script for MyShop e-commerce platform
This script sets up Redis for caching and session storage, and configures load balancing
"""

import os
import sys
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scaling_setup.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ScalingSetup:
    """Class to handle scaling configuration"""
    
    def __init__(self):
        self.redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')
        self.load_balancer_type = os.environ.get('LOAD_BALANCER_TYPE', 'nginx')
        
    def configure_redis(self):
        """Configure Redis for caching and session storage"""
        try:
            logger.info("Configuring Redis for caching and session storage")
            
            # In a real implementation, this would connect to Redis and set up configurations
            # For now, we'll just log the configuration
            
            redis_config = {
                "url": self.redis_url,
                "max_connections": int(os.environ.get('REDIS_MAX_CONNECTIONS', 20)),
                "socket_timeout": int(os.environ.get('REDIS_SOCKET_TIMEOUT', 5)),
                "socket_connect_timeout": int(os.environ.get('REDIS_SOCKET_CONNECT_TIMEOUT', 5)),
                "health_check_interval": int(os.environ.get('REDIS_HEALTH_CHECK_INTERVAL', 30))
            }
            
            logger.info(f"Redis configuration: {json.dumps(redis_config, indent=2)}")
            
            # Test Redis connection
            import redis
            r = redis.Redis.from_url(self.redis_url)
            r.ping()
            logger.info("Redis connection test successful")
            
            return True
        except Exception as e:
            logger.error(f"Redis configuration failed: {str(e)}")
            return False
    
    def configure_load_balancer(self):
        """Configure load balancer"""
        try:
            logger.info(f"Configuring {self.load_balancer_type} load balancer")
            
            if self.load_balancer_type == 'nginx':
                self._configure_nginx()
            elif self.load_balancer_type == 'haproxy':
                self._configure_haproxy()
            else:
                logger.warning(f"Unsupported load balancer type: {self.load_balancer_type}")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Load balancer configuration failed: {str(e)}")
            return False
    
    def _configure_nginx(self):
        """Configure Nginx as load balancer"""
        nginx_config = """
# Nginx load balancer configuration for MyShop
upstream myshop_backend {
    # Add your backend servers here
    server web1:8000 weight=3;
    server web2:8000 weight=3;
    server web3:8000 weight=2;
    
    # Load balancing method
    least_conn;
    
    # Health checks
    keepalive 32;
}

server {
    listen 80;
    server_name yourdomain.com;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    location / {
        proxy_pass http://myshop_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    location /static/ {
        alias /app/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /app/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
}
"""
        
        # Write configuration to file
        config_path = "/etc/nginx/conf.d/myshop.conf"
        try:
            with open(config_path, 'w') as f:
                f.write(nginx_config)
            logger.info(f"Nginx configuration written to {config_path}")
        except Exception as e:
            logger.warning(f"Could not write Nginx configuration file: {str(e)}")
            logger.info("Nginx configuration:")
            logger.info(nginx_config)
    
    def _configure_haproxy(self):
        """Configure HAProxy as load balancer"""
        haproxy_config = """
# HAProxy load balancer configuration for MyShop
global
    daemon
    maxconn 4096
    log /dev/log local0
    log /dev/log local1 notice

defaults
    mode http
    log global
    option httplog
    option dontlognull
    option httpclose
    option forwardfor
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms
    
    # Health checks
    option httpchk GET /health/
    http-check expect status 200

frontend myshop_frontend
    bind *:80
    default_backend myshop_backend
    
    # Security headers
    rspadd Strict-Transport-Security:\ max-age=31536000

backend myshop_backend
    balance leastconn
    
    # Backend servers
    server web1 web1:8000 check
    server web2 web2:8000 check
    server web3 web3:8000 check
"""
        
        # Write configuration to file
        config_path = "/etc/haproxy/haproxy.cfg"
        try:
            with open(config_path, 'w') as f:
                f.write(haproxy_config)
            logger.info(f"HAProxy configuration written to {config_path}")
        except Exception as e:
            logger.warning(f"Could not write HAProxy configuration file: {str(e)}")
            logger.info("HAProxy configuration:")
            logger.info(haproxy_config)
    
    def configure_caching(self):
        """Configure application-level caching"""
        try:
            logger.info("Configuring application-level caching")
            
            # This would typically involve setting up cache keys, expiration times, etc.
            cache_config = {
                "default_timeout": int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 300)),
                "product_cache_timeout": int(os.environ.get('CACHE_PRODUCT_TIMEOUT', 3600)),
                "category_cache_timeout": int(os.environ.get('CACHE_CATEGORY_TIMEOUT', 1800)),
                "session_cache_timeout": int(os.environ.get('CACHE_SESSION_TIMEOUT', 300))
            }
            
            logger.info(f"Cache configuration: {json.dumps(cache_config, indent=2)}")
            
            return True
        except Exception as e:
            logger.error(f"Cache configuration failed: {str(e)}")
            return False
    
    def setup_auto_scaling(self):
        """Set up auto-scaling policies"""
        try:
            logger.info("Setting up auto-scaling policies")
            
            # This is a simplified example. In a real AWS environment, you would use boto3
            # to configure auto-scaling groups, policies, and CloudWatch alarms.
            
            scaling_config = {
                "min_instances": int(os.environ.get('SCALING_MIN_INSTANCES', 2)),
                "max_instances": int(os.environ.get('SCALING_MAX_INSTANCES', 10)),
                "scale_up_threshold": int(os.environ.get('SCALING_UP_THRESHOLD', 70)),  # CPU percentage
                "scale_down_threshold": int(os.environ.get('SCALING_DOWN_THRESHOLD', 30)),  # CPU percentage
                "scale_up_step": int(os.environ.get('SCALING_UP_STEP', 1)),
                "scale_down_step": int(os.environ.get('SCALING_DOWN_STEP', 1))
            }
            
            logger.info(f"Auto-scaling configuration: {json.dumps(scaling_config, indent=2)}")
            
            # In a real implementation, you would use AWS SDK to create:
            # 1. Auto Scaling Group
            # 2. Launch Configuration
            # 3. Scaling Policies
            # 4. CloudWatch Alarms
            
            return True
        except Exception as e:
            logger.error(f"Auto-scaling setup failed: {str(e)}")
            return False
    
    def run_setup(self):
        """Run all scaling configuration steps"""
        logger.info("Starting scaling configuration setup")
        
        steps = [
            ("Redis Configuration", self.configure_redis),
            ("Load Balancer Configuration", self.configure_load_balancer),
            ("Caching Configuration", self.configure_caching),
            ("Auto-scaling Setup", self.setup_auto_scaling)
        ]
        
        results = []
        for step_name, step_func in steps:
            try:
                logger.info(f"Executing: {step_name}")
                result = step_func()
                results.append(result)
                if result:
                    logger.info(f"Completed: {step_name}")
                else:
                    logger.error(f"Failed: {step_name}")
            except Exception as e:
                logger.error(f"Error in {step_name}: {str(e)}")
                results.append(False)
        
        # Overall status
        if all(results):
            logger.info("All scaling configuration steps completed successfully")
            return True
        else:
            failed_steps = [steps[i][0] for i, result in enumerate(results) if not result]
            logger.error(f"Some scaling configuration steps failed: {failed_steps}")
            return False

def main():
    """Main scaling setup function"""
    logger.info("Starting scaling configuration setup")
    
    setup = ScalingSetup()
    status = setup.run_setup()
    
    if status:
        logger.info("Scaling configuration completed successfully")
        sys.exit(0)
    else:
        logger.error("Scaling configuration completed with issues")
        sys.exit(1)

if __name__ == "__main__":
    main()