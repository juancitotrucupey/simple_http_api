#!/usr/bin/env python3
"""
Test script to validate the Locust file setup.

This script helps you verify that:
1. Locust is properly installed
2. The locustfile.py is syntactically correct
3. The API endpoints are accessible
4. Basic load testing can be performed

Usage:
    python test_locust.py
"""

import requests
import sys
import time
import json


def test_api_connectivity(host="http://localhost:8080"):
    """Test basic API connectivity before running Locust."""
    print(f"🔍 Testing API connectivity to {host}")
    
    try:
        # Test health endpoint
        response = requests.get(f"{host}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        print("💡 Make sure the API is running with: make run")
        return False
    
    try:
        # Test visit endpoint
        test_visit = {
            "user_id": "test_user",
            "page_url": "https://example.com/test",
            "user_agent": "TestAgent/1.0"
        }
        response = requests.post(f"{host}/visit", json=test_visit, timeout=5)
        if response.status_code == 200:
            print("✅ Visit endpoint working")
        else:
            print(f"❌ Visit endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Visit endpoint error: {e}")
        return False
    
    try:
        # Test stats endpoint
        response = requests.get(f"{host}/stats", timeout=5)
        if response.status_code == 200:
            print("✅ Stats endpoint working")
            data = response.json()
            print(f"   Total visits: {data.get('total_visits', 'unknown')}")
            print(f"   Server status: {data.get('server_status', 'unknown')}")
        else:
            print(f"❌ Stats endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Stats endpoint error: {e}")
        return False
    
    print("🎉 All API endpoints are working correctly!")
    return True


def test_locust_import():
    """Test if Locust is installed and locustfile can be imported."""
    print("\n🔍 Testing Locust installation and locustfile")
    
    try:
        import locust
        print(f"✅ Locust installed (version: {locust.__version__})")
    except ImportError:
        print("❌ Locust not installed. Install with:")
        print("   pip install -r requirements.txt")
        print("   OR: pip install locust")
        return False
    
    try:
        import locustfile
        print("✅ locustfile.py can be imported successfully")
        
        # Check if our main user class exists
        if hasattr(locustfile, 'WebVisitUser'):
            print("✅ WebVisitUser class found")
        else:
            print("❌ WebVisitUser class not found")
            return False
            
    except ImportError as e:
        print(f"❌ Cannot import locustfile.py: {e}")
        return False
    except Exception as e:
        print(f"❌ Error in locustfile.py: {e}")
        return False
    
    return True


def show_usage_examples():
    """Show practical usage examples for the Locust file."""
    print("\n📋 Locust Usage Examples:")
    print("\n1. 🌐 Basic web UI (recommended for beginners):")
    print("   locust --host=http://localhost:8080")
    print("   Then open: http://localhost:8089")
    
    print("\n2. 🚀 Quick load test (10 users, 2 per second):")
    print("   locust --host=http://localhost:8080 --users 10 --spawn-rate 2 --run-time 60s")
    
    print("\n3. 📊 Headless mode with specific user class:")
    print("   locust --host=http://localhost:8080 --users 20 --spawn-rate 5 --run-time 120s --headless TrafficTrackerUser")
    
    print("\n4. 🔥 Heavy load test:")
    print("   locust --host=http://localhost:8080 --users 100 --spawn-rate 10 --run-time 300s --headless")
    
    print("\n5. 👥 Multiple user types:")
    print("   locust --host=http://localhost:8080 --users 30 --spawn-rate 3 --run-time 180s --headless")
    
    print("\n6. 🧪 Docker testing:")
    print("   # First start the API in Docker:")
    print("   docker compose up -d")
    print("   # Then run Locust:")
    print("   locust --host=http://localhost:8080 --users 50 --spawn-rate 5")


def main():
    """Main test function."""
    print("🔥 Traffic Tracker API - Locust Test Validation")
    print("=" * 50)
    
    # Test API connectivity
    if not test_api_connectivity():
        print("\n💡 Start your API first:")
        print("   make run                    # Local development")
        print("   docker compose up          # Docker")
        sys.exit(1)
    
    # Test Locust setup
    if not test_locust_import():
        print("\n💡 Install Locust:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    # Show usage examples
    show_usage_examples()
    
    print("\n🎯 Performance Testing Scenarios:")
    print("• TrafficTrackerUser: Realistic user behavior (5:1 visit:stats ratio)")
    print("• AdminUser: Monitoring-focused behavior")
    print("• BurstUser: Sudden traffic spikes")
    print("• LightLoad: Light testing with longer waits")
    print("• HeavyLoad: Intensive testing with short waits")
    
    print("\n📈 Key Metrics to Monitor:")
    print("• Response times for /visit and /stats endpoints")
    print("• Request success rate (should be close to 100%)")
    print("• API throughput (requests per second)")
    print("• Error rate and types")
    
    print("\n✅ All tests passed! Ready for load testing.")


if __name__ == "__main__":
    main() 