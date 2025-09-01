#!/usr/bin/env python3
"""
Simple load testing script using requests library (synchronous)
This provides a basic load test without additional dependencies
"""

import requests
import json
import time
import random
import threading
import statistics
from datetime import datetime
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse


class SimpleLoadTester:
    """
    Simple synchronous load tester for the Amazing API endpoint
    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()

        # Test data
        self.positive_messages = [
            "You are amazing!",
            "You are wonderful!",
            "You're fantastic!",
            "You are incredible!",
            "You are awesome!",
            "You rock!",
            "You're the best!",
            "You are brilliant!",
            "You are outstanding!",
            "You are magnificent!",
            # Spanish
            "Eres increíble!",
            "Eres maravilloso!",
            "Eres fantástico!",
            # French
            "Tu es fantastique!",
            "Vous êtes incroyable!",
            "Tu es merveilleux!",
            # German
            "Du bist großartig!",
            "Sie sind wunderbar!",
            # Italian
            "Sei fantastico!",
            "Sei meraviglioso!",
            # Portuguese
            "Você é incrível!",
            "Você é maravilhoso!",
            # Dutch
            "Je bent geweldig!",
            # Japanese (simple)
            "あなたは素晴らしい!",
            # Chinese (simple)
            "你很棒!",
            # Hebrew
            "אתה מדהים!",
            # Arabic
            "أنت رائع!",
        ]

        self.negative_messages = [
            "Hello world",
            "What time is it?",
            "I like pizza",
            "Random text",
            "poooppuupu",
            "Testing 123",
            "Weather is nice today",
            "I need to buy groceries",
            "This is just a test message",
            "Programming is fun"
        ]

        # Thread-safe metrics
        self.lock = threading.Lock()
        self.results = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'response_times': [],
            'status_codes': {},
            'errors': [],
            'start_time': None,
            'end_time': None
        }

    def make_request(self, message: str, expected_success: bool = True, user_id: int = 0) -> Dict[str, Any]:
        """
        Make a single request to POST /api/amazing

        Args:
            message: The message to send
            expected_success: Whether we expect this request to succeed
            user_id: ID of the user making the request

        Returns:
            Dict with request results
        """
        start_time = time.time()

        payload = {"text": message}
        headers = {'Content-Type': 'application/json'}

        try:
            response = self.session.post(
                f"{self.base_url}/api/amazing",
                json=payload,
                headers=headers,
                timeout=30
            )

            response_time = time.time() - start_time
            status_code = response.status_code

            try:
                response_data = response.json()
            except:
                response_data = None

            # Thread-safe metrics update
            with self.lock:
                self.results['total_requests'] += 1
                self.results['response_times'].append(response_time)

                if status_code not in self.results['status_codes']:
                    self.results['status_codes'][status_code] = 0
                self.results['status_codes'][status_code] += 1

            # Determine if request was successful based on expectation
            success = False
            error_msg = None

            if expected_success:
                if status_code == 200:
                    success = True
                elif status_code == 400:
                    # Check if it's a duplicate/repetition (acceptable)
                    if response_data and 'detail' in response_data:
                        detail = response_data['detail']
                        if "already have the sentence" in detail or "Adding a repetition" in detail:
                            success = True
                        else:
                            error_msg = f"Unexpected 400: {detail}"
                    else:
                        error_msg = "Unexpected 400 without detail"
                else:
                    error_msg = f"Unexpected status code: {status_code}"
            else:
                # For negative messages, we expect 400
                if status_code == 400:
                    success = True
                else:
                    error_msg = f"Expected 400 but got: {status_code}"

            with self.lock:
                if success:
                    self.results['successful_requests'] += 1
                else:
                    self.results['failed_requests'] += 1
                    if error_msg:
                        self.results['errors'].append({
                            'user_id': user_id,
                            'message': message[:50],
                            'error': error_msg,
                            'status_code': status_code,
                            'response_time': response_time
                        })

            return {
                'user_id': user_id,
                'message': message[:50],
                'status_code': status_code,
                'response_time': response_time,
                'success': success,
                'error': error_msg,
                'response_data': response_data
            }

        except Exception as e:
            response_time = time.time() - start_time

            with self.lock:
                self.results['total_requests'] += 1
                self.results['failed_requests'] += 1
                self.results['response_times'].append(response_time)

            error_msg = f"Request exception: {str(e)}"
            with self.lock:
                self.results['errors'].append({
                    'user_id': user_id,
                    'message': message[:50],
                    'error': error_msg,
                    'status_code': None,
                    'response_time': response_time
                })

            return {
                'user_id': user_id,
                'message': message[:50],
                'status_code': None,
                'response_time': response_time,
                'success': False,
                'error': error_msg,
                'response_data': None
            }

    def user_session(self, user_id: int, requests_per_user: int) -> List[Dict[str, Any]]:
        """
        Simulate a single user's session

        Args:
            user_id: Unique identifier for the user
            requests_per_user: Number of requests this user should make

        Returns:
            List of request results
        """
        results = []
        print(
            f"👤 User {user_id} starting session with {requests_per_user} requests")

        for request_num in range(requests_per_user):
            # Randomly choose message type
            if random.random() < 0.8:  # 80% positive messages
                message = random.choice(self.positive_messages)
                expected_success = True
            else:  # 20% negative messages
                message = random.choice(self.negative_messages)
                expected_success = False

            result = self.make_request(message, expected_success, user_id)
            results.append(result)

            if result['success']:
                status = "✅"
            else:
                status = "❌"

            print(f"{status} User {user_id} Request {request_num + 1}: "
                  f"{result['message']} -> {result['status_code']} "
                  f"({result['response_time']:.3f}s)")

            # Small delay between requests
            time.sleep(random.uniform(0.1, 0.5))

        print(f"👤 User {user_id} completed session")
        return results

    def run_load_test(
        self,
        concurrent_users: int = 10,
        requests_per_user: int = 10
    ):
        """
        Run the load test using ThreadPoolExecutor

        Args:
            concurrent_users: Number of concurrent users to simulate
            requests_per_user: Number of requests each user should make
        """

        print(f"🚀 Starting load test with {concurrent_users} concurrent users")
        print(f"📊 Each user will make {requests_per_user} requests")
        print(f"🎯 Target endpoint: {self.base_url}/api/amazing")
        print("-" * 60)

        self.results['start_time'] = datetime.now()

        # Use ThreadPoolExecutor for concurrent execution
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            # Submit all user sessions
            futures = [
                executor.submit(self.user_session, user_id, requests_per_user)
                for user_id in range(concurrent_users)
            ]

            # Wait for all to complete
            for future in as_completed(futures):
                try:
                    future.result()  # This will raise any exceptions that occurred
                except Exception as e:
                    print(f"❌ User session failed: {e}")

        self.results['end_time'] = datetime.now()

    def health_check(self) -> bool:
        """
        Perform a health check on the API

        Returns:
            True if API is healthy, False otherwise
        """
        try:
            print("🔍 Performing health check...")
            response = self.session.get(f"{self.base_url}/health", timeout=10)

            if response.status_code == 200:
                data = response.json()
                print(
                    f"✅ API is healthy - Status: {data.get('status', 'unknown')}")
                print(f"📊 Items count: {data.get('items_count', 'unknown')}")
                return True
            else:
                print(
                    f"❌ Health check failed - Status: {response.status_code}")
                return False

        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False

    def print_results(self):
        """Print detailed test results"""
        print("\n" + "=" * 60)
        print("📈 LOAD TEST RESULTS")
        print("=" * 60)

        # Basic metrics
        duration = self.results['end_time'] - self.results['start_time']
        print(f"⏱️  Test Duration: {duration}")
        print(f"📊 Total Requests: {self.results['total_requests']}")
        print(f"✅ Successful: {self.results['successful_requests']}")
        print(f"❌ Failed: {self.results['failed_requests']}")

        if self.results['total_requests'] > 0:
            success_rate = (
                self.results['successful_requests'] / self.results['total_requests']) * 100
            print(f"📈 Success Rate: {success_rate:.2f}%")

        # Response time statistics
        if self.results['response_times']:
            response_times = self.results['response_times']
            print(f"\n⏱️  Response Time Statistics:")
            print(f"   • Mean: {statistics.mean(response_times):.3f}s")
            print(f"   • Median: {statistics.median(response_times):.3f}s")
            print(f"   • Min: {min(response_times):.3f}s")
            print(f"   • Max: {max(response_times):.3f}s")

            if len(response_times) > 1:
                print(f"   • Std Dev: {statistics.stdev(response_times):.3f}s")

            # Percentiles
            sorted_times = sorted(response_times)
            p95_index = int(0.95 * len(sorted_times))
            p99_index = int(0.99 * len(sorted_times))
            print(f"   • 95th percentile: {sorted_times[p95_index]:.3f}s")
            print(f"   • 99th percentile: {sorted_times[p99_index]:.3f}s")

        # Status codes
        if self.results['status_codes']:
            print(f"\n📋 Status Code Distribution:")
            for status_code, count in sorted(self.results['status_codes'].items()):
                percentage = (count / self.results['total_requests']) * 100
                print(f"   • {status_code}: {count} ({percentage:.1f}%)")

        # Errors summary
        if self.results['errors']:
            print(f"\n🚨 Errors ({len(self.results['errors'])}):")
            error_summary = {}
            for error in self.results['errors']:
                error_type = error['error']
                if error_type not in error_summary:
                    error_summary[error_type] = 0
                error_summary[error_type] += 1

            for error_type, count in error_summary.items():
                print(f"   • {error_type}: {count}")

        # Throughput
        duration_seconds = duration.total_seconds()
        if duration_seconds > 0:
            rps = self.results['total_requests'] / duration_seconds
            print(f"\n🚀 Throughput: {rps:.2f} requests/second")

        print("=" * 60)


def main():
    """Main function to run the load test"""
    parser = argparse.ArgumentParser(
        description="Simple Load test for Amazing API")
    parser.add_argument("--url", default="http://localhost:8000",
                        help="Base URL for the API (default: http://localhost:8000)")
    parser.add_argument("--users", type=int, default=5,
                        help="Number of concurrent users (default: 5)")
    parser.add_argument("--requests", type=int, default=10,
                        help="Number of requests per user (default: 10)")
    parser.add_argument("--health", action="store_true",
                        help="Perform health check before running tests")

    args = parser.parse_args()

    tester = SimpleLoadTester(args.url)

    if args.health:
        if not tester.health_check():
            print("❌ Health check failed. Exiting.")
            return 1
        print()

    tester.run_load_test(
        concurrent_users=args.users,
        requests_per_user=args.requests
    )
    tester.print_results()

    return 0


if __name__ == "__main__":
    exit(main())
