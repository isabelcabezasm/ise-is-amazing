#!/usr/bin/env python3
"""
Load testing script for POST /api/amazing endpoint using Locust
This script simulates multiple users making requests to the amazing API endpoint
"""

from locust import HttpUser, task, between
import json
import random
import time
from typing import List


class AmazingAPIUser(HttpUser):
    """
    User behavior for testing the /api/amazing POST endpoint
    """

    # Wait between 1-3 seconds between tasks
    wait_time = between(1, 3)

    # Test data - various positive messages in different languages
    positive_messages: List[str] = [
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

    negative_messages: List[str] = [
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

    def on_start(self):
        """Called when a user starts"""
        print(
            f"User {self.user_id if hasattr(self, 'user_id') else 'unknown'} starting load test")

    @task(8)  # 80% of requests will be positive messages (should succeed)
    def post_positive_amazing_message(self):
        """Test POST /api/amazing with positive messages that should succeed"""
        message = random.choice(self.positive_messages)

        payload = {
            "text": message
        }

        headers = {
            "Content-Type": "application/json"
        }

        with self.client.post(
            "/api/amazing",
            json=payload,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                # Success - new item created
                response.success()
                try:
                    data = response.json()
                    print(
                        f"✅ Created: {data.get('item', {}).get('text', 'N/A')[:50]}...")
                except:
                    pass
            elif response.status_code == 400:
                # Could be duplicate or language already exists
                try:
                    error_detail = response.json().get('detail', '')
                    if "already have the sentence" in error_detail or "Adding a repetition" in error_detail:
                        response.success()  # This is expected behavior
                        print(f"ℹ️  Duplicate handled: {message[:30]}...")
                    else:
                        response.failure(
                            f"Unexpected 400 error: {error_detail}")
                except:
                    response.failure(
                        f"400 error with message: {message[:30]}...")
            else:
                response.failure(
                    f"Unexpected status code: {response.status_code}")

    @task(1)  # 10% of requests will be negative messages (should fail)
    def post_negative_amazing_message(self):
        """Test POST /api/amazing with negative messages that should fail semantic validation"""
        message = random.choice(self.negative_messages)

        payload = {
            "text": message
        }

        headers = {
            "Content-Type": "application/json"
        }

        with self.client.post(
            "/api/amazing",
            json=payload,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code == 400:
                # Expected - should fail semantic validation
                response.success()
                print(f"✅ Correctly rejected: {message[:30]}...")
            elif response.status_code == 200:
                response.failure(
                    f"Unexpected success for negative message: {message[:30]}...")
            else:
                response.failure(
                    f"Unexpected status code {response.status_code} for: {message[:30]}...")

    @task(1)  # 10% of requests will test edge cases
    def post_edge_cases(self):
        """Test edge cases for POST /api/amazing"""
        edge_cases = [
            "",  # Empty string
            "   ",  # Only whitespace
            "a" * 1000,  # Very long string
            "You're amazing!" * 50,  # Repeated positive message
            "🎉 You are amazing! 🚀",  # With emojis
            "YOU ARE AMAZING!!!",  # All caps
            "you are amazing",  # Lowercase
        ]

        message = random.choice(edge_cases)

        payload = {
            "text": message
        }

        headers = {
            "Content-Type": "application/json"
        }

        with self.client.post(
            "/api/amazing",
            json=payload,
            headers=headers,
            catch_response=True
        ) as response:
            if response.status_code in [200, 400]:
                # Both are acceptable for edge cases
                response.success()
                if response.status_code == 200:
                    print(f"✅ Edge case accepted: {message[:30]}...")
                else:
                    print(f"ℹ️  Edge case rejected: {message[:30]}...")
            else:
                response.failure(
                    f"Unexpected status code {response.status_code} for edge case: {message[:30]}...")

    @task(1)
    def get_amazing_items(self):
        """Test GET /api/amazing to retrieve all items"""
        with self.client.get("/api/amazing", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
                try:
                    data = response.json()
                    items_count = len(data.get('items', []))
                    print(f"📋 Retrieved {items_count} items")
                except:
                    pass
            else:
                response.failure(
                    f"GET failed with status: {response.status_code}")

    def on_stop(self):
        """Called when a user stops"""
        print(
            f"User {self.user_id if hasattr(self, 'user_id') else 'unknown'} finished load test")


if __name__ == "__main__":
    # This allows running the script directly for testing
    import os
    os.system("locust -f load_test_locust.py --host=https://youareamazing-api.ambitiousmushroom-0229ef63.westus2.azurecontainerapps.io/")
