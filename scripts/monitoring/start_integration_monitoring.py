#!/usr/bin/env python3
"""
Start Integration Monitoring Service

Starts the comprehensive integration validation and monitoring system
for the KGAS infrastructure and tools.
"""

import asyncio
import argparse
import logging
import signal
import sys
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.monitoring.integration_validator import (
    IntegrationValidator, 
    create_production_validator,
    create_development_validator
)

logger = logging.getLogger(__name__)


class MonitoringService:
    """Integration monitoring service"""
    
    def __init__(self, config_path: Optional[str] = None, mode: str = "production"):
        """Initialize monitoring service"""
        self.config_path = config_path
        self.mode = mode
        self.validator = None
        self._shutdown_event = asyncio.Event()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, initiating shutdown...")
        asyncio.create_task(self._shutdown())
    
    async def _shutdown(self):
        """Graceful shutdown"""
        self._shutdown_event.set()
    
    async def start(self) -> bool:
        """Start monitoring service"""
        try:
            # Create validator based on mode
            if self.mode == "production":
                self.validator = create_production_validator(self.config_path)
            elif self.mode == "development":
                self.validator = create_development_validator(self.config_path)
            else:
                self.validator = IntegrationValidator(self.config_path)
            
            logger.info(f"Starting integration monitoring in {self.mode} mode...")
            
            # Initialize components
            logger.info("Initializing monitoring components...")
            if not await self.validator.initialize_components():
                logger.error("Failed to initialize monitoring components")
                return False
            
            logger.info("Components initialized successfully")
            
            # Start monitoring
            logger.info("Starting continuous monitoring...")
            if not await self.validator.start_monitoring():
                logger.error("Failed to start monitoring")
                return False
            
            logger.info("Integration monitoring started successfully")
            
            # Wait for shutdown signal
            await self._shutdown_event.wait()
            
            # Graceful shutdown
            logger.info("Shutting down monitoring service...")
            await self.validator.stop_monitoring()
            await self.validator.cleanup()
            
            logger.info("Monitoring service stopped")
            return True
            
        except Exception as e:
            logger.error(f"Monitoring service failed: {e}", exc_info=True)
            return False
    
    async def status(self) -> dict:
        """Get monitoring status"""
        if not self.validator:
            return {"status": "not_started"}
        
        try:
            health_status = await self.validator.get_health_status()
            recent_alerts = await self.validator.get_recent_alerts(hours=1)
            
            return {
                "status": "running",
                "health": health_status,
                "recent_alerts_count": len(recent_alerts),
                "mode": self.mode
            }
            
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return {"status": "error", "error": str(e)}
    
    async def export_report(self, output_path: str) -> bool:
        """Export monitoring report"""
        if not self.validator:
            logger.error("Monitoring service not started")
            return False
        
        try:
            return await self.validator.export_monitoring_data(output_path)
        except Exception as e:
            logger.error(f"Failed to export report: {e}")
            return False


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="KGAS Integration Monitoring Service")
    parser.add_argument(
        "--config", 
        type=str, 
        help="Path to monitoring configuration file"
    )
    parser.add_argument(
        "--mode", 
        choices=["production", "development", "custom"],
        default="production",
        help="Monitoring mode (default: production)"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    parser.add_argument(
        "--command",
        choices=["start", "status", "export"],
        default="start",
        help="Command to execute (default: start)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output path for export command"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("logs/integration_monitoring.log")
        ]
    )
    
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    # Create monitoring service
    service = MonitoringService(args.config, args.mode)
    
    try:
        if args.command == "start":
            # Start monitoring service
            success = await service.start()
            sys.exit(0 if success else 1)
            
        elif args.command == "status":
            # Get status
            status = await service.status()
            print(f"Monitoring Status: {status}")
            sys.exit(0)
            
        elif args.command == "export":
            # Export report
            if not args.output:
                logger.error("Output path required for export command")
                sys.exit(1)
            
            success = await service.export_report(args.output)
            if success:
                print(f"Report exported to: {args.output}")
                sys.exit(0)
            else:
                logger.error("Failed to export report")
                sys.exit(1)
                
    except KeyboardInterrupt:
        logger.info("Monitoring service interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Monitoring service failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())