#!/usr/bin/env python3
"""
Quick demo/test of the load testing setup
This script validates that the load testing tools work correctly
"""

import subprocess
import sys
import time
import requests
from pathlib import Path


def check_api_health(url: str = "http://localhost:8000") -> bool:
    """Check if the API is running and healthy"""
    try:
        response = requests.get(f"{url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(
                f"✅ API is healthy - Status: {data.get('status', 'unknown')}")
            return True
        else:
            print(
                f"❌ API health check failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API health check error: {e}")
        return False


def run_quick_load_test():
    """Run a quick load test with minimal load"""
    print("🚀 Running quick load test (3 users, 5 requests each)...")

    try:
        result = subprocess.run([
            sys.executable, "load_test_simple.py",
            "--users", "3",
            "--requests", "5",
            "--health"
        ], capture_output=True, text=True, timeout=60)

        print("📊 Load test output:")
        print(result.stdout)

        if result.stderr:
            print("⚠️  Warnings/Errors:")
            print(result.stderr)

        if result.returncode == 0:
            print("✅ Load test completed successfully!")
            return True
        else:
            print(f"❌ Load test failed with return code: {result.returncode}")
            return False

    except subprocess.TimeoutExpired:
        print("⏰ Load test timed out")
        return False
    except Exception as e:
        print(f"❌ Error running load test: {e}")
        return False


def test_individual_request():
    """Test a single request to the API"""
    print("🔍 Testing individual request...")

    try:
        # Test positive message
        payload = {"text": "You are absolutely amazing!"}
        response = requests.post(
            "http://localhost:8000/api/amazing",
            json=payload,
            timeout=10
        )

        print(f"📤 Sent: {payload['text']}")
        print(f"📥 Response: {response.status_code}")

        if response.status_code in [200, 400]:  # 400 might be duplicate
            try:
                data = response.json()
                if response.status_code == 200:
                    print(
                        f"✅ Success: {data.get('item', {}).get('language', 'N/A')} message added")
                else:
                    print(f"ℹ️  Response: {data.get('detail', 'N/A')}")
            except:
                pass
            return True
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error with individual request: {e}")
        return False


def main():
    """Main demo function"""
    print("🔥 Amazing API Load Testing Demo")
    print("=" * 40)

    # Change to load-tests directory
    script_dir = Path(__file__).parent
    import os
    os.chdir(script_dir)

    # Step 1: Health check
    print("\n1️⃣ Checking API health...")
    if not check_api_health():
        print("\n❌ API is not running. Please start it first:")
        print("   cd api-python")
        print("   uvicorn main:app --host 0.0.0.0 --port 8000")
        return 1

    # Step 2: Test individual request
    print("\n2️⃣ Testing individual request...")
    if not test_individual_request():
        print("❌ Individual request test failed")
        return 1

    # Step 3: Run quick load test
    print("\n3️⃣ Running quick load test...")
    if not run_quick_load_test():
        print("❌ Load test failed")
        return 1

    print("\n🎉 All tests passed! Load testing setup is working correctly.")
    print("\n📚 Next steps:")
    print("   • Run full load test: ./run_load_test.sh")
    print("   • Try different parameters: ./run_load_test.sh -c 20 -r 50")
    print("   • Use async test: ./run_load_test.sh -t async")
    print("   • Start Locust GUI: ./run_load_test.sh -t locust")

    return 0


if __name__ == "__main__":
    exit(main())
