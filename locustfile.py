"""
Locust performance testing file for E-commerce Promotion Buy Tracker API.

This file simulates realistic traffic patterns for an e-commerce promotion campaign
that tracks customer purchases and provides analytics for promotion effectiveness.

Endpoints tested:
- POST /buy: Log customer purchases on promotional pages
- GET /stats: Get promotion analytics and buy metrics  
- GET /health: Health check endpoint

User Types:
- CustomerUser: Simulates customers making purchases (high volume)
- AdminUser: Simulates admins monitoring campaign performance (low volume)

Usage:
    locust --host=http://localhost:8080
    locust --host=http://localhost:8080 --users 50 --spawn-rate 5
"""

import json
import random
import time
from locust import HttpUser, task, between


class CustomerUser(HttpUser):
    """
    Simulates customers making purchases during e-commerce promotion campaigns.
    
    This user class models realistic customer buying behavior:
    - Making purchases on different promotional products
    - Realistic timing between purchases
    - Each purchase contributes to promotion analytics
    
    Weight: 20 (majority of traffic should be customers)
    """
    
    weight = 20  # High weight - most users should be customers
    wait_time = between(2, 8)  # Realistic time between purchases
    
    def on_start(self):
        """Initialize customer session and verify API is healthy."""
        response = self.client.get("/health")
        if response.status_code != 200:
            print(f"⚠️  API health check failed: {response.status_code}")
    
    @task(10)
    def make_purchase(self):
        """
        Log a customer purchase (primary customer action).
        
        Weight: 10 (main customer behavior)
        Simulates customers buying products during promotional campaigns.
        """
        # Generate realistic purchase data
        user_id = random.randint(1000, 50000)  # Customer ID range
        promotion_id = random.randint(1, 10)   # Limited number of active promotions
        product_id = random.randint(100, 999)  # Product catalog range
        
        # Realistic purchase amounts for promotional products
        product_amounts = [
            9.99, 19.99, 29.99, 39.99, 49.99, 59.99, 69.99, 79.99, 89.99, 99.99,
            149.99, 199.99, 249.99, 299.99, 399.99, 499.99, 599.99, 799.99, 999.99
        ]
        product_amount = random.choice(product_amounts)
        
        purchase_data = {
            "user_id": user_id,
            "promotion_id": promotion_id,
            "product_id": product_id,
            "product_amount": product_amount
        }
        
        # Add timestamp header for accurate analytics (simulating real client)
        headers = {
            "Content-Type": "application/json",
            "x-client-time": str(int(time.time()))  # Unix timestamp
        }
        
        with self.client.post(
            "/buy",
            json=purchase_data,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("success"):
                        response.success()  # type: ignore
                        # Optional: Log successful purchase for debugging
                        # print(f"✅ Purchase: User {user_id}, Product ${product_amount}")
                    else:
                        response.failure(f"Purchase not successful: {data}")  # type: ignore
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")  # type: ignore
            else:
                response.failure(f"HTTP {response.status_code}: {response.text}")  # type: ignore
    
    @task(2)
    def high_value_purchase(self):
        """
        Simulate high-value purchases (less frequent but important for analytics).
        
        Weight: 2 (occasional high-value customers)
        """
        user_id = random.randint(1000, 50000)
        promotion_id = random.randint(1, 5)  # Premium promotions
        product_id = random.randint(800, 999)  # Premium products
        
        # High-value purchase amounts
        high_value_amounts = [999.99, 1499.99, 1999.99, 2499.99, 2999.99, 3999.99, 4999.99]
        product_amount = random.choice(high_value_amounts)
        
        purchase_data = {
            "user_id": user_id,
            "promotion_id": promotion_id,
            "product_id": product_id,
            "product_amount": product_amount
        }
        
        headers = {
            "Content-Type": "application/json",
            "x-timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())  # ISO timestamp
        }
        
        self.client.post("/buy", json=purchase_data, headers=headers)


class AdminUser(HttpUser):
    """
    Simulates admin users monitoring promotion campaign performance.
    
    This user focuses on analytics, monitoring, and system health checks.
    Admins need to track campaign effectiveness and ensure system stability.
    
    Weight: 1 (few admin users compared to customers)
    """
    
    weight = 1  # Low weight - only a few admin users
    wait_time = between(5, 15)  # Admins check less frequently but more thoroughly
    
    def on_start(self):
        """Initialize admin session with comprehensive health check."""
        print(f"🔧 Admin user starting monitoring session")
        response = self.client.get("/health")
        if response.status_code != 200:
            print(f"❌ Admin detected API health issue: {response.status_code}")
    
    @task(5)
    def monitor_campaign_performance(self):
        """
        Primary admin task: Monitor campaign performance with detailed analytics.
        
        Weight: 5 (main admin responsibility)
        Checks various timeframes for comprehensive campaign analysis.
        """
        # Admin checks multiple timeframes for complete campaign overview
        timeframes = [
            (0.1, "6 minutes"),     # Very recent activity
            (1.0, "1 hour"),        # Recent hourly performance  
            (6.0, "6 hours"),       # Daily performance trends
            (24.0, "24 hours"),     # Daily campaign results
            (168.0, "1 week")       # Weekly campaign overview
        ]
        
        for timeframe_hours, description in timeframes:
            with self.client.get(
                f"/stats?timeframe_hours={timeframe_hours}",
                catch_response=True,
                name=f"/stats?timeframe_hours={timeframe_hours}"
            ) as response:
                if response.status_code == 200:
                    try:
                        data = response.json()
                        required_fields = [
                            "uptime_seconds", "total_buys", "current_time",
                            "server_status", "n_recent_buys", "timeframe_hours"
                        ]
                        
                        if all(field in data for field in required_fields):
                            if data["server_status"] == "healthy":
                                response.success()  # type: ignore
                                # Optional: Log campaign metrics for admin visibility
                                # print(f"📊 {description}: {data['n_recent_buys']} buys, Total: {data['total_buys']}")
                            else:
                                response.failure(f"Server unhealthy: {data['server_status']}")  # type: ignore
                        else:
                            missing = [f for f in required_fields if f not in data]
                            response.failure(f"Missing analytics fields: {missing}")  # type: ignore
                    except json.JSONDecodeError:
                        response.failure("Invalid JSON response")  # type: ignore
                else:
                    response.failure(f"HTTP {response.status_code}: {response.text}")  # type: ignore
            
            # Brief pause between timeframe checks
            time.sleep(0.3)
    
    @task(4)
    def system_health_monitoring(self):
        """
        Continuous system health monitoring.
        
        Weight: 4 (critical admin responsibility)
        Ensures the purchase tracking system is stable during campaigns.
        """
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("status") == "healthy":
                        response.success()  # type: ignore
                    else:
                        response.failure(f"System unhealthy: {data}")  # type: ignore
                        print(f"🚨 Admin alert: System health issue detected!")
                except json.JSONDecodeError:
                    response.failure("Invalid health check JSON")  # type: ignore
            else:
                response.failure(f"Health check failed: HTTP {response.status_code}")  # type: ignore
    
    @task(3)
    def real_time_analytics(self):
        """
        Real-time analytics monitoring for active campaign management.
        
        Weight: 3 (important for campaign optimization)
        Focuses on short-term metrics for immediate decision making.
        """
        # Focus on real-time and short-term metrics
        real_time_frames = [0.1, 0.5, 1.0, 2.0]  # 6min to 2 hours
        
        for timeframe in real_time_frames:
            self.client.get(f"/stats?timeframe_hours={timeframe}")
            time.sleep(0.2)
    
    @task(2)
    def api_documentation_check(self):
        """
        Check API documentation and endpoints (admin maintenance).
        
        Weight: 2 (periodic admin maintenance)
        """
        documentation_endpoints = ["/", "/docs", "/redoc"]
        
        for endpoint in documentation_endpoints:
            with self.client.get(endpoint, catch_response=True) as response:
                if response.status_code == 200:
                    response.success()  # type: ignore
                else:
                    response.failure(f"Documentation endpoint failed: {endpoint}")  # type: ignore
            time.sleep(0.5)
    
    @task(1) 
    def campaign_deep_dive(self):
        """
        Comprehensive campaign analysis (periodic deep monitoring).
        
        Weight: 1 (thorough but infrequent analysis)
        """
        print(f"🔍 Admin performing campaign deep dive analysis")
        
        # Get comprehensive stats
        response = self.client.get("/stats?timeframe_hours=24.0")
        if response.status_code == 200:
            try:
                data = response.json()
                total_buys = data.get("total_buys", 0)
                recent_buys = data.get("n_recent_buys", 0)
                uptime = data.get("uptime_formatted", "unknown")
                
                print(f"📈 Campaign metrics - Total: {total_buys}, 24h: {recent_buys}, Uptime: {uptime}")
                
                # Simulate admin decision making based on metrics
                if recent_buys < 10:
                    print(f"⚠️  Admin notice: Low purchase activity in last 24h ({recent_buys} buys)")
                elif recent_buys > 1000:
                    print(f"🚀 Admin notice: High purchase activity in last 24h ({recent_buys} buys)")
                    
            except json.JSONDecodeError:
                print(f"❌ Admin error: Invalid analytics data")


# Legacy user classes for backward compatibility and specialized testing
class BurstCustomer(CustomerUser):
    """
    Simulates burst customer traffic during flash sales or viral promotions.
    
    Creates sudden spikes in purchase activity to test system resilience
    during high-traffic promotional events.
    """
    
    weight = 2  # Occasional burst traffic
    wait_time = between(0.1, 1)  # Very frequent purchases during bursts
    
    @task
    def flash_sale_purchases(self):
        """Create burst of purchases simulating flash sale traffic."""
        burst_size = random.randint(3, 6)
        flash_sale_promotion = random.randint(1, 3)  # Limited flash sale promotions
        
        for i in range(burst_size):
            user_id = random.randint(10000, 99999)  # Flash sale customer range
            product_id = random.randint(100, 200)   # Flash sale products
            
            # Flash sale pricing
            flash_prices = [9.99, 14.99, 19.99, 24.99, 29.99, 39.99]
            product_amount = random.choice(flash_prices)
            
            purchase_data = {
                "user_id": user_id,
                "promotion_id": flash_sale_promotion,
                "product_id": product_id,
                "product_amount": product_amount
            }
            
            # Add request start header (simulating load balancer timing)
            headers = {
                "Content-Type": "application/json",
                "x-request-start": str(int(time.time() * 1000))  # Milliseconds
            }
            
            self.client.post("/buy", json=purchase_data, headers=headers)
            time.sleep(0.05)  # Very brief pause between burst purchases


# Configuration classes for different load testing scenarios  
class LightTraffic(CustomerUser):
    """Light traffic configuration for basic testing."""
    weight = 5
    wait_time = between(5, 12)


class HeavyTraffic(CustomerUser):
    """Heavy traffic configuration for stress testing."""
    weight = 15
    wait_time = between(0.5, 3)


if __name__ == "__main__":
    print("🔥 Locust file for E-commerce Promotion Buy Tracker API")
    print("=" * 60)
    print("📊 User Classes:")
    print("   👥 CustomerUser (weight: 20) - Customers making purchases")
    print("   🔧 AdminUser (weight: 1)    - Admins monitoring campaigns") 
    print("   ⚡ BurstCustomer (weight: 2) - Flash sale burst traffic")
    print("   🟢 LightTraffic (weight: 5) - Light load configuration")
    print("   🔴 HeavyTraffic (weight: 15)- Heavy load configuration")
    print()
    print("🎯 Traffic Distribution:")
    print("   ~87% Customers (20/23 weight ratio)")
    print("   ~4%  Admins (1/23 weight ratio)")  
    print("   ~9%  Burst Traffic (2/23 weight ratio)")
    print()
    print("🚀 Usage Examples:")
    print("   # Default mixed traffic")
    print("   locust --host=http://localhost:8080")
    print()
    print("   # 50 users, 5 spawn rate") 
    print("   locust --host=http://localhost:8080 --users 50 --spawn-rate 5")
    print()
    print("   # Only customer traffic")
    print("   locust -f locustfile.py --host=http://localhost:8080 CustomerUser")
    print()
    print("   # Only admin monitoring")
    print("   locust -f locustfile.py --host=http://localhost:8080 AdminUser")
    print()
    print("   # Headless stress test")
    print("   locust --host=http://localhost:8080 --users 100 --spawn-rate 10 --run-time 300s --headless")