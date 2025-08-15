#!/usr/bin/env python3
"""
Integration Monitoring Dashboard

Provides a web-based dashboard for monitoring the KGAS integration system
with real-time health status, alerts, and performance metrics.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.monitoring.integration_validator import IntegrationValidator, create_production_validator

logger = logging.getLogger(__name__)


class MonitoringDashboard:
    """Web-based monitoring dashboard"""
    
    def __init__(self, validator: IntegrationValidator, port: int = 8080):
        """Initialize dashboard"""
        self.validator = validator
        self.port = port
        self.app = None
        
    async def create_app(self):
        """Create web application"""
        try:
            from aiohttp import web, web_response
            import aiohttp_cors
            
            app = web.Application()
            
            # Setup CORS
            cors = aiohttp_cors.setup(app, defaults={
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers="*",
                    allow_headers="*",
                    allow_methods="*"
                )
            })
            
            # Routes
            app.router.add_get('/', self._handle_dashboard)
            app.router.add_get('/api/health', self._handle_health)
            app.router.add_get('/api/alerts', self._handle_alerts)
            app.router.add_get('/api/metrics', self._handle_metrics)
            app.router.add_get('/api/export', self._handle_export)
            app.router.add_static('/static', Path(__file__).parent / 'static')
            
            # Add CORS to all routes
            for route in list(app.router.routes()):
                cors.add(route)
            
            self.app = app
            return app
            
        except ImportError:
            logger.error("aiohttp not available. Install with: pip install aiohttp aiohttp-cors")
            return None
    
    async def _handle_dashboard(self, request):
        """Serve dashboard HTML"""
        html_content = self._generate_dashboard_html()
        return web_response.Response(text=html_content, content_type='text/html')
    
    async def _handle_health(self, request):
        """Handle health status API"""
        try:
            health_status = await self.validator.get_health_status()
            return web_response.json_response(health_status)
        except Exception as e:
            logger.error(f"Health API error: {e}")
            return web_response.json_response(
                {"error": str(e)}, 
                status=500
            )
    
    async def _handle_alerts(self, request):
        """Handle alerts API"""
        try:
            hours = int(request.query.get('hours', 24))
            alerts = await self.validator.get_recent_alerts(hours=hours)
            return web_response.json_response({"alerts": alerts})
        except Exception as e:
            logger.error(f"Alerts API error: {e}")
            return web_response.json_response(
                {"error": str(e)}, 
                status=500
            )
    
    async def _handle_metrics(self, request):
        """Handle metrics API"""
        try:
            # Get infrastructure metrics
            metrics = {}
            if self.validator.infrastructure_integrator:
                metrics = self.validator.infrastructure_integrator.get_integration_metrics()
            
            # Add system metrics
            import psutil
            system_metrics = {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'timestamp': datetime.now().isoformat()
            }
            
            return web_response.json_response({
                "infrastructure_metrics": metrics,
                "system_metrics": system_metrics
            })
            
        except Exception as e:
            logger.error(f"Metrics API error: {e}")
            return web_response.json_response(
                {"error": str(e)}, 
                status=500
            )
    
    async def _handle_export(self, request):
        """Handle data export API"""
        try:
            # Create temporary export file
            export_path = f"temp_monitoring_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            success = await self.validator.export_monitoring_data(export_path)
            if success:
                # Read and return file content
                with open(export_path, 'r') as f:
                    data = json.load(f)
                
                # Clean up temp file
                Path(export_path).unlink()
                
                return web_response.json_response(data)
            else:
                return web_response.json_response(
                    {"error": "Export failed"}, 
                    status=500
                )
                
        except Exception as e:
            logger.error(f"Export API error: {e}")
            return web_response.json_response(
                {"error": str(e)}, 
                status=500
            )
    
    def _generate_dashboard_html(self) -> str:
        """Generate dashboard HTML"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KGAS Integration Monitoring Dashboard</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .header h1 {
            margin: 0;
            color: #333;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .status-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .status-card h3 {
            margin-top: 0;
            color: #333;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-healthy { background-color: #28a745; }
        .status-warning { background-color: #ffc107; }
        .status-critical { background-color: #dc3545; }
        .status-unknown { background-color: #6c757d; }
        .metrics-section {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .alert-item {
            padding: 10px;
            margin: 5px 0;
            border-left: 4px solid;
            background: #f8f9fa;
        }
        .alert-critical { border-left-color: #dc3545; }
        .alert-error { border-left-color: #fd7e14; }
        .alert-warning { border-left-color: #ffc107; }
        .alert-info { border-left-color: #17a2b8; }
        .refresh-btn {
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            margin: 10px 0;
        }
        .refresh-btn:hover {
            background: #0056b3;
        }
        .timestamp {
            color: #6c757d;
            font-size: 0.9em;
        }
        .metric-value {
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
        }
        .progress-bar {
            width: 100%;
            height: 20px;
            background-color: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin: 5px 0;
        }
        .progress-fill {
            height: 100%;
            transition: width 0.3s ease;
        }
        .progress-normal { background-color: #28a745; }
        .progress-warning { background-color: #ffc107; }
        .progress-danger { background-color: #dc3545; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 KGAS Integration Monitoring Dashboard</h1>
            <button class="refresh-btn" onclick="refreshAll()">🔄 Refresh All</button>
            <button class="refresh-btn" onclick="exportData()">📁 Export Data</button>
            <span class="timestamp" id="lastUpdate">Last updated: Loading...</span>
        </div>

        <div class="status-grid">
            <div class="status-card">
                <h3>🏗️ Infrastructure Status</h3>
                <div id="infrastructureStatus">Loading...</div>
            </div>
            
            <div class="status-card">
                <h3>⚙️ Services Status</h3>
                <div id="servicesStatus">Loading...</div>
            </div>
            
            <div class="status-card">
                <h3>🔧 Tools Status</h3>
                <div id="toolsStatus">Loading...</div>
            </div>
            
            <div class="status-card">
                <h3>📊 Performance Status</h3>
                <div id="performanceStatus">Loading...</div>
            </div>
        </div>

        <div class="metrics-section">
            <h3>📈 System Metrics</h3>
            <div id="systemMetrics">Loading...</div>
        </div>

        <div class="metrics-section">
            <h3>🚨 Recent Alerts</h3>
            <div id="recentAlerts">Loading...</div>
        </div>
    </div>

    <script>
        let refreshInterval;

        function getStatusIcon(status) {
            const icons = {
                'healthy': '✅',
                'warning': '⚠️',
                'critical': '❌',
                'unknown': '❓'
            };
            return icons[status] || '❓';
        }

        function getStatusClass(status) {
            return `status-${status}`;
        }

        function formatTimestamp(timestamp) {
            return new Date(timestamp).toLocaleString();
        }

        function createProgressBar(value, max, type = 'normal') {
            const percentage = Math.min((value / max) * 100, 100);
            let colorClass = 'progress-normal';
            
            if (percentage > 85) colorClass = 'progress-danger';
            else if (percentage > 70) colorClass = 'progress-warning';
            
            return `
                <div class="progress-bar">
                    <div class="progress-fill ${colorClass}" style="width: ${percentage}%"></div>
                </div>
                <small>${value.toFixed(1)}% of ${max}%</small>
            `;
        }

        async function refreshHealth() {
            try {
                const response = await fetch('/api/health');
                const data = await response.json();
                
                // Update overall status indicators
                const components = data.components || {};
                
                for (const [component, info] of Object.entries(components)) {
                    const elementId = component + 'Status';
                    const element = document.getElementById(elementId);
                    
                    if (element) {
                        element.innerHTML = `
                            <div>
                                <span class="status-indicator ${getStatusClass(info.status)}"></span>
                                ${getStatusIcon(info.status)} ${info.status.toUpperCase()}
                            </div>
                            <div style="margin-top: 8px; color: #666;">
                                ${info.message}
                            </div>
                            <div class="timestamp">
                                Last check: ${formatTimestamp(info.last_check)}
                            </div>
                        `;
                    }
                }
                
            } catch (error) {
                console.error('Failed to refresh health:', error);
            }
        }

        async function refreshMetrics() {
            try {
                const response = await fetch('/api/metrics');
                const data = await response.json();
                
                const systemMetrics = data.system_metrics || {};
                const infraMetrics = data.infrastructure_metrics || {};
                
                const metricsHtml = `
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                        <div>
                            <h4>💻 CPU Usage</h4>
                            ${createProgressBar(systemMetrics.cpu_percent || 0, 100)}
                        </div>
                        <div>
                            <h4>🧠 Memory Usage</h4>
                            ${createProgressBar(systemMetrics.memory_percent || 0, 100)}
                        </div>
                        <div>
                            <h4>💿 Disk Usage</h4>
                            ${createProgressBar(systemMetrics.disk_percent || 0, 100)}
                        </div>
                        <div>
                            <h4>📦 Cache Hit Rate</h4>
                            <div class="metric-value">
                                ${infraMetrics.performance_metrics?.cache_hit_rate || 'N/A'}
                            </div>
                        </div>
                        <div>
                            <h4>⚡ Average Speedup</h4>
                            <div class="metric-value">
                                ${infraMetrics.performance_metrics?.average_speedup || 'N/A'}
                            </div>
                        </div>
                        <div>
                            <h4>🔄 Total Operations</h4>
                            <div class="metric-value">
                                ${infraMetrics.performance_metrics?.total_operations || 'N/A'}
                            </div>
                        </div>
                    </div>
                `;
                
                document.getElementById('systemMetrics').innerHTML = metricsHtml;
                
            } catch (error) {
                console.error('Failed to refresh metrics:', error);
            }
        }

        async function refreshAlerts() {
            try {
                const response = await fetch('/api/alerts?hours=24');
                const data = await response.json();
                
                const alerts = data.alerts || [];
                
                let alertsHtml = '';
                if (alerts.length === 0) {
                    alertsHtml = '<div style="color: #28a745;">✅ No alerts in the last 24 hours</div>';
                } else {
                    alertsHtml = alerts.map(alert => `
                        <div class="alert-item alert-${alert.severity}">
                            <strong>${alert.severity.toUpperCase()}</strong> - ${alert.component}
                            <br>
                            ${alert.message}
                            <br>
                            <span class="timestamp">${formatTimestamp(alert.triggered_at)}</span>
                        </div>
                    `).join('');
                }
                
                document.getElementById('recentAlerts').innerHTML = alertsHtml;
                
            } catch (error) {
                console.error('Failed to refresh alerts:', error);
            }
        }

        async function refreshAll() {
            document.getElementById('lastUpdate').textContent = `Last updated: ${new Date().toLocaleString()}`;
            
            await Promise.all([
                refreshHealth(),
                refreshMetrics(),
                refreshAlerts()
            ]);
        }

        async function exportData() {
            try {
                const response = await fetch('/api/export');
                const data = await response.json();
                
                const blob = new Blob([JSON.stringify(data, null, 2)], {
                    type: 'application/json'
                });
                
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `kgas_monitoring_export_${new Date().toISOString().slice(0,10)}.json`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                
            } catch (error) {
                console.error('Failed to export data:', error);
                alert('Failed to export data: ' + error.message);
            }
        }

        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            refreshAll();
            
            // Auto-refresh every 30 seconds
            refreshInterval = setInterval(refreshAll, 30000);
        });

        // Clean up on page unload
        window.addEventListener('beforeunload', function() {
            if (refreshInterval) {
                clearInterval(refreshInterval);
            }
        });
    </script>
</body>
</html>
        """
    
    async def start(self):
        """Start dashboard server"""
        from aiohttp import web
        
        if not self.app:
            await self.create_app()
        
        if not self.app:
            logger.error("Failed to create web application")
            return False
        
        try:
            runner = web.AppRunner(self.app)
            await runner.setup()
            
            site = web.TCPSite(runner, 'localhost', self.port)
            await site.start()
            
            logger.info(f"Dashboard started at http://localhost:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start dashboard: {e}")
            return False


async def main():
    """Main entry point for dashboard"""
    import argparse
    
    parser = argparse.ArgumentParser(description="KGAS Integration Monitoring Dashboard")
    parser.add_argument("--port", type=int, default=8080, help="Dashboard port (default: 8080)")
    parser.add_argument("--config", type=str, help="Path to monitoring configuration file")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Create validator
        validator = create_production_validator(args.config)
        
        # Initialize components
        logger.info("Initializing monitoring components...")
        if not await validator.initialize_components():
            logger.error("Failed to initialize monitoring components")
            return 1
        
        # Start monitoring
        logger.info("Starting monitoring...")
        if not await validator.start_monitoring():
            logger.error("Failed to start monitoring")
            return 1
        
        # Create and start dashboard
        dashboard = MonitoringDashboard(validator, args.port)
        if not await dashboard.start():
            logger.error("Failed to start dashboard")
            return 1
        
        logger.info(f"Dashboard available at http://localhost:{args.port}")
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Dashboard stopped by user")
        
        # Cleanup
        await validator.stop_monitoring()
        await validator.cleanup()
        
        return 0
        
    except Exception as e:
        logger.error(f"Dashboard failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))