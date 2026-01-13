"""
Self-Healing Health Monitor
Monitors all services and automatically restarts failed components
"""
import asyncio
import httpx
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ServiceHealth:
    name: str
    url: str
    status: str  # healthy, degraded, down
    last_check: datetime
    consecutive_failures: int
    restart_count: int


class HealthMonitor:
    """
    Monitors service health and performs auto-recovery
    """
    
    def __init__(self, check_interval: int = 30, max_failures: int = 3):
        self.check_interval = check_interval
        self.max_failures = max_failures
        self.services: Dict[str, ServiceHealth] = {}
        self.running = False
        
    def register_service(self, name: str, url: str):
        """Register a service for monitoring"""
        self.services[name] = ServiceHealth(
            name=name,
            url=url,
            status="unknown",
            last_check=datetime.utcnow(),
            consecutive_failures=0,
            restart_count=0
        )
        logger.info(f"Registered service: {name} at {url}")
    
    async def check_service(self, service: ServiceHealth) -> bool:
        """Check if a service is healthy"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{service.url}/health")
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"Health check failed for {service.name}: {e}")
            return False
    
    async def restart_service(self, service: ServiceHealth) -> bool:
        """Attempt to restart a failed service"""
        logger.warning(f"Attempting to restart {service.name}")
        
        try:
            # Use docker compose to restart the service
            result = subprocess.run(
                ["docker", "compose", "restart", service.name.lower().replace(" ", "_")],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully restarted {service.name}")
                service.restart_count += 1
                service.consecutive_failures = 0
                return True
            else:
                logger.error(f"Failed to restart {service.name}: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error restarting {service.name}: {e}")
            return False
    
    async def monitor_loop(self):
        """Main monitoring loop"""
        logger.info("Health monitor started")
        self.running = True
        
        while self.running:
            for service in self.services.values():
                is_healthy = await self.check_service(service)
                service.last_check = datetime.utcnow()
                
                if is_healthy:
                    if service.status != "healthy":
                        logger.info(f"{service.name} is now healthy")
                    service.status = "healthy"
                    service.consecutive_failures = 0
                else:
                    service.consecutive_failures += 1
                    
                    if service.consecutive_failures >= self.max_failures:
                        service.status = "down"
                        logger.error(f"{service.name} is down (failures: {service.consecutive_failures})")
                        
                        # Attempt auto-recovery
                        if await self.restart_service(service):
                            # Wait for service to come back up
                            await asyncio.sleep(10)
                            if await self.check_service(service):
                                service.status = "healthy"
                                logger.info(f"{service.name} recovered successfully")
                    else:
                        service.status = "degraded"
                        logger.warning(f"{service.name} is degraded (failures: {service.consecutive_failures})")
            
            # Wait before next check
            await asyncio.sleep(self.check_interval)
    
    def get_status(self) -> Dict[str, dict]:
        """Get current status of all services"""
        return {
            name: {
                "status": service.status,
                "last_check": service.last_check.isoformat(),
                "consecutive_failures": service.consecutive_failures,
                "restart_count": service.restart_count
            }
            for name, service in self.services.items()
        }
    
    async def start(self):
        """Start the health monitor"""
        await self.monitor_loop()
    
    def stop(self):
        """Stop the health monitor"""
        self.running = False
        logger.info("Health monitor stopped")


# Standalone health monitor service
async def main():
    monitor = HealthMonitor(check_interval=30, max_failures=3)
    
    # Register services
    monitor.register_service("HP OMEN", "http://hp-omen:8080")
    monitor.register_service("Lenovo API", "http://lenovo:8088")
    monitor.register_service("PostgreSQL", "http://lenovo:54328")  # Would need health endpoint
    monitor.register_service("Redis", "http://lenovo:63798")  # Would need health endpoint
    
    # Start monitoring
    try:
        await monitor.start()
    except KeyboardInterrupt:
        monitor.stop()
        logger.info("Shutting down health monitor")


if __name__ == "__main__":
    asyncio.run(main())
