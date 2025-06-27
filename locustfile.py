"""
Locust performance testing file for E-commerce Promotion API.

This file simulates realistic traffic patterns for an e-commerce promotion campaign
that tracks user interactions and displays visit counts as part of publicity efforts.

Endpoints tested:
- POST /visit: Log user visits to the promotion (returns total visitor count)
- GET /stats: Get promotion statistics and visitor metrics
- GET /health: Health check endpoint

Usage:
    locust --host=http://localhost:8080
    locust --host=http://localhost:8080 --users 10 --spawn-rate 2
"""

import json
import random
import time
from locust import HttpUser, task, between


class WebVisitUser(HttpUser):
    """
    Simulates regular website visitors during an e-commerce promotion.
    
    This user class models realistic customer behavior:
    - Customers browsing different pages of the e-commerce site
    - Realistic timing between page visits
    - Each visit contributes to the promotion's visitor count display
    """
    
    # Wait between 1-5 seconds between tasks (realistic user behavior)
    wait_time = between(1, 5)
    
    def on_start(self):
        """Initialize user session and verify API is healthy."""
        # Check if the API is healthy before starting tests
        response = self.client.get("/health")
        if response.status_code != 200:
            print(f"⚠️  API health check failed: {response.status_code}")
    
    @task(5)
    def log_visit(self):
        """
        Log a user visit (most common operation).
        
        Weight: 5 (happens 5x more often than stats check)
        This simulates users browsing different pages on a website.
        """
        # Generate realistic visit data
        user_id = f"user_{random.randint(1, 1000)}"
        pages = [
            "https://example.com/",
            "https://example.com/products",
            "https://example.com/about",
            "https://example.com/contact",
            "https://example.com/blog",
            "https://example.com/pricing",
            "https://example.com/features",
            "https://example.com/support",
        ]
        
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X)",
            "Mozilla/5.0 (Android 11; Mobile; rv:92.0) Gecko/92.0",
        ]
        
        referrers = [
            "https://google.com/search?q=example",
            "https://twitter.com/",
            "https://facebook.com/",
            "https://linkedin.com/",
            "",  # Direct visit
        ]
        
        visit_data = {
            "user_id": user_id,
            "page_url": random.choice(pages),
            "user_agent": random.choice(user_agents),
            "referrer": random.choice(referrers),
            # IP address will be auto-detected by the API
        }
        
        with self.client.post(
            "/visit",
            json=visit_data,
            headers={"Content-Type": "application/json"},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("success"):
                        response.success()
                    else:
                        response.failure(f"Visit not successful: {data}")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"HTTP {response.status_code}: {response.text}")
    
    @task(1)
    def test_root_endpoint(self):
        """
        Test root endpoint (occasional API discovery).
        
        Weight: 1 (users discovering the API)
        This simulates users or developers exploring the API.
        """
        with self.client.get("/", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "message" in data and "Traffic Tracker API" in data["message"]:
                        response.success()
                    else:
                        response.failure(f"Unexpected root response: {data}")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"HTTP {response.status_code}: {response.text}")


class AdminUser(HttpUser):
    """
    Heavy stats user simulating admin/monitoring behavior.
    
    This user focuses primarily on statistics and monitoring,
    representing admin users or monitoring systems.
    """
    
    wait_time = between(2, 10)  # Less frequent, longer intervals
    weight = 1  # Fewer admin users compared to regular users
    
    @task(3)
    def detailed_stats_check(self):
        """Check stats with various timeframes for monitoring."""
        timeframes = [0.1, 1.0, 6.0, 24.0, 168.0]  # Different monitoring intervals
        
        for timeframe in timeframes:
            self.client.get(f"/stats?timeframe_hours={timeframe}")
            time.sleep(0.5)  # Brief pause between requests
    
    @task(2)
    def health_monitoring(self):
        """Continuous health monitoring."""
        self.client.get("/health")
    
        
    @task(1)
    def check_stats(self):
        """
        Check server statistics (less frequent operation).
        
        Weight: 1 (happens less frequently than visits)
        This simulates admins or monitoring systems checking stats.
        """
        # Test different timeframe parameters
        timeframes = [0.1, 0.5, 1.0, 2.0, 6.0, 24.0, 168.0]  # 6min to 1 week
        timeframe = random.choice(timeframes)
        
        with self.client.get(
            f"/stats?timeframe_hours={timeframe}",
            catch_response=True,
            name="/stats"  # Group all stats requests under one name
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    required_fields = [
                        "uptime_seconds", "total_visits", "current_time",
                        "server_status", "recent_visits", "timeframe_hours"
                    ]
                    
                    if all(field in data for field in required_fields):
                        if data["server_status"] == "running":
                            response.success()
                        else:
                            response.failure(f"Server not running: {data['server_status']}")
                    else:
                        missing = [f for f in required_fields if f not in data]
                        response.failure(f"Missing fields: {missing}")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"HTTP {response.status_code}: {response.text}")
    
    @task(1)
    def api_discovery(self):
        """Explore API endpoints."""
        endpoints = ["/", "/docs", "/redoc"]
        for endpoint in endpoints:
            self.client.get(endpoint)
            time.sleep(0.2)


class BurstUser(HttpUser):
    """
    Simulates burst traffic patterns.
    
    This user creates sudden spikes in traffic to test
    how the API handles load bursts.
    """
    
    wait_time = between(0.1, 1)  # Very fast requests
    weight = 1  # Occasional burst users
    
    @task
    def burst_visits(self):
        """Create a burst of visit requests."""
        for i in range(random.randint(3, 8)):
            visit_data = {
                "user_id": f"burst_user_{random.randint(1, 100)}",
                "page_url": f"https://example.com/page_{i}",
                "user_agent": "BurstTestAgent/1.0",
            }
            self.client.post("/visit", json=visit_data)
            time.sleep(0.1)  # Very brief pause


# Configuration for different load testing scenarios
class LightLoad(WebVisitUser):
    """Light load testing configuration."""
    weight = 10
    wait_time = between(3, 8)


class HeavyLoad(WebVisitUser):
    """Heavy load testing configuration."""
    weight = 5
    wait_time = between(0.5, 2)


if __name__ == "__main__":
    print("🔥 Locust file for E-commerce Promotion API")
    print("📊 Available user classes:")
    print("   - WebVisitUser: Regular website visitors (primary traffic)")
    print("   - AdminUser: Admin/monitoring behavior for promotion stats")
    print("   - BurstUser: Sudden traffic spikes during promotion")
    print("   - LightLoad: Light load testing configuration")
    print("   - HeavyLoad: Heavy load testing configuration")
    print("\n🚀 Usage examples:")
    print("   locust --host=http://localhost:8080")
    print("   locust --host=http://localhost:8080 --users 50 --spawn-rate 5")
    print("   locust -f locustfile.py --host=http://localhost:8080 WebVisitUser")