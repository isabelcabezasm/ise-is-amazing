#!/usr/bin/env python3
"""
Async load testing script for POST /api/amazing endpoint using aiohttp
This script provides more control over concurrent requests and detailed metrics
"""

import asyncio
import aiohttp
import json
import random
import time
import statistics
from datetime import datetime
from typing import List, Dict, Any
import argparse


class AmazingAPILoadTester:
    """
    Async load tester for the Amazing API endpoint
    """

    def __init__(self, base_url: str = "https://youareamazing-api.ambitiousmushroom-0229ef63.westus2.azurecontainerapps.io/"):
        self.base_url = base_url
        self.session = None

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

        # Metrics
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

    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(
            limit=100,  # Maximum number of connections
            ttl_dns_cache=300,
            ttl_resolver_cache=300,
        )
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'Content-Type': 'application/json'}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def make_request(self, message: str, expected_success: bool = True) -> Dict[str, Any]:
        """
        Make a single request to POST /api/amazing

        Args:
            message: The message to send
            expected_success: Whether we expect this request to succeed

        Returns:
            Dict with request results
        """
        start_time = time.time()

        payload = {"text": message}

        try:
            async with self.session.post(
                f"{self.base_url}/api/amazing",
                json=payload
            ) as response:
                response_time = time.time() - start_time
                status_code = response.status

                try:
                    response_data = await response.json()
                except:
                    response_data = None

                # Update metrics
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

                if success:
                    self.results['successful_requests'] += 1
                else:
                    self.results['failed_requests'] += 1
                    if error_msg:
                        self.results['errors'].append({
                            'message': message[:50],
                            'error': error_msg,
                            'status_code': status_code,
                            'response_time': response_time
                        })

                return {
                    'message': message[:50],
                    'status_code': status_code,
                    'response_time': response_time,
                    'success': success,
                    'error': error_msg,
                    'response_data': response_data
                }

        except Exception as e:
            response_time = time.time() - start_time
            self.results['total_requests'] += 1
            self.results['failed_requests'] += 1
            self.results['response_times'].append(response_time)

            error_msg = f"Request exception: {str(e)}"
            self.results['errors'].append({
                'message': message[:50],
                'error': error_msg,
                'status_code': None,
                'response_time': response_time
            })

            return {
                'message': message[:50],
                'status_code': None,
                'response_time': response_time,
                'success': False,
                'error': error_msg,
                'response_data': None
            }

    async def run_load_test(
        self,
        concurrent_users: int = 10,
        requests_per_user: int = 10,
        test_duration: int = None
    ):
        """
        Run the load test

        Args:
            concurrent_users: Number of concurrent users to simulate
            requests_per_user: Number of requests each user should make
            test_duration: Maximum test duration in seconds (optional)
        """

        print(f"🚀 Starting load test with {concurrent_users} concurrent users")
        print(f"📊 Each user will make {requests_per_user} requests")
        if test_duration:
            print(f"⏰ Maximum test duration: {test_duration} seconds")
        print(f"🎯 Target endpoint: {self.base_url}/api/amazing")
        print("-" * 60)

        self.results['start_time'] = datetime.now()

        async def user_session(user_id: int):
            """Simulate a single user's session"""
            print(f"👤 User {user_id} starting session")

            for request_num in range(requests_per_user):
                # Randomly choose message type
                if random.random() < 0.8:  # 80% positive messages
                    message = random.choice(self.positive_messages)
                    expected_success = True
                else:  # 20% negative messages
                    message = random.choice(self.negative_messages)
                    expected_success = False

                result = await self.make_request(message, expected_success)

                if result['success']:
                    status = "✅"
                else:
                    status = "❌"

                print(f"{status} User {user_id} Request {request_num + 1}: "
                      f"{result['message']} -> {result['status_code']} "
                      f"({result['response_time']:.3f}s)")

                # Small delay between requests
                await asyncio.sleep(random.uniform(0.1, 0.5))

            print(f"👤 User {user_id} completed session")

        # Create tasks for all concurrent users
        tasks = [user_session(i) for i in range(concurrent_users)]

        try:
            if test_duration:
                await asyncio.wait_for(
                    asyncio.gather(*tasks),
                    timeout=test_duration
                )
            else:
                await asyncio.gather(*tasks)
        except asyncio.TimeoutError:
            print(f"⏰ Test stopped due to time limit ({test_duration}s)")

        self.results['end_time'] = datetime.now()

    def print_results(self):
        """Print detailed test results"""
        print("\n" + "=" * 60)
        print("📈 LOAD TEST RESULTS")
        print("=" * 60)

        # Basic metrics
        print(
            f"⏱️  Test Duration: {self.results['end_time'] - self.results['start_time']}")
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

        # Errors
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
        duration = (self.results['end_time'] -
                    self.results['start_time']).total_seconds()
        if duration > 0:
            rps = self.results['total_requests'] / duration
            print(f"\n🚀 Throughput: {rps:.2f} requests/second")

        print("=" * 60)


async def main():
    """Main function to run the load test"""
    parser = argparse.ArgumentParser(description="Load test for Amazing API")
    parser.add_argument("--url", default="http://localhost:8000",
                        help="Base URL for the API (default: http://localhost:8000)")
    parser.add_argument("--users", type=int, default=10,
                        help="Number of concurrent users (default: 10)")
    parser.add_argument("--requests", type=int, default=10,
                        help="Number of requests per user (default: 10)")
    parser.add_argument("--duration", type=int,
                        help="Maximum test duration in seconds")

    args = parser.parse_args()

    async with AmazingAPILoadTester(args.url) as tester:
        await tester.run_load_test(
            concurrent_users=args.users,
            requests_per_user=args.requests,
            test_duration=args.duration
        )
        tester.print_results()


if __name__ == "__main__":
    asyncio.run(main())
