#!/usr/bin/env python
"""
Monitoring and alerting script for MyShop e-commerce platform
This script monitors system health and sends alerts when issues are detected
"""

import os
import sys
import boto3
import requests
import smtplib
import logging
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import psycopg2
import redis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SystemMonitor:
    """System monitoring class"""
    
    def __init__(self):
        self.alerts_enabled = os.environ.get('ALERTS_ENABLED', 'true').lower() == 'true'
        self.alert_email = os.environ.get('ALERT_EMAIL')
        self.smtp_server = os.environ.get('SMTP_SERVER')
        self.smtp_port = int(os.environ.get('SMTP_PORT', 587))
        self.smtp_user = os.environ.get('SMTP_USER')
        self.smtp_password = os.environ.get('SMTP_PASSWORD')
        
    def check_database_connection(self):
        """Check if database is accessible"""
        try:
            conn = psycopg2.connect(
                dbname=os.environ.get('DB_NAME'),
                user=os.environ.get('DB_USER'),
                password=os.environ.get('DB_PASSWORD'),
                host=os.environ.get('DB_HOST'),
                port=os.environ.get('DB_PORT', '5432')
            )
            conn.close()
            logger.info("Database connection: OK")
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {str(e)}")
            self.send_alert("Database connection failed", str(e))
            return False
    
    def check_redis_connection(self):
        """Check if Redis is accessible"""
        try:
            redis_client = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/1'))
            redis_client.ping()
            logger.info("Redis connection: OK")
            return True
        except Exception as e:
            logger.error(f"Redis connection failed: {str(e)}")
            self.send_alert("Redis connection failed", str(e))
            return False
    
    def check_web_server(self):
        """Check if web server is responding"""
        try:
            domain = os.environ.get('DOMAIN', 'localhost:8000')
            if not domain.startswith('http'):
                domain = f"http://{domain}"
                
            response = requests.get(domain, timeout=10)
            if response.status_code == 200:
                logger.info("Web server: OK")
                return True
            else:
                logger.error(f"Web server returned status code: {response.status_code}")
                self.send_alert("Web server issue", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Web server check failed: {str(e)}")
            self.send_alert("Web server unreachable", str(e))
            return False
    
    def check_disk_space(self):
        """Check disk space usage"""
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            usage_percent = (used / total) * 100
            
            logger.info(f"Disk usage: {usage_percent:.2f}%")
            
            if usage_percent > 90:
                logger.warning("Disk space critically low")
                self.send_alert("Disk space critically low", f"Usage: {usage_percent:.2f}%")
                return False
            elif usage_percent > 80:
                logger.warning("Disk space low")
                return True
            else:
                logger.info("Disk space: OK")
                return True
        except Exception as e:
            logger.error(f"Disk space check failed: {str(e)}")
            return False
    
    def check_memory_usage(self):
        """Check memory usage"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            usage_percent = memory.percent
            
            logger.info(f"Memory usage: {usage_percent:.2f}%")
            
            if usage_percent > 90:
                logger.warning("Memory usage critically high")
                self.send_alert("Memory usage critically high", f"Usage: {usage_percent:.2f}%")
                return False
            elif usage_percent > 80:
                logger.warning("Memory usage high")
                return True
            else:
                logger.info("Memory usage: OK")
                return True
        except Exception as e:
            logger.error(f"Memory usage check failed: {str(e)}")
            return False
    
    def check_cpu_usage(self):
        """Check CPU usage"""
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            
            logger.info(f"CPU usage: {cpu_percent:.2f}%")
            
            if cpu_percent > 90:
                logger.warning("CPU usage critically high")
                self.send_alert("CPU usage critically high", f"Usage: {cpu_percent:.2f}%")
                return False
            elif cpu_percent > 80:
                logger.warning("CPU usage high")
                return True
            else:
                logger.info("CPU usage: OK")
                return True
        except Exception as e:
            logger.error(f"CPU usage check failed: {str(e)}")
            return False
    
    def send_alert(self, subject, message):
        """Send alert notification"""
        if not self.alerts_enabled:
            logger.info("Alerts disabled, skipping notification")
            return
            
        if not all([self.alert_email, self.smtp_server, self.smtp_user, self.smtp_password]):
            logger.warning("Alert configuration incomplete, skipping notification")
            return
            
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = self.alert_email
            msg['Subject'] = f"MyShop Alert: {subject}"
            
            body = f"""
            MyShop System Alert
            
            Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            Subject: {subject}
            Message: {message}
            
            Please check the system immediately.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            text = msg.as_string()
            server.sendmail(self.smtp_user, self.alert_email, text)
            server.quit()
            
            logger.info(f"Alert sent: {subject}")
        except Exception as e:
            logger.error(f"Failed to send alert: {str(e)}")
    
    def run_health_checks(self):
        """Run all health checks"""
        logger.info("Starting system health checks")
        
        checks = [
            self.check_database_connection,
            self.check_redis_connection,
            self.check_web_server,
            self.check_disk_space,
            self.check_memory_usage,
            self.check_cpu_usage
        ]
        
        results = []
        for check in checks:
            try:
                result = check()
                results.append(result)
            except Exception as e:
                logger.error(f"Error running check {check.__name__}: {str(e)}")
                results.append(False)
        
        # Overall system status
        if all(results):
            logger.info("All system checks passed")
            return True
        else:
            failed_checks = [checks[i].__name__ for i, result in enumerate(results) if not result]
            logger.error(f"Some system checks failed: {failed_checks}")
            return False

def main():
    """Main monitoring function"""
    logger.info("Starting system monitoring")
    
    monitor = SystemMonitor()
    status = monitor.run_health_checks()
    
    if status:
        logger.info("System monitoring completed successfully")
        sys.exit(0)
    else:
        logger.error("System monitoring completed with issues")
        sys.exit(1)

if __name__ == "__main__":
    main()