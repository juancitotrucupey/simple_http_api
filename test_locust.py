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
        # Test buy endpoint
        test_purchase = {
            "user_id": 99999,
            "promotion_id": 1,
            "product_id": 999,
            "product_quantity": 3
        }
        response = requests.post(f"{host}/buy", json=test_purchase, timeout=5)
        if response.status_code == 200:
            print("✅ Buy endpoint working")
            data = response.json()
            print(f"   Purchase logged successfully, Total buys: {data.get('buy_count', 'unknown')}")
        else:
            print(f"❌ Buy endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Buy endpoint error: {e}")
        return False
    
    try:
        # Test stats endpoint
        response = requests.get(f"{host}/stats", timeout=5)
        if response.status_code == 200:
            print("✅ Stats endpoint working")
            data = response.json()
            print(f"   Total buys: {data.get('total_buys', 'unknown')}")
            print(f"   Recent buys (1h): {data.get('n_recent_buys', 'unknown')}")
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
        
        # Check if our main user classes exist
        user_classes_found = []
        
        if hasattr(locustfile, 'CustomerUser'):
            print("✅ CustomerUser class found")
            user_classes_found.append('CustomerUser')
        else:
            print("❌ CustomerUser class not found")
            
        if hasattr(locustfile, 'AdminUser'):
            print("✅ AdminUser class found")
            user_classes_found.append('AdminUser')
        else:
            print("❌ AdminUser class not found")
            
        if hasattr(locustfile, 'BurstCustomer'):
            print("✅ BurstCustomer class found")
            user_classes_found.append('BurstCustomer')
        else:
            print("⚠️  BurstCustomer class not found (optional)")
            
        if len(user_classes_found) < 2:
            print("❌ Critical user classes missing from locustfile.py")
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
    
    print("\n3. 📊 Headless mode with mixed traffic:")
    print("   locust --host=http://localhost:8080 --users 20 --spawn-rate 5 --run-time 120s --headless")
    
    print("\n4. 👥 Customer traffic only:")
    print("   locust -f locustfile.py --host=http://localhost:8080 CustomerUser --users 15 --spawn-rate 3 --run-time 180s --headless")
    
    print("\n5. 🔧 Admin monitoring only:")
    print("   locust -f locustfile.py --host=http://localhost:8080 AdminUser --users 2 --spawn-rate 1 --run-time 120s --headless")
    
    print("\n6. 🔥 Heavy load test (realistic e-commerce traffic):")
    print("   locust --host=http://localhost:8080 --users 100 --spawn-rate 10 --run-time 300s --headless")
    
    print("\n7. ⚡ Flash sale simulation:")
    print("   locust -f locustfile.py --host=http://localhost:8080 BurstCustomer --users 50 --spawn-rate 25 --run-time 60s --headless")
    
    print("\n8. 🧪 Docker testing:")
    print("   # First start the API in Docker:")
    print("   docker compose up -d")
    print("   # Then run Locust:")
    print("   locust --host=http://localhost:8080 --users 50 --spawn-rate 5")


def main():
    """Main test function."""
    print("🔥 E-commerce Promotion Buy Tracker API - Locust Test Validation")
    print("=" * 60)
    
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
    
    print("\n🎯 Performance Testing User Types:")
    print("• 👥 CustomerUser (weight: 20): Customers making purchases - high volume")
    print("• 🔧 AdminUser (weight: 1): Admins monitoring campaigns - low volume")
    print("• ⚡ BurstCustomer (weight: 2): Flash sale burst traffic")
    print("• 🟢 LightTraffic (weight: 5): Light load configuration")
    print("• 🔴 HeavyTraffic (weight: 15): Heavy load configuration")
    
    print("\n📊 Traffic Distribution (Default Mixed):")
    print("• ~87% Customer purchases (/buy endpoint)")
    print("• ~4% Admin monitoring (/stats, /health endpoints)")
    print("• ~9% Burst traffic (flash sales)")
    
    print("\n📈 Key Metrics to Monitor:")
    print("• Response times for /buy, /stats, and /health endpoints")
    print("• Request success rate (should be close to 100%)")
    print("• Purchase throughput (buys per second)")
    print("• Campaign analytics accuracy")
    print("• Error rate and types")
    print("• Timestamp extraction from headers")
    
    print("\n🛒 E-commerce Scenarios to Test:")
    print("• Normal shopping traffic: 20-50 concurrent customers")
    print("• Flash sale events: 100-500 concurrent burst customers")
    print("• Admin monitoring: 1-3 concurrent admin users")
    print("• Peak holiday traffic: 200+ concurrent mixed users")
    print("• Campaign performance tracking: Various timeframes")
    
    print("\n✅ All tests passed! Ready for e-commerce promotion load testing.")
    print("\n🚀 Start load testing:")
    print("   locust --host=http://localhost:8080")


if __name__ == "__main__":
    main() 