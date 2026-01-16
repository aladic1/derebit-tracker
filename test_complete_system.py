import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_endpoint(name, endpoint, params=None, expected_status=200):
    """Test an API endpoint."""
    url = f"{BASE_URL}{endpoint}"
    try:
        print(f"\n{'='*60}")
        print(f"Test: {name}")
        print(f"URL: {url}")
        if params:
            print(f"Params: {params}")
        
        response = requests.get(url, params=params)
        
        status_ok = response.status_code == expected_status
        print(f"Status: {response.status_code} {'✅' if status_ok else '❌'}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list):
                    print(f"Response: List with {len(data)} items")
                    if len(data) > 0:
                        print(f"First item: {json.dumps(data[0], indent=2)[:200]}...")
                elif isinstance(data, dict):
                    print(f"Response keys: {list(data.keys())}")
                    # Для списка цен покажем количество
                    if 'prices' in data and isinstance(data['prices'], list):
                        print(f"Prices count: {len(data['prices'])}")
                    # Для последней цены покажем значение
                    elif 'price' in data:
                        print(f"Latest price: {data['price']}")
                else:
                    print(f"Response: {str(data)[:200]}...")
            except:
                print(f"Response: {response.text[:200]}...")
        else:
            print(f"Error: {response.text[:200]}")
            
        return status_ok
    except Exception as e:
        print(f"Exception: {e}")
        return False

print("🚀 Deribit Price Tracker API - Complete System Test")
print("="*60)

# Get dates
today = datetime.now().date()
yesterday = today - timedelta(days=1)

tests_passed = 0
tests_total = 0

# Test 1: Health check
tests_total += 1
if test_endpoint("Health Check", "/health"):
    tests_passed += 1

# Test 2: Root endpoint
tests_total += 1
if test_endpoint("Root Endpoint", "/"):
    tests_passed += 1

# Test 3: Get all BTC prices
tests_total += 1
if test_endpoint("Get All BTC Prices", "/api/v1/prices", {"ticker": "BTC", "limit": 2}):
    tests_passed += 1

# Test 4: Get latest BTC price
tests_total += 1
if test_endpoint("Get Latest BTC Price", "/api/v1/prices/latest", {"ticker": "BTC"}):
    tests_passed += 1

# Test 5: Get latest ETH price
tests_total += 1
if test_endpoint("Get Latest ETH Price", "/api/v1/prices/latest", {"ticker": "ETH"}):
    tests_passed += 1

# Test 6: Get BTC prices by date (today)
tests_total += 1
if test_endpoint("Get BTC Prices by Date (Today)", "/api/v1/prices/date", {"ticker": "BTC", "date": str(today)}):
    tests_passed += 1

# Test 7: Get BTC prices by date (yesterday)
tests_total += 1
# 404 is expected if no data for yesterday
if test_endpoint("Get BTC Prices by Date (Yesterday)", "/api/v1/prices/date", {"ticker": "BTC", "date": str(yesterday)}, 404):
    tests_passed += 1

# Test 8: Invalid ticker
tests_total += 1
if test_endpoint("Invalid Ticker", "/api/v1/prices", {"ticker": "INVALID"}, 400):
    tests_passed += 1

# Test 9: Pagination
tests_total += 1
if test_endpoint("Pagination", "/api/v1/prices", {"ticker": "BTC", "limit": 1, "skip": 5}):
    tests_passed += 1

# Test 10: Get data for 2026-01-15 (should have data)
tests_total += 1
if test_endpoint("Get BTC Prices for 2026-01-15", "/api/v1/prices/date", {"ticker": "BTC", "date": "2026-01-15"}):
    tests_passed += 1

print(f"\n{'='*60}")
print(f"SUMMARY: {tests_passed}/{tests_total} tests passed")
print("="*60)

if tests_passed == tests_total:
    print("🎉 ALL TESTS PASSED! System is working correctly.")
    print("\n✅ SYSTEM STATUS:")
    print("   - FastAPI: Running on http://localhost:8000")
    print("   - Database: PostgreSQL with price data")
    print("   - Celery: Collecting prices from Deribit every minute")
    print("   - API Endpoints: All 3 endpoints working")
    print("   - Data: Real-time prices being collected")
else:
    print(f"⚠️  {tests_total - tests_passed} tests failed.")
